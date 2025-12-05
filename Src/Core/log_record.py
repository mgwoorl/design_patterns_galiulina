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
