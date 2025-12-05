from abc import ABC, abstractmethod
from Src.Core.log_level import LogLevel
from Src.Core.log_record import log_record

"""
Абстрактный класс обработчика логов 
"""
class log_handler(ABC):

    @abstractmethod
    def handle(self, log_record: log_record):
        """
        Обработать запись лога

        Args:
            log_record (log_record): запись лога для обработки
        """
        pass

    @abstractmethod
    def should_handle(self, log_record: log_record) -> bool:
        """
        Проверить, должен ли обработчик обработать данную запись

        Args:
            log_record (log_record): запись лога для проверки

        Returns:
            bool: True если обработчик должен обработать запись
        """
        pass
