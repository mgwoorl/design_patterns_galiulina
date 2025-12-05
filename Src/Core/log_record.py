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

    def to_string(self) -> str:
        """
        Преобразовать запись лога в строку
        
        Returns:
            str: строковое представление записи лога
        """
        timestamp_str = self.__timestamp.strftime("%Y-%m-%d %H:%M:%S")
        result = f"{timestamp_str}\t[{self.__level.value}] [{self.__service}] {self.__message}"
        
        if self.__details:
            import json
            details_str = json.dumps(self.__details, ensure_ascii=False, indent=2)
            result += f"\n{details_str}"
            
        return result
