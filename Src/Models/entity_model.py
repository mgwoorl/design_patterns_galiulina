"""
Общий класс для наследования моделей сущностей
Содержит стандартное определение: код, наименование
Наследуется от abstract_reference для поддержки наблюдателя
"""
from Src.Core.abstract_reference import abstact_reference
from Src.Core.validator import validator

class entity_model(abstact_reference):
    __name:str = ""

    """
    Наименование модели
    """
    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value:str):
        validator.validate(value, str)
        self.__name = value.strip()

    """
    Фабричный метод создания модели
    """
    @staticmethod
    def create(name:str):
        item = entity_model()
        item.name = name
        return item
