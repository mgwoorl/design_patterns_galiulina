from enum import Enum

"""
Перечисление уровней логирования
"""
class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO" 
    ERROR = "ERROR"
    WARNING = "WARNING"

    @staticmethod
    def from_string(value: str) -> "LogLevel":
        """
        Преобразовать строку в уровень логирования
        
        Args:
            value (str): строковое представление уровня
            
        Returns:
            LogLevel: соответствующий уровень логирования
        """
        value = value.upper()
        if value == "DEBUG":
            return LogLevel.DEBUG
        elif value == "INFO":
            return LogLevel.INFO
        elif value == "WARNING":
            return LogLevel.WARNING
        elif value == "ERROR":
            return LogLevel.ERROR
        else:
            return LogLevel.INFO
