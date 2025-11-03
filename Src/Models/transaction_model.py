from Src.Core.abstract_model import abstact_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.storage_model import storage_model
from Src.Core.validator import validator, argument_exception
from datetime import datetime

"""
Модель транзакции
"""
class transaction_model(abstact_model):
    __date: datetime
    __nomenclature: nomenclature_model
    __storage: storage_model
    __quantity: float
    __unit: str

    # Дата
    @property
    def date(self) -> datetime:
        return self.__date

    @date.setter
    def date(self, value: datetime):
        validator.validate(value, datetime)
        self.__date = value

    # Номенклатура
    @property
    def nomenclature(self) -> nomenclature_model:
        return self.__nomenclature

    @nomenclature.setter
    def nomenclature(self, value: nomenclature_model):
        validator.validate(value, nomenclature_model)
        self.__nomenclature = value

    # Склад
    @property
    def storage(self) -> storage_model:
        return self.__storage

    @storage.setter
    def storage(self, value: storage_model):
        validator.validate(value, storage_model)
        self.__storage = value

    # Количество
    @property
    def quantity(self) -> float:
        return self.__quantity

    @quantity.setter
    def quantity(self, value: float):
        validator.validate(value, (int, float))
        self.__quantity = float(value)

    # Единица измерения
    @property
    def unit(self) -> str:
        return self.__unit

    @unit.setter
    def unit(self, value: str):
        validator.validate(value, str)
        self.__unit = value.strip()

    """
    Фабричный метод
    """
    @staticmethod
    def create(date: datetime, nomenclature: nomenclature_model, storage: storage_model, quantity: float, unit: str):
        item = transaction_model()
        item.date = date
        item.nomenclature = nomenclature
        item.storage = storage
        item.quantity = quantity
        item.unit = unit
        return item
