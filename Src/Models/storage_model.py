from Src.Core.entity_model import entity_model
from Src.Core.validator import validator

"""
Модель склада для хранения товаров
"""
class storage_model(entity_model):
    __address:str = ""

    @property
    def address(self) -> str:
        return self.__address.strip()
    
    @address.setter
    def address(self, value:str):
        validator.validate(value, str)
        self.__address = value.strip()

    @staticmethod
    def create(name: str, address: str = ""):
        item = storage_model()
        item.name = name
        if address:
            item.address = address
        return item
