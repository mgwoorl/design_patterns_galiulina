from enum import Enum

"""
Перечисление уровней логирования
"""
class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    ERROR = "ERROR"
    WARNING = "WARNING"

    """
    Проверяет, включает ли текущий уровень указанный уровень
    """
    def includes(self, other_level: "LogLevel") -> bool:
        order = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR]
        current_index = order.index(self)
        other_index = order.index(other_level)
        return current_index <= other_index

    """
    Получить список всех уровней
    """
    @staticmethod
    def all_levels() -> list:
        return [level.value for level in LogLevel]
