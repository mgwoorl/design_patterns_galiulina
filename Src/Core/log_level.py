from enum import Enum

"""
Перечисление уровней логирования
"""
class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

    @staticmethod
    def from_string(level_str: str) -> "LogLevel":
        """
        Преобразовать строку в уровень логирования
        
        Args:
            level_str: строковое представление уровня
            
        Returns:
            LogLevel: соответствующий уровень
        """
        if not level_str:
            return LogLevel.INFO

        level_map = {
            "DEBUG": LogLevel.DEBUG,
            "INFO": LogLevel.INFO,
            "WARNING": LogLevel.WARNING,
            "ERROR": LogLevel.ERROR
        }
        return level_map.get(level_str.upper(), LogLevel.INFO)

    def includes(self, other: "LogLevel") -> bool:
        """
        Проверяет, включает ли текущий уровень указанный
        
        Args:
            other: уровень для проверки
            
        Returns:
            bool: True если текущий уровень включает другой
        """
        order = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR]
        return order.index(self) <= order.index(other)
