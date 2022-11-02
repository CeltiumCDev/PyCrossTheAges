
from http.client import CannotSendHeader
from sys import int_info
import colored
import pydantic
import typing 
import ipdb
import prettytable as pt 
#from prettytable import PrettyTable, ALL


CARD_COLOR_DEFAULT = \
    {
        "name": "white",
        "element": "white", 
        "value": "white",
        "rarity": "white",
        "grade": "white",
        "player_name": "white",
        "owner": "white",
        "value_current": "yellow"
    }
CTA_CARDS_ADVANTAGE = \
                {"air": ["nature", "darkness"], 
                 "nature": ["earth", "water"], 
                 "earth": ["darkness", "fire"], 
                 "light": ["air", "earth"], 
                 "fire": ["nature", 'light'], 
                 "water": ["fire", "air"], 
                 "darkness": ["light", "water"]}

CTA_CARD_SIMPLE_AFFINITYS = \
                {"air": ["fire", "earth"], 
                 "nature": ["light", "darkness"], 
                 "earth": ["air", "water"], 
                 "light": ["water", "nature"], 
                 "fire": ["air", 'darkness'], 
                 "water": ["earth", "light"], 
                 "darkness": ["fire", "nature"]}

CTA_CARD_DOUBLE_AFFINITYS= \
                {"air": ["light", "nature"], 
                 "nature": ["air", "earth"], 
                 "earth": ["nature", "darkness"], 
                 "light": ["air", "fire"], 
                 "fire": ["water", 'light'], 
                 "water": ["darkness", "fire"], 
                 "darkness": ["earth", "water"]}


class CardNotFoundError(Exception):
    pass
class CantPlayError(Exception):
    pass

class Card(pydantic.BaseModel):
    name: str = pydantic.Field(None, description="Card name")

    def to_str_list_fmt(self, 
                     exclude=[],
                     color={}):

        colors_dict = CARD_COLOR_DEFAULT.copy()
        colors_dict.update(color)
        attr_list = self.dict().keys()
        obj_liststr = []
        for attr in attr_list:
            attr_obj = getattr(self, attr)
            if not(attr in exclude) and not(attr_obj is None):
                attr_str = colored.stylize(
                    attr_obj,
                    styles=colored.attr("bold") + colored.fg(colors_dict.get(attr))
                )

                obj_liststr.append(attr_str)
                
        return obj_liststr
        
    def __str__(self):
        return " | ".join(self.to_str_list_fmt())

    def to_str(self, sep="\n", exclude=[], color={}):
        return sep.join(self.to_str_list_fmt(exclude=exclude, color=color))

class CTACard(Card):
    element: str = pydantic.Field(None, description="Card element") 
    value: int = pydantic.Field(None, description="Card value")
    rarity: str = pydantic.Field(None, description="Card rarity")
    grade: str = pydantic.Field(None, description="Card grade")

    def display(self):
        table = pt.PrettyTable()
        table.field_names = ['Name', 'Element', 'Value', 'Rarity', 'Grade']
        table.add_row([self.name, self.element, self.value, self.rarity, self.grade])
        return table

class CTAPlayer(pydantic.BaseModel):
    name: str = pydantic.Field(..., description="Player's name")
    deck: typing.List[CTACard] = pydantic.Field([], description="Player's deck")

    def display(self):
        table = pt.PrettyTable()
        table.field_names = ['Name', 'Element', 'Value', 'Rarity', 'Grade']
        for card in self.deck:
            table.add_row([card.name, card.element, card.value, card.rarity, card.grade])

        return """Player's name: {0}\nPlayer's deck: \n{1}""".format(self.name, table)


class CTACardIngame(CTACard):
    player_name: str = pydantic.Field(None, description="The owner name of the card")
    value_current: int = pydantic.Field(None, description="Card value in game")
    owner: int = pydantic.Field(0, description="The card owner durning the game")
    is_leader: bool = pydantic.Field(False, description="The card is the leader of the game?")

    def __init__(self, **kwrds):
        super().__init__(**kwrds)
        self.value_current = self.value

    def to_str_list_fmt(self, exclude=[], color={}):
        return super().to_str_list_fmt(exclude=exclude + ["owner", "is_leader"], 
            color=color)

    def display(self):
        table = pt.PrettyTable()
        table.field_names = ['Name', 'Element', 'Value', 'Rarity', 'Grade', 'Player', 'In game value']
        table.add_row([self.name, self.element, self.value, self.rarity, self.grade, self.player_name, self.value_in_game])
        return table


class CTABoard(pydantic.BaseModel):
    grid: typing.List[CTACardIngame] = \
        pydantic.Field([None]*16, description="Board gride")

    owners_colors: dict = pydantic.Field({0: "grey", 1: "red", 2: "blue"})

    def get_card(self, x, y):
        return self.grid[x+4*y]

    def set_card(self, card, x, y):
        self.grid[x+4*y] = card

    def display(self):
        table = pt.PrettyTable()
        table.header = False
        table.hrules = pt.ALL
        for i in range(4):
            table.add_row([
                self.get_card(i, j).to_str(
                        exclude=['grade', 'rarity'],
                        color={"name": self.owners_colors[int(self.get_card(i, j).owner)]}) 
                    if not(self.get_card(i, j) is None) else ""
                    for j in range(4)])
            
        return table

class Game(pydantic.BaseModel):
    board: CTABoard = pydantic.Field(CTABoard(), description="Game's board")
    player1: CTAPlayer = pydantic.Field(None, description="Player 1")
    player2: CTAPlayer = pydantic.Field(None, description="Player 2")

    def add_player(self, player):
        new_player = player.copy()
        new_player.deck = [CTACardIngame(**c.dict()) for c in new_player.deck]
        return new_player

    def set_player1(self, player):
        self.player1 = self.add_player(player=player)
        
    def set_player2(self, player):
        self.player2 = self.add_player(player=player)

    def play_card(self, player_num, card_num, x, y):
        if self.check_game_finish == True:
            raise CantPlayError('The game is already finished.')
        player = self.player1 if player_num == 1 else self.player2
        card = player.deck.pop(card_num)
        self.board.set_card(card, x, y)

    def check_game_finish(self):
        return not(any([x is None for x in self.board.grid]))

    def update_affinitys(self, x, y): 
        for x in range(0, 3):
            for y in range(0, 3):
                neighbours = [[x+1, y+1], [x+1, y-1], [x-1, y+1], [x-1, y-1]]
                card = self.board.get_card(x, y)
                for co in neighbours:
                    n_card = self.board.get_card(co[0], co[1])
                    if n_card.element in CTA_CARD_SIMPLE_AFFINITYS[card.element]:
                        card.value_current += 100

    def attack(self, x, y, card):
        cos_to_check = [[x+1, y+1], [x+1, y-1], [x-1, y+1], [x-1, y-1]]

        for co in cos_to_check:
            card = card.copy()
            # Check x+1 y+1 card
            if not(co[0] > 4 or co[1] > 4) and not(self.board.get_card(co[0], co[1]) == None):
                card_attacked = self.board.get_card(co[0], co[1])
            
                # Check ability
                if card_attacked.element in CTA_CARDS_ADVANTAGE[card.element]:
                    card.value_current += 150

                # Launch attack
                if card.value_current > card_attacked.value_current:
                    self.board.set_card(co[0], co[1], card_attacked.owner == card.owner)
                    self.attack(co[0], co[1], self.board.get_card(co[0], co[1]))
            