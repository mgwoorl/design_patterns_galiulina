from datetime import datetime
from Src.Core.log_level import LogLevel
from Src.Core.validator import validator

"""
Модель записи лога
"""
class log_record:
    __timestamp: datetime
    __level: LogLevel
    __message: str
    __service: str
    __details: dict = None

    def __init__(self, level: LogLevel, message: str, service: str, details: dict = None):
        validator.validate(level, LogLevel)
        validator.validate(message, str)
        validator.validate(service, str)
        
        self.__timestamp = datetime.now()
        self.__level = level
        self.__message = message
        self.__service = service
        self.__details = details

    @property
    def timestamp(self) -> datetime:
        return self.__timestamp

    @property
    def level(self) -> LogLevel:
        return self.__level

    @property
    def message(self) -> str:
        return self.__message

    @property
    def service(self) -> str:
        return self.__service

    @property
    def details(self) -> dict:
        return self.__details

    def to_dict(self) -> dict:
        """
        Преобразовать запись лога в словарь
        
        Returns:
            dict: словарь с данными лога
        """
        result = {
            "timestamp": self.__timestamp.isoformat(),
            "level": self.__level.value,
            "service": self.__service,
            "message": self.__message
        }
        
        if self.__details:
            result["details"] = self.__details
            
        return result
    
    def to_string(self, log_format: str = None, date_format: str = None) -> str:
        """
        Преобразовать запись лога в строку
        
        Args:
            log_format: формат строки
            date_format: формат даты
            
        Returns:
            str: строковое представление
        """
        if not log_format:
            log_format = "[{level}] {timestamp} - {service}: {message}"
        if not date_format:
            date_format = "%Y-%m-%d %H:%M:%S"
            
        timestamp_str = self.__timestamp.strftime(date_format)
        message = log_format
        message = message.replace("{level}", self.__level.value)
        message = message.replace("{timestamp}", timestamp_str)
        message = message.replace("{service}", self.__service)
        message = message.replace("{message}", self.__message)
        
        if self.__details:
            import json
            try:
                details_str = json.dumps(self.__details, ensure_ascii=False, indent=2)
                message += f"\n{details_str}"
            except:
                message += f"\n{str(self.__details)}"
            
        return message
