from Src.Core.abstract_dto import abstact_dto
from Src.Core.validator import validator

class reference_dto(abstact_dto):
    __model_dto_dict: dict = None
    
    @property
    def model_dto_dict(self) -> dict:
        return self.__model_dto_dict
    
    @model_dto_dict.setter
    def model_dto_dict(self, value):
        validator.validate(value, dict)
        self.__model_dto_dict = value
