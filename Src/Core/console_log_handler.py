from Src.Core.log_handler import log_handler
from Src.Core.log_record import log_record
from Src.Core.log_level import LogLevel
from Src.Core.validator import validator

"""
Обработчик логов для вывода в консоль
"""
class console_log_handler(log_handler):
    __min_level: LogLevel

    def __init__(self, min_level: LogLevel = LogLevel.DEBUG):
        validator.validate(min_level, LogLevel)
        self.__min_level = min_level

    def handle(self, log_record: log_record):
        """
        Вывести запись лога в консоль

        Args:
            log_record (log_record): запись лога для вывода
        """
        validator.validate(log_record, log_record)
        
        if self.should_handle(log_record):
            log_str = log_record.to_string()
            print(log_str)

    def should_handle(self, log_record: log_record) -> bool:
        """
        Проверить, должен ли обработчик обработать данную запись

        Args:
            log_record (log_record): запись лога для проверки

        Returns:
            bool: True если уровень лога >= минимальному уровню
        """
        validator.validate(log_record, log_record)
        return self.__min_level.includes(log_record.level)
