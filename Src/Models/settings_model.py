from Src.Models.company_model import company_model
from Src.Core.validator import validator
from Src.Core.response_format import ResponseFormat
from datetime import datetime

"""
Модель настроек приложения
"""
class settings_model:
    __company: company_model = None
    __response_format: ResponseFormat = ResponseFormat.JSON
    __is_first_start: bool = True
    __block_period: datetime = None

    @property
    def company(self) -> company_model:
        return self.__company

    @company.setter
    def company(self, value: company_model):
        validator.validate(value, company_model)
        self.__company = value

    @property
    def response_format(self) -> ResponseFormat:
        return self.__response_format

    @response_format.setter
    def response_format(self, value: ResponseFormat):
        validator.validate(value, ResponseFormat)
        self.__response_format = value

    @property
    def is_first_start(self) -> bool:
        return self.__is_first_start

    @is_first_start.setter
    def is_first_start(self, value: bool):
        validator.validate(value, bool)
        self.__is_first_start = value

    @property
    def block_period(self) -> datetime:
        return self.__block_period

    @block_period.setter
    def block_period(self, value: datetime):
        if value is not None:
            validator.validate(value, datetime)
        self.__block_period = value
