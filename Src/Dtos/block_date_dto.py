from Src.Core.abstract_dto import abstact_dto
from datetime import datetime
from Src.Core.validator import validator

class block_date_dto(abstact_dto):
    __new_block_date: datetime = None
    
    @property
    def new_block_date(self) -> datetime:
        return self.__new_block_date
    
    @new_block_date.setter
    def new_block_date(self, value):
        validator.validate(value, datetime)
        self.__new_block_date = value
