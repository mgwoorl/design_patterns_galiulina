"""
Абстрактный класс для наследования моделей
Теперь также является подписчиком на события
"""
from abc import ABC
import uuid
from Src.Core.validator import validator, operation_exception
from Src.Core.abstract_subscriber import abstract_subscriber
from Src.Core.observe_service import observe_service
from Src.Core.event_type import event_type


class abstact_model(ABC, abstract_subscriber):
    """
    Абстрактная модель с полем уникального кода
    Теперь также является подписчиком на события
    """
    __unique_code: str

    def __init__(self) -> None:
        super().__init__()
        self.__unique_code = uuid.uuid4().hex
        observe_service.add(self) 

    """
    Уникальный код
    """
    @property
    def unique_code(self) -> str:
        return self.__unique_code

    @unique_code.setter
    def unique_code(self, value: str):
        validator.validate(value, str)
        self.__unique_code = value.strip()

    """
    Перегрузка штатного варианта сравнения
    """
    def __eq__(self, value) -> bool:
        if value is None:
            return False
        if not isinstance(value, abstact_model):
            return False

        return self.unique_code == value.unique_code

    def __hash__(self):
        return hash(self.unique_code)

    def __contains__(self, value) -> bool:
        values = self.__dict__.values()
        return any(value == item or 
                  (isinstance(item, (list, tuple, abstact_model, str)) and value in item) 
                  for item in values)

    def __str__(self):
        return self.unique_code

    def handle(self, event: str, params) -> None:
        """
        Обработка событий для зависимостей
        Вызывается observe_service при создании событий
        """
        super().handle(event, params)
        
        if event == event_type.update_dependencies():
            from Src.Dtos.update_dependencies_dto import update_dependencies_dto
            validator.validate(params, update_dependencies_dto)
            
            old_model = params.old_model
            new_model = params.new_model
            
            # Проверяем все поля модели
            for field_name, field_value in self.__dict__.items():
                # Пропускаем приватные поля
                if field_name.startswith('_') and not field_name.endswith('__'):
                    continue
                
                # Если поле равно старой модели, заменяем на новую
                if field_value == old_model:
                    setattr(self, field_name, new_model)
                
                # Также проверяем списки и кортежи
                elif isinstance(field_value, (list, tuple)):
                    for i, item in enumerate(field_value):
                        if item == old_model:
                            field_value[i] = new_model
        
        elif event == event_type.check_dependencies():
            from Src.Dtos.check_dependencies_dto import check_dependencies_dto
            validator.validate(params, check_dependencies_dto)
            
            model_to_delete = params.model
            
            # Проверяем все поля модели
            for field_name, field_value in self.__dict__.items():
                # Пропускаем приватные поля
                if field_name.startswith('_') and not field_name.endswith('__'):
                    continue
                
                # Если поле содержит удаляемую модель, кидаем исключение
                if field_value == model_to_delete:
                    raise operation_exception(
                        f"Отказ в удалении объекта по причине: удаляемый объект содержится в {self}."
                    )
                
                # Также проверяем списки и кортежи
                elif isinstance(field_value, (list, tuple)):
                    if model_to_delete in field_value:
                        raise operation_exception(
                            f"Отказ в удалении объекта по причине: удаляемый объект содержится в {self}."
                        )
