from unicodedata import name
import pydantic
import typing
import ipdb
import prettytable as pt 
#from prettytable import PrettyTable, ALL

class Card(pydantic.BaseModel):
    name: str = pydantic.Field(None, description="Card name")

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
    
class player(pydantic.BaseModel):
    name: str = pydantic.Field(..., description="Player's name")
    deck: typing.List[CTACard] = pydantic.Field([], description="Player's deck")

    def display(self):
        table = pt.PrettyTable()
        table.field_names = ['Name', 'Element', 'Value', 'Rarity', 'Grade']
        for card in self.deck:
            table.add_row([card.name, card.element, card.value, card.rarity, card.grade])

        return """Player's name: {0}\nPlayer's deck: \n{1}""".format(self.name, table)

class board(pydantic.BaseModel):


    board: typing.List[CTACard] = \
        pydantic.Field([None]*16, description="Card grade")

    def get_card(self, x, y):
        return self.board[x+4*y]

    def set_card(self, x, y, card):
        
        self.board[x+4*y] = card

    def display(self):
        table = pt.PrettyTable()
        table.header = False
        table.hrules = pt.ALL
        for i in range(4):
            table.add_row([
                self.get_card(i, j).name if not(self.get_card(i, j) is None) else ""
                for j in range(4)])
        
        return table