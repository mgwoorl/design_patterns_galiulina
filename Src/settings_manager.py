"""
Менеджер настроек приложения
"""
from Src.Models.settings_model import settings_model
from Src.Core.validator import argument_exception, operation_exception, validator
from Src.Models.company_model import company_model
from Src.Core.common import common
from Src.Core.response_format import ResponseFormat
from Src.Core.observe_service import observe_service
from Src.Core.event_type import event_type
import os
import json
from datetime import datetime

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
            
            # Логируем установку файла настроек
            observe_service.create_event(event_type.debug(), {
                "message": f"Установлен файл настроек: {full_file_name}",
                "service": "settings_manager"
            })
        else:
            error_msg = f'Не найден файл настроек {full_file_name}'
            observe_service.create_event(event_type.error(), {
                "message": error_msg,
                "service": "settings_manager"
            })
            raise argument_exception(error_msg)

    def load(self) -> bool:
        if self.__full_file_name == "":
            error_msg = "Не найден файл настроек!"
            observe_service.create_event(event_type.error(), {
                "message": error_msg,
                "service": "settings_manager"
            })
            raise operation_exception(error_msg)

        # Логируем начало загрузки настроек
        observe_service.create_event(event_type.info(), {
            "message": f"Загрузка настроек из файла: {self.__full_file_name}",
            "service": "settings_manager"
        })

        with open(self.__full_file_name, 'r', encoding='utf-8') as file_instance:
            settings = json.load(file_instance)

            if "response_format" in settings:
                format_str = settings["response_format"].upper()
                try:
                    self.__settings.response_format = ResponseFormat[format_str]
                    observe_service.create_event(event_type.debug(), {
                        "message": f"Установлен формат ответа: {format_str}",
                        "service": "settings_manager"
                    })
                except KeyError:
                    self.__settings.response_format = ResponseFormat.JSON
                    observe_service.create_event(event_type.warning(), {
                        "message": f"Неизвестный формат ответа, установлен по умолчанию: JSON",
                        "service": "settings_manager",
                        "details": {
                            "requested_format": format_str,
                            "default_format": "JSON"
                        }
                    })

            if "is_first_start" in settings:
                self.__settings.is_first_start = settings["is_first_start"]
                observe_service.create_event(event_type.debug(), {
                    "message": f"Установлен флаг первого запуска: {self.__settings.is_first_start}",
                    "service": "settings_manager"
                })

            if "block_period" in settings and settings["block_period"]:
                try:
                    block_period = datetime.fromisoformat(settings["block_period"])
                    self.__settings.block_period = block_period
                    observe_service.create_event(event_type.debug(), {
                        "message": f"Установлена дата блокировки: {block_period.isoformat()}",
                        "service": "settings_manager"
                    })
                except ValueError:
                    self.__settings.block_period = None
                    observe_service.create_event(event_type.warning(), {
                        "message": f"Некорректный формат даты блокировки: {settings['block_period']}",
                        "service": "settings_manager"
                    })

            # Загружаем настройки логирования если они есть
            if "logging" in settings:
                observe_service.create_event(event_type.debug(), {
                    "message": "Найдены настройки логирования",
                    "service": "settings_manager"
                })

            # Логируем успешную загрузку настроек
            observe_service.create_event(event_type.info(), {
                "message": "Настройки загружены успешно",
                "service": "settings_manager"
            })

            if "company" in settings.keys():
                data = settings["company"]
                return self.convert(data)

        return False

    def save(self) -> bool:
        if self.__full_file_name == "":
            error_msg = "Не указан файл для сохранения настроек!"
            observe_service.create_event(event_type.error(), {
                "message": error_msg,
                "service": "settings_manager"
            })
            raise operation_exception(error_msg)

        # Логируем начало сохранения настроек
        observe_service.create_event(event_type.info(), {
            "message": f"Сохранение настроек в файл: {self.__full_file_name}",
            "service": "settings_manager"
        })

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

        if self.__settings.block_period:
            settings_dict["block_period"] = self.__settings.block_period.isoformat()
            observe_service.create_event(event_type.debug(), {
                "message": f"Сохранение даты блокировки: {self.__settings.block_period.isoformat()}",
                "service": "settings_manager"
            })

        # Сохраняем настройки логирования если они есть в исходном файле
        try:
            with open(self.__full_file_name, 'r', encoding='utf-8') as f:
                existing_settings = json.load(f)
                if "logging" in existing_settings:
                    settings_dict["logging"] = existing_settings["logging"]
                    observe_service.create_event(event_type.debug(), {
                        "message": "Сохранены настройки логирования",
                        "service": "settings_manager"
                    })
        except:
            pass

        with open(self.__full_file_name, 'w', encoding='utf-8') as file_instance:
            json.dump(settings_dict, file_instance, ensure_ascii=False, indent=2)
        
        self.__save_to_appsettings()
        
        # Логируем успешное сохранение
        observe_service.create_event(event_type.info(), {
            "message": "Настройки сохранены успешно",
            "service": "settings_manager"
        })
        
        return True

    def __save_to_appsettings(self):
        """
        Сохранить текущие данные в appsettings.json для наблюдателей
        """
        try:
            from Src.start_service import start_service
            from Src.Logics.convert_factory import convert_factory
            from Src.reposity import reposity
            
            service = start_service()
            factory = convert_factory()
            
            appsettings_data = {
                "measure_model": [
                    factory.convert(item) for item in service.data.data.get(reposity.range_key(), [])
                ],
                "nomenclature_group_model": [
                    factory.convert(item) for item in service.data.data.get(reposity.group_key(), [])
                ],
                "nomenclature_model": [
                    factory.convert(item) for item in service.data.data.get(reposity.nomenclature_key(), [])
                ],
                "storage_model": [
                    factory.convert(item) for item in service.data.data.get(reposity.storage_key(), [])
                ],
                "first_start": self.__settings.is_first_start
            }
            
            if self.__settings.block_period:
                appsettings_data["block_date"] = self.__settings.block_period.strftime("%Y-%m-%d")
            
            appsettings_path = "appsettings.json"
            with open(appsettings_path, 'w', encoding='utf-8') as f:
                json.dump(appsettings_data, f, ensure_ascii=False, indent=2)
                
            observe_service.create_event(event_type.debug(), {
                "message": "Данные сохранены в appsettings.json",
                "service": "settings_manager"
            })
                
        except Exception as e:
            observe_service.create_event(event_type.error(), {
                "message": f"Ошибка при сохранении appsettings.json: {str(e)}",
                "service": "settings_manager"
            })

    def convert(self, data: dict) -> bool:
        validator.validate(data, dict)

        fields = common.get_fields(self.__settings.company)
        matching_keys = list(filter(lambda key: key in fields, data.keys()))

        observe_service.create_event(event_type.debug(), {
            "message": f"Конвертация данных компании: {len(matching_keys)} полей",
            "service": "settings_manager"
        })

        for key in matching_keys:
            old_value = getattr(self.__settings.company, key, None)
            setattr(self.__settings.company, key, data[key])
            new_value = data[key]
            
            if old_value != new_value:
                observe_service.create_event(event_type.debug(), {
                    "message": f"Изменено поле компании: {key}",
                    "service": "settings_manager",
                    "details": {
                        "field": key,
                        "old_value": old_value,
                        "new_value": new_value
                    }
                })

        observe_service.create_event(event_type.info(), {
            "message": f"Данные компании загружены: {self.__settings.company.name}",
            "service": "settings_manager"
        })

        return True

    def set_default(self):
        observe_service.create_event(event_type.debug(), {
            "message": "Установка настроек по умолчанию",
            "service": "settings_manager"
        })

        company = company_model()
        company.name = "Рога и копыта"
        company.inn = -1

        self.__settings = settings_model()
        self.__settings.company = company
        self.__settings.response_format = ResponseFormat.JSON
        self.__settings.is_first_start = True
        self.__settings.block_period = None

        observe_service.create_event(event_type.info(), {
            "message": "Настройки по умолчанию установлены",
            "service": "settings_manager"
        })

    def set_block_period(self, block_period: datetime) -> bool:
        validator.validate(block_period, datetime)
        
        old_block_period = self.__settings.block_period
        self.__settings.block_period = block_period
        
        # Логируем изменение даты блокировки
        observe_service.create_event(event_type.info(), {
            "message": "Изменение даты блокировки",
            "service": "settings_manager",
            "details": {
                "old_block_period": old_block_period.isoformat() if old_block_period else None,
                "new_block_period": block_period.isoformat()
            }
        })
        
        return self.save()

    def get_block_period(self) -> datetime:
        block_period = self.__settings.block_period
        
        observe_service.create_event(event_type.debug(), {
            "message": "Запрос даты блокировки",
            "service": "settings_manager",
            "details": {
                "block_period": block_period.isoformat() if block_period else None
            }
        })
        
        return block_period
