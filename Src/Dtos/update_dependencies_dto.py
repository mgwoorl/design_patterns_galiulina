from Src.Core.abstract_dto import abstact_dto
from Src.Models.abstract_reference import abstact_reference
from Src.Core.validator import validator

class update_dependencies_dto(abstact_dto):
    __old_model: abstact_reference = None
    __new_model: abstact_reference = None
    
    @property
    def old_model(self) -> abstact_reference:
        return self.__old_model
    
    @old_model.setter
    def old_model(self, value):
        validator.validate(value, abstact_reference)
        self.__old_model = value
    
    @property
    def new_model(self) -> abstact_reference:
        return self.__new_model
    
    @new_model.setter
    def new_model(self, value):
        validator.validate(value, abstact_reference)
        self.__new_model = value
