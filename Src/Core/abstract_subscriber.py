"""
Абстрактный класс для подписчиков в паттерне Наблюдатель
"""
from Src.Core.event_type import event_type
from Src.Core.validator import validator, operation_exception

class abstract_subscriber:
    """
    Обработка события
    """
    def handle(self, event: str, params):
        validator.validate(event, str)
        events = event_type.events()
        if event not in events:
            raise operation_exception(f"{event} - не является событием!")
