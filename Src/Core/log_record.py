from datetime import datetime
from Src.Core.log_level import LogLevel
from Src.Core.validator import validator

"""
Запись лога
"""
class log_record:
    __timestamp: datetime
    __level: LogLevel
    __message: str
    __service: str
    __details: dict = None

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

    def __init__(self, level: LogLevel, message: str, service: str, details: dict = None):
        validator.validate(level, LogLevel)
        validator.validate(message, str)
        validator.validate(service, str)

        self.__timestamp = datetime.now()
        self.__level = level
        self.__message = message
        self.__service = service
        self.__details = details

    """
    Преобразовать запись лога в строку
    """
    def to_string(self) -> str:
        timestamp_str = self.__timestamp.strftime("%Y-%m-%d %H:%M:%S")
        base = f"[{timestamp_str}] [{self.__level.value}] [{self.__service}] {self.__message}"
        
        if self.__details:
            import json
            details_str = json.dumps(self.__details, ensure_ascii=False, indent=2)
            base += f"\nDetails: {details_str}"
            
        return base

    """
    Преобразовать запись лога в словарь
    """
    def to_dict(self) -> dict:
        result = {
            "timestamp": self.__timestamp.isoformat(),
            "level": self.__level.value,
            "service": self.__service,
            "message": self.__message
        }
        
        if self.__details:
            result["details"] = self.__details
            
        return result
