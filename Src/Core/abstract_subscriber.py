from Src.Core.event_type import event_type
from Src.Core.validator import validator, operation_exception

"""
Абстрактный подписчик для реализации шаблона Наблюдатель
"""
class abstract_subscriber:
    
    def handle(self, event: str, params):
        """
        Обработка события
        
        Args:
            event (str): тип события
            params: параметры события
            
        Raises:
            operation_exception: если событие неизвестно
        """
        validator.validate(event, str)
        events = event_type.events()
        if event not in events:
            raise operation_exception(f"{event} - не является событием!")
