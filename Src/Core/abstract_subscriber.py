"""
Абстрактный подписчик на события
"""
from abc import ABCMeta, abstractmethod
from typing import Any
from Src.Core.validator import validator, operation_exception
from Src.Core.event_type import event_type


class abstract_subscriber(metaclass=ABCMeta):
    """
    Абстрактный подписчик на события
    """
    
    @abstractmethod
    def handle(self, event: str, params: Any) -> None:
        """
        Обработка события
        """
        validator.validate(event, str)
        
        # Проверяем, что событие существует
        events = event_type.events()
        if event not in events:
            raise operation_exception(f"{event} - не является событием!")
