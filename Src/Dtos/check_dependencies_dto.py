"""
DTO для проверки зависимостей перед удалением объекта
"""
from Src.Core.abstract_dto import abstact_dto
from Src.Models.abstract_reference import abstact_reference
from Src.Core.validator import validator

class check_dependencies_dto(abstact_dto):
    __model: abstact_reference = None

    """
    Модель для проверки зависимостей
    """
    @property
    def model(self) -> abstact_reference:
        return self.__model

    @model.setter
    def model(self, value):
        validator.validate(value, abstact_reference)
        self.__model = value
