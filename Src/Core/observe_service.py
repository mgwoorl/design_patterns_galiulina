from Src.Core.abstract_subscriber import abstract_subscriber

"""
Реализация шаблона Наблюдатель
"""
class observe_service:
    handlers = []
    
    @staticmethod
    def add(instance):
        """
        Добавить объект под наблюдение
        """
        if instance is None:
            return
        if not isinstance(instance, abstract_subscriber):
            return
        
        if instance not in observe_service.handlers:
            observe_service.handlers.append(instance)
    
    @staticmethod
    def delete(instance):
        """
        Удалить из под наблюдения
        """
        if instance is None:
            return
        if not isinstance(instance, abstract_subscriber):
            return
        
        if instance in observe_service.handlers:
            observe_service.handlers.remove(instance)
    
    @staticmethod
    def create_event(event: str, params):
        """
        Вызвать событие
        """
        for instance in observe_service.handlers:
            instance.handle(event, params)
