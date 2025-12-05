"""
Сервис логирования
"""
from Src.Core.log_record import log_record
from Src.Core.log_level import LogLevel
from Src.Core.abstract_subscriber import abstract_subscriber
from Src.Core.validator import validator
from Src.Core.observe_service import observe_service
from Src.Core.event_type import event_type
import os
import json

class logger_service(abstract_subscriber):
    __min_level: LogLevel = LogLevel.DEBUG
    __log_to_console: bool = True
    __log_to_file: bool = False
    __file_path: str = "app.log"
    __log_format: str = "[{level}] {timestamp} - {service}: {message}"
    __log_date_format: str = "%Y-%m-%d %H:%M:%S"
    
    def __init__(self):
        # Загружаем настройки из settings.json
        self.__load_settings()
        observe_service.add(self)
    
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
                        
                        # Файл для логирования
                        if "log_file" in logging_settings:
                            self.__file_path = logging_settings["log_file"]
                        
                        # Формат логов
                        if "log_format" in logging_settings:
                            self.__log_format = logging_settings["log_format"]
                        
                        # Формат даты
                        if "log_date_format" in logging_settings:
                            self.__log_date_format = logging_settings["log_date_format"]
                            
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
                        "log_file": self.__file_path if self.__log_to_file else None
                    }
                ))
                
        except Exception as e:
            # Используем значения по умолчанию при ошибке
            self.__write_log(log_record(
                LogLevel.WARNING,
                f"Ошибка загрузки настроек логирования: {str(e)}. Используются значения по умолчанию",
                "logger_service"
            ))
    
    def __should_log(self, level: LogLevel) -> bool:
        """
        Проверить, нужно ли логировать на данном уровне
        
        Args:
            level (LogLevel): уровень логирования для проверки
            
        Returns:
            bool: True если нужно логировать
        """
        return self.__min_level.includes(level)
    
    def __format_message(self, record: log_record) -> str:
        """
        Форматировать сообщение лога
        
        Args:
            record (log_record): запись лога
            
        Returns:
            str: отформатированное сообщение
        """
        timestamp_str = record.timestamp.strftime(self.__log_date_format)
        message = self.__log_format
        message = message.replace("{level}", record.level.value)
        message = message.replace("{timestamp}", timestamp_str)
        message = message.replace("{service}", record.service)
        message = message.replace("{message}", record.message)
        
        if record.details:
            import json
            details_str = json.dumps(record.details, ensure_ascii=False, indent=2)
            message += f"\n{details_str}"
            
        return message
    
    def __write_log(self, record: log_record):
        """
        Записать лог в соответствии с настройками
        
        Args:
            record (log_record): запись лога для записи
        """
        if not self.__should_log(record.level):
            return
            
        log_str = self.__format_message(record) + "\n"
        
        # Вывод в консоль
        if self.__log_to_console:
            print(log_str)
        
        # Запись в файл
        if self.__log_to_file:
            try:
                # Создаем директорию если ее нет
                directory = os.path.dirname(self.__file_path)
                if directory and not os.path.exists(directory):
                    os.makedirs(directory)
                    
                with open(self.__file_path, 'a', encoding='utf-8') as f:
                    f.write(log_str)
            except Exception as e:
                # Если не удалось записать в файл, выводим в консоль
                if not self.__log_to_console:
                    print(f"{record.timestamp.strftime(self.__log_date_format)}\t[ERROR] [logger_service] Ошибка записи в файл: {str(e)}")
    
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
