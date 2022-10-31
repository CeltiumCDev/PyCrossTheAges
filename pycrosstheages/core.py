
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

class CardNotFoundError(Exception):
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

    # def to_str_list_fmt(self, exclude=[], color={}):
    
    #     obj_liststr = super().to_str_list_fmt(exclude, color)

    #     colors_dict = CARD_COLOR_DEFAULT.copy()
    #     colors_dict.update(color)
    
    #     attr_list = ['element', 'value', 'rarity', 'grade']
    #     for attr in attr_list:
    #         attr_obj = getattr(self, attr)
    #         if not(attr in exclude) and not(attr_obj is None):
    #             attr_str = colored.stylize(
    #                 attr_obj,
    #                 styles=colored.attr("bold") + colored.fg(colors_dict.get(attr))
    #             )

    #             obj_liststr.append(attr_str)
                
    #     return obj_liststr



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

    def __init__(self, **kwrds):
        super().__init__(**kwrds)
        self.value_current = self.value

    def to_str_list_fmt(self, exclude=[], color={}):
        return super().to_str_list_fmt(exclude=exclude + ["owner"], 
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
        player = self.player1 if player_num == 1 else self.player2
        card = player.deck.pop(card_num)
        self.board.set_card(card, x, y)

