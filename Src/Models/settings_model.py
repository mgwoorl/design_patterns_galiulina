from Src.Models.company_model import company_model
from Src.Core.validator import validator
from Src.Core.response_format import ResponseFormat


######################################
# Модель настроек приложения
class settings_model:
    __company: company_model = None
    __response_format: ResponseFormat = ResponseFormat.JSON
    __is_first_start: bool = True

    # Текущая организация
    @property
    def company(self) -> company_model:
        return self.__company

    @company.setter
    def company(self, value: company_model):
        validator.validate(value, company_model)
        self.__company = value

    # Формат ответа
    @property
    def response_format(self) -> ResponseFormat:
        return self.__response_format

    @response_format.setter
    def response_format(self, value: ResponseFormat):
        validator.validate(value, ResponseFormat)
        self.__response_format = value

    # Первый старт
    @property
    def is_first_start(self) -> bool:
        return self.__is_first_start

    @is_first_start.setter
    def is_first_start(self, value: bool):
        validator.validate(value, bool)
        self.__is_first_start = value
