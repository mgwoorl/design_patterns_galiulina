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
        if value is None:
            return LogLevel.DEBUG
            
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

    def includes(self, other: "LogLevel") -> bool:
        """
        Проверить, включает ли текущий уровень указанный уровень
        
        Args:
            other (LogLevel): уровень для проверки
            
        Returns:
            bool: True если текущий уровень включает другой
        """
        levels = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR]
        current_index = levels.index(self)
        other_index = levels.index(other)
        return current_index <= other_index
