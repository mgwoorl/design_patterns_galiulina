"""
DTO для обновления зависимостей
"""
from Src.Core.abstract_dto import abstract_dto
from Src.Core.abstract_model import abstact_model
from Src.Core.validator import validator


class update_dependencies_dto(abstract_dto):
    """
    DTO для передачи информации об обновлении зависимостей
    """
    __old_model: abstact_model = None
    __new_model: abstact_model = None
    
    @property
    def old_model(self) -> abstact_model:
        return self.__old_model
    
    @old_model.setter
    def old_model(self, value: abstact_model):
        validator.validate(value, abstact_model)
        self.__old_model = value
    
    @property
    def new_model(self) -> abstact_model:
        return self.__new_model
    
    @new_model.setter
    def new_model(self, value: abstact_model):
        validator.validate(value, abstact_model)
        self.__new_model = value
