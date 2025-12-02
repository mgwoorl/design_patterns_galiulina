from typing import Dict, List, Callable
from Src.Core.validator import validator

"""
Менеджер событий для реализации шаблона Наблюдатель
"""
class event_manager:
    __subscribers: Dict[str, List[Callable]] = {}
    
    @staticmethod
    def subscribe(event_type: str, callback: Callable):
        """
        Подписаться на событие
        """
        validator.validate(event_type, str)
        
        if event_type not in event_manager.__subscribers:
            event_manager.__subscribers[event_type] = []
        
        if callback not in event_manager.__subscribers[event_type]:
            event_manager.__subscribers[event_type].append(callback)
    
    @staticmethod
    def unsubscribe(event_type: str, callback: Callable):
        """
        Отписаться от события
        """
        if event_type in event_manager.__subscribers:
            if callback in event_manager.__subscribers[event_type]:
                event_manager.__subscribers[event_type].remove(callback)
    
    @staticmethod
    def notify(event_type: str, *args, **kwargs):
        """
        Уведомить подписчиков о событии
        """
        if event_type in event_manager.__subscribers:
            for callback in event_manager.__subscribers[event_type]:
                try:
                    callback(*args, **kwargs)
                except Exception:
                    # Игнорируем ошибки в обработчиках, чтобы не прерывать основной поток
                    continue
