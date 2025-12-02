"""
Реализация наблюдателя (сервис наблюдения)
"""
from typing import Any, List
from Src.Core.abstract_subscriber import abstract_subscriber
from Src.Core.validator import validator


class observe_service:
    """
    Сервис для управления подписчиками и событиями (Observable)
    """
    __handlers: List[abstract_subscriber] = []
    
    @staticmethod
    def add(instance: abstract_subscriber) -> None:
        """
        Добавить объект под наблюдение
        """
        if instance is None:
            return
        
        if not isinstance(instance, abstract_subscriber):
            return
        
        if instance not in observe_service.__handlers:
            observe_service.__handlers.append(instance)
    
    @staticmethod
    def delete(instance: abstract_subscriber) -> None:
        """
        Удалить из под наблюдения
        """
        if instance is None:
            return
        
        if not isinstance(instance, abstract_subscriber):
            return
        
        if instance in observe_service.__handlers:
            observe_service.__handlers.remove(instance)
    
    @staticmethod
    def create_event(event: str, params: Any = None) -> None:
        """
        Вызвать событие
        """
        validator.validate(event, str)
        
        for instance in observe_service.__handlers:
            instance.handle(event, params)
