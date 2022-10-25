from xml.dom.minidom import Element
import pydantic
import typing

class Card(pydantic.BaseModel):
    name: str = pydantic.Field(None, description="Card name")

class CTACard(Card):
    element: str = pydantic.Field(None, description="Card element") 
    value: int = pydantic.Field(None, description="Card value")
    rarity: str = pydantic.Field(None, description="Card rarity")
    grade: str = pydantic.Field(None, description="Card grade")

