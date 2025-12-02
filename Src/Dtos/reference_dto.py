"""
DTO для работы со справочниками
"""
from Src.Core.abstract_dto import abstract_dto
from Src.Core.validator import validator


class reference_dto(abstract_dto):
    """
    DTO для передачи данных о справочнике
    """
    __model_dto_dict: dict = None
    
    @property
    def model_dto_dict(self) -> dict:
        return self.__model_dto_dict
    
    @model_dto_dict.setter
    def model_dto_dict(self, value: dict):
        validator.validate(value, dict)
        self.__model_dto_dict = value
