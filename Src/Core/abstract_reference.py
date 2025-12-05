"""
Абстрактная модель для справочников с поддержкой наблюдателя
Наследуется от abstract_subscriber для получения уведомлений о событиях
"""
from abc import ABC
import uuid
from Src.Core.validator import validator
from functools import total_ordering
from Src.Core.abstract_subscriber import abstract_subscriber
from Src.Core.observe_service import observe_service
from Src.Core.event_type import event_type

@total_ordering
class abstact_reference(ABC, abstract_subscriber):
    __unique_code: str

    def __init__(self) -> None:
        super().__init__()
        self.__unique_code = uuid.uuid4().hex
        observe_service.add(self)

    """
    Уникальный код модели
    """
    @property
    def unique_code(self) -> str:
        return self.__unique_code

    @unique_code.setter
    def unique_code(self, value: str):
        validator.validate(value, str)
        self.__unique_code = value.strip()

    """
    Перегрузка операторов сравнения
    """
    def __eq__(self, value) -> bool:
        if value is None:
            return False
        if not isinstance(value, abstact_reference):
            return False

        return self.unique_code == value.unique_code

    def __lt__(self, value) -> bool:
        if value is None:
            return False
        if not isinstance(value, abstact_reference):
            return False

        return self.unique_code < value.unique_code

    def __contains__(self, value) -> bool:
        values = [value for value in self.__dict__.values() if value is not None]
        return any(value == item or (isinstance(item, (list, tuple, abstact_reference, str)) and value in item) for item in values)

    def __str__(self):
        return self.unique_code

    """
    Обработка событий наблюдателя
    """
    def handle(self, event: str, params):
        super().handle(event, params)

        if event == event_type.update_dependencies():
            from Src.Dtos.update_dependencies_dto import update_dependencies_dto
            validator.validate(params, update_dependencies_dto)
            old_model = params.old_model
            new_model = params.new_model
            from Src.Core.common import common
            for field in common.get_fields(self):
                if getattr(self, field) == old_model:
                    setattr(self, field, new_model)
        elif event == event_type.check_dependencies():
            from Src.Dtos.check_dependencies_dto import check_dependencies_dto
            validator.validate(params, check_dependencies_dto)
            model = params.model
            from Src.Core.common import common
            for field in common.get_fields(self):
                if getattr(self, field) == model:
                    from Src.Core.validator import operation_exception
                    raise operation_exception(f"Отказ в удалении объекта по причине: удаляемый объект содержится в {self}.")
