from Src.Models.settings_model import settings_model
from Src.Core.validator import argument_exception
from Src.Core.validator import operation_exception
from Src.Core.validator import validator
from Src.Models.company_model import company_model
from Src.Core.common import common
from Src.Core.response_format import ResponseFormat
import os
import json


####################################################3
# Менеджер настроек.
# Предназначен для управления настройками и хранения параметров приложения
class settings_manager:
    # Наименование файла (полный путь)
    __full_file_name: str = ""

    # Настройки
    __settings: settings_model = None

    # Singletone
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(settings_manager, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.set_default()

    # Текущие настройки
    @property
    def settings(self) -> settings_model:
        return self.__settings

    # Текущий файл
    @property
    def file_name(self) -> str:
        return self.__full_file_name

    # Полный путь к файлу настроек
    @file_name.setter
    def file_name(self, value: str):
        validator.validate(value, str)
        full_file_name = os.path.abspath(value)
        if os.path.exists(full_file_name):
            self.__full_file_name = full_file_name.strip()
        else:
            raise argument_exception(f'Не найден файл настроек {full_file_name}')

    # Загрузить настройки из Json файла
    def load(self) -> bool:
        if self.__full_file_name == "":
            raise operation_exception("Не найден файл настроек!")

        try:
            with open(self.__full_file_name, 'r', encoding='utf-8') as file_instance:
                settings = json.load(file_instance)

                # Обработка формата ответа (НОВОЕ)
                if "response_format" in settings:
                    format_str = settings["response_format"].upper()
                    try:
                        self.__settings.response_format = ResponseFormat[format_str]
                    except KeyError:
                        # Значение по умолчанию при ошибке
                        self.__settings.response_format = ResponseFormat.JSON

                if "company" in settings.keys():
                    data = settings["company"]
                    return self.convert(data)

            return False
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
            return False

    # Обработать полученный словарь
    def convert(self, data: dict) -> bool:
        validator.validate(data, dict)

        fields = common.get_fields(self.__settings.company)
        matching_keys = list(filter(lambda key: key in fields, data.keys()))

        try:
            for key in matching_keys:
                setattr(self.__settings.company, key, data[key])
        except:
            return False

        return True

    # Параметры настроек по умолчанию
    def set_default(self):
        company = company_model()
        company.name = "Рога и копыта"
        company.inn = -1

        self.__settings = settings_model()
        self.__settings.company = company
        # Устанавливаем формат по умолчанию (НОВОЕ)
        self.__settings.response_format = ResponseFormat.JSON