"""
DTO для проверки зависимостей
"""
from Src.Core.abstract_dto import abstract_dto
from Src.Core.abstract_model import abstact_model
from Src.Core.validator import validator


class check_dependencies_dto(abstract_dto):
    """
    DTO для проверки зависимостей перед удалением
    """
    __model: abstact_model = None
    
    @property
    def model(self) -> abstact_model:
        return self.__model
    
    @model.setter
    def model(self, value: abstact_model):
        validator.validate(value, abstact_model)
        self.__model = value
