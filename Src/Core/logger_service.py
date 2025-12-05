"""
Сервис логирования с поддержкой ежедневных файлов
"""
from Src.Core.log_record import log_record
from Src.Core.log_level import LogLevel
from Src.Core.abstract_subscriber import abstract_subscriber
from Src.Core.validator import validator
from Src.Core.observe_service import observe_service
from Src.Core.event_type import event_type
import os
import json
from datetime import datetime

class logger_service(abstract_subscriber):
    __instance = None
    __min_level: LogLevel = LogLevel.DEBUG
    __log_to_console: bool = True
    __log_to_file: bool = False
    __log_directory: str = "logs"
    __log_file_prefix: str = "app"
    __log_format: str = "[{level}] {timestamp} - {service}: {message}"
    __log_date_format: str = "%Y-%m-%d %H:%M:%S"
    __current_log_file: str = None
    __current_date: str = None
    __enable_daily_files: bool = True
    
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(logger_service, cls).__new__(cls)
        return cls.__instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            # Загружаем настройки из settings.json
            self.__load_settings()
            observe_service.add(self)
            
            # Инициализируем текущий файл лога
            self.__update_log_file()
            self._initialized = True
    
    def __load_settings(self):
        """
        Загрузить настройки логирования из settings.json
        """
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                    if "logging" in settings:
                        logging_settings = settings["logging"]
                        
                        # Минимальный уровень
                        if "min_level" in logging_settings:
                            self.__min_level = LogLevel.from_string(logging_settings["min_level"])
                        
                        # Куда выводить
                        if "output" in logging_settings:
                            output = logging_settings["output"].lower()
                            if output == "console":
                                self.__log_to_console = True
                                self.__log_to_file = False
                            elif output == "file":
                                self.__log_to_console = False
                                self.__log_to_file = True
                            elif output == "both":
                                self.__log_to_console = True
                                self.__log_to_file = True
                        
                        # Директория для логов
                        if "log_directory" in logging_settings:
                            self.__log_directory = logging_settings["log_directory"]
                        
                        # Префикс файла
                        if "log_file_prefix" in logging_settings:
                            self.__log_file_prefix = logging_settings["log_file_prefix"]
                        
                        # Формат логов
                        if "log_format" in logging_settings:
                            self.__log_format = logging_settings["log_format"]
                        
                        # Формат даты
                        if "log_date_format" in logging_settings:
                            self.__log_date_format = logging_settings["log_date_format"]
                        
                        # Дополнительные настройки
                        if "enable_daily_files" in logging_settings:
                            self.__enable_daily_files = logging_settings["enable_daily_files"]
                            
                # Логируем успешную загрузку настроек
                self.__write_log(log_record(
                    LogLevel.INFO,
                    "Настройки логирования загружены",
                    "logger_service",
                    {
                        "min_level": self.__min_level.value,
                        "output": "console" if self.__log_to_console and not self.__log_to_file else 
                                 "file" if not self.__log_to_console and self.__log_to_file else 
                                 "both",
                        "log_directory": self.__log_directory,
                        "log_file_prefix": self.__log_file_prefix,
                        "enable_daily_files": self.__enable_daily_files
                    }
                ))
                
        except Exception as e:
            # Используем значения по умолчанию при ошибке
            try:
                record = log_record(
                    LogLevel.WARNING,
                    f"Ошибка загрузки настроек логирования: {str(e)}. Используются значения по умолчанию",
                    "logger_service"
                )
                # Пытаемся записать в консоль напрямую только если включен вывод в консоль
                if self.__log_to_console:
                    print(record.to_string(self.__log_format, self.__log_date_format))
            except:
                # Если даже это не работает, просто игнорируем ошибку
                pass
    
    def __update_log_file(self):
        """
        Обновить текущий файл лога на основе даты
        """
        if not self.__log_to_file:
            return
            
        today = datetime.now().strftime("%Y-%m-%d")
        
        if self.__current_date != today:
            self.__current_date = today
            
            if self.__enable_daily_files:
                # Ежедневные файлы
                self.__current_log_file = f"{self.__log_directory}/{self.__log_file_prefix}_{today}.log"
            else:
                # Один файл
                self.__current_log_file = f"{self.__log_directory}/{self.__log_file_prefix}.log"
            
            # Создаем директорию если ее нет
            directory = os.path.dirname(self.__current_log_file)
            if directory and not os.path.exists(directory):
                try:
                    os.makedirs(directory)
                except Exception as e:
                    # Логируем ошибку создания директории
                    record = log_record(
                        LogLevel.ERROR,
                        f"Ошибка создания директории для логов: {str(e)}",
                        "logger_service"
                    )
                    if self.__log_to_console:
                        print(record.to_string(self.__log_format, self.__log_date_format))
    
    def __should_log(self, level: LogLevel) -> bool:
        """
        Проверить, нужно ли логировать на данном уровне
        
        Args:
            level (LogLevel): уровень логирования для проверки
            
        Returns:
            bool: True если нужно логировать
        """
        return self.__min_level.includes(level)
    
    def __write_log(self, record: log_record):
        """
        Записать лог в соответствии с настройками
        
        Args:
            record (log_record): запись лога для записи
        """
        if not self.__should_log(record.level):
            return
        
        # Обновляем файл если нужно
        self.__update_log_file()
            
        log_str = record.to_string(self.__log_format, self.__log_date_format) + "\n"
        
        # Вывод в консоль (если включено в настройках)
        if self.__log_to_console:
            print(log_str, end='')
        
        # Запись в файл (если включено в настройках)
        if self.__log_to_file and self.__current_log_file:
            try:
                with open(self.__current_log_file, 'a', encoding='utf-8') as f:
                    f.write(log_str)
            except Exception as e:
                # Если не удалось записать в файл, и вывод в консоль не включен,
                # пытаемся вывести ошибку через консоль
                if not self.__log_to_console:
                    error_record = log_record(
                        LogLevel.ERROR,
                        f"Ошибка записи в файл: {str(e)}",
                        "logger_service"
                    )
                    print(error_record.to_string(self.__log_format, self.__log_date_format))
    
    def log(self, level: LogLevel, message: str, service: str, details: dict = None):
        """
        Создать запись лога
        
        Args:
            level (LogLevel): уровень логирования
            message (str): сообщение лога
            service (str): сервис-источник
            details (dict): дополнительные детали
        """
        record = log_record(level, message, service, details)
        self.__write_log(record)
    
    def debug(self, message: str, service: str, details: dict = None):
        """
        Создать запись лога уровня DEBUG
        
        Args:
            message (str): сообщение лога
            service (str): сервис-источник
            details (dict): дополнительные детали
        """
        self.log(LogLevel.DEBUG, message, service, details)
    
    def info(self, message: str, service: str, details: dict = None):
        """
        Создать запись лога уровня INFO
        
        Args:
            message (str): сообщение лога
            service (str): сервис-источник
            details (dict): дополнительные детали
        """
        self.log(LogLevel.INFO, message, service, details)
    
    def warning(self, message: str, service: str, details: dict = None):
        """
        Создать запись лога уровня WARNING
        
        Args:
            message (str): сообщение лога
            service (str): сервис-источник
            details (dict): дополнительные детали
        """
        self.log(LogLevel.WARNING, message, service, details)
    
    def error(self, message: str, service: str, details: dict = None):
        """
        Создать запись лога уровня ERROR
        
        Args:
            message (str): сообщение лога
            service (str): сервис-источник
            details (dict): дополнительные детали
        """
        self.log(LogLevel.ERROR, message, service, details)
    
    def handle(self, event: str, params):
        """
        Обработка событий логирования
        
        Args:
            event (str): тип события
            params: параметры события
        """
        super().handle(event, params)
        
        if event == event_type.debug():
            if isinstance(params, dict):
                self.debug(params.get("message", ""), params.get("service", "unknown"), params.get("details"))
            else:
                self.debug(str(params), "unknown")
        elif event == event_type.info():
            if isinstance(params, dict):
                self.info(params.get("message", ""), params.get("service", "unknown"), params.get("details"))
            else:
                self.info(str(params), "unknown")
        elif event == event_type.warning():
            if isinstance(params, dict):
                self.warning(params.get("message", ""), params.get("service", "unknown"), params.get("details"))
            else:
                self.warning(str(params), "unknown")
        elif event == event_type.error():
            if isinstance(params, dict):
                self.error(params.get("message", ""), params.get("service", "unknown"), params.get("details"))
            else:
                self.error(str(params), "unknown")

# Глобальный экземпляр логгера
logger = logger_service()
