from Src.Models.settings_model import settings_model
from Src.Core.validator import argument_exception
from Src.Core.validator import operation_exception
from Src.Core.validator import validator
from Src.Models.company_model import company_model
from Src.Core.common import common
from Src.Core.response_format import ResponseFormat
import os
import json
from datetime import datetime

"""
Менеджер настроек приложения
"""
class settings_manager:
    __full_file_name: str = ""
    __settings: settings_model = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(settings_manager, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.set_default()

    @property
    def settings(self) -> settings_model:
        return self.__settings

    @property
    def file_name(self) -> str:
        return self.__full_file_name

    @file_name.setter
    def file_name(self, value: str):
        validator.validate(value, str)
        full_file_name = os.path.abspath(value)
        if os.path.exists(full_file_name):
            self.__full_file_name = full_file_name.strip()
        else:
            raise argument_exception(f'Не найден файл настроек {full_file_name}')

    def load(self) -> bool:
        if self.__full_file_name == "":
            raise operation_exception("Не найден файл настроек!")

        with open(self.__full_file_name, 'r', encoding='utf-8') as file_instance:
            settings = json.load(file_instance)

            if "response_format" in settings:
                format_str = settings["response_format"].upper()
                try:
                    self.__settings.response_format = ResponseFormat[format_str]
                except KeyError:
                    self.__settings.response_format = ResponseFormat.JSON

            if "is_first_start" in settings:
                self.__settings.is_first_start = settings["is_first_start"]

            if "block_period" in settings and settings["block_period"]:
                try:
                    block_period = datetime.fromisoformat(settings["block_period"])
                    self.__settings.block_period = block_period
                except ValueError:
                    self.__settings.block_period = None

            if "company" in settings.keys():
                data = settings["company"]
                return self.convert(data)

        return False

    def save(self) -> bool:
        if self.__full_file_name == "":
            raise operation_exception("Не указан файл для сохранения настроек!")

        settings_dict = {
            "response_format": self.__settings.response_format.value,
            "is_first_start": self.__settings.is_first_start,
            "company": {
                "name": self.__settings.company.name,
                "inn": self.__settings.company.inn,
                "bic": self.__settings.company.bic,
                "corr_account": self.__settings.company.corr_account,
                "account": self.__settings.company.account,
                "ownership": self.__settings.company.ownership
            }
        }

        # Добавляем дату блокировки если она установлена
        if self.__settings.block_period:
            settings_dict["block_period"] = self.__settings.block_period.isoformat()

        with open(self.__full_file_name, 'w', encoding='utf-8') as file_instance:
            json.dump(settings_dict, file_instance, ensure_ascii=False, indent=2)

        return True

    def convert(self, data: dict) -> bool:
        validator.validate(data, dict)

        fields = common.get_fields(self.__settings.company)
        matching_keys = list(filter(lambda key: key in fields, data.keys()))

        for key in matching_keys:
            setattr(self.__settings.company, key, data[key])

        return True

    def set_default(self):
        company = company_model()
        company.name = "Рога и копыта"
        company.inn = -1

        self.__settings = settings_model()
        self.__settings.company = company
        self.__settings.response_format = ResponseFormat.JSON
        self.__settings.is_first_start = True
        self.__settings.block_period = None

    def set_block_period(self, block_period: datetime) -> bool:
        """
        Установка даты блокировки
        
        Args:
            block_period (datetime): дата блокировки
            
        Returns:
            bool: True если установка прошла успешно
        """
        validator.validate(block_period, datetime)
        self.__settings.block_period = block_period
        return self.save()

    def get_block_period(self) -> datetime:
        """
        Получение текущей даты блокировки
        
        Returns:
            datetime: дата блокировки или None
        """
        return self.__settings.block_period
