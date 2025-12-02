from Src.Core.validator import validator, argument_exception, operation_exception
from Src.Core.prototype import prototype
from Src.reposity import reposity
from Src.Core.abstract_model import abstact_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model
from Src.Models.storage_model import storage_model
from Src.Core.event_manager import event_manager
from Src.Core.event_types import event_types
from Src.Dtos.filter_dto import filter_dto
from Src.Core.filter_type import FilterType
import uuid

"""
Сервис для работы со справочниками
Использует Prototype для поиска и EventManager для уведомлений
"""
class reference_service:
    __repo: reposity = None
    
    def __init__(self, data: reposity):
        if not isinstance(data, reposity):
            raise argument_exception("Некорректный тип данных")
        self.__repo = data

    def __get_repository_key(self, reference_type: str):
        """Получает ключ репозитория по типу справочника"""
        key_map = {
            "nomenclature": reposity.nomenclature_key(),
            "group": reposity.group_key(),
            "range": reposity.range_key(),
            "storage": reposity.storage_key()
        }
        
        if reference_type not in key_map:
            raise operation_exception(f"Неизвестный тип справочника: {reference_type}")
        
        return key_map[reference_type]

    def __get_data_list(self, reference_type: str):
        """Получает список данных по типу справочника"""
        key = self.__get_repository_key(reference_type)
        return self.__repo.data.get(key, [])

    def add(self, reference_type: str, data: dict) -> abstact_model:
        """
        Добавление элемента в справочник
        """
        validator.validate(reference_type, str)
        validator.validate(data, dict)
        
        repository_key = self.__get_repository_key(reference_type)
        
        # Создаем элемент из данных
        if reference_type == "nomenclature":
            item = self.__create_nomenclature_from_data(data)
            event_type = event_types.AFTER_CREATE_NOMENCLATURE
        elif reference_type == "group":
            item = group_model.create(data.get("name", ""))
            event_type = event_types.AFTER_CREATE_GROUP
        elif reference_type == "range":
            item = self.__create_range_from_data(data)
            event_type = event_types.AFTER_CREATE_RANGE
        elif reference_type == "storage":
            item = storage_model.create(
                data.get("name", ""),
                data.get("address", "")
            )
            event_type = event_types.AFTER_CREATE_STORAGE
        else:
            raise operation_exception(f"Неподдерживаемый тип справочника: {reference_type}")
        
        # Генерируем уникальный код если не указан
        if not hasattr(item, 'unique_code') or not item.unique_code:
            item.unique_code = uuid.uuid4().hex
        
        # Добавляем в репозиторий
        self.__repo.data[repository_key].append(item)
        
        # Уведомляем о создании
        event_manager.notify(event_type, item)
        event_manager.notify(event_types.DATA_EXPORT_NEEDED)
        
        return item

    def update(self, reference_type: str, item_id: str, data: dict) -> bool:
        """
        Изменение элемента справочника
        """
        validator.validate(reference_type, str)
        validator.validate(item_id, str)
        validator.validate(data, dict)
        
        item = self.find_by_id(reference_type, item_id)
        
        if not item:
            raise operation_exception(f"Элемент с ID {item_id} не найден")
        
        # Обновляем поля
        if reference_type == "nomenclature":
            self.__update_nomenclature(item, data)
            event_type = event_types.AFTER_UPDATE_NOMENCLATURE
        elif reference_type == "group":
            if "name" in data:
                item.name = data["name"]
            event_type = event_types.AFTER_UPDATE_GROUP
        elif reference_type == "range":
            self.__update_range(item, data)
            event_type = event_types.AFTER_UPDATE_RANGE
        elif reference_type == "storage":
            if "name" in data:
                item.name = data["name"]
            if "address" in data:
                item.address = data["address"]
            event_type = event_types.AFTER_UPDATE_STORAGE
        
        # Уведомляем об обновлении
        event_manager.notify(event_type, item)
        event_manager.notify(event_types.DATA_EXPORT_NEEDED)
        
        return True

    def delete(self, reference_type: str, item_id: str) -> bool:
        """
        Удаление элемента справочника
        """
        validator.validate(reference_type, str)
        validator.validate(item_id, str)
        
        # Получаем событие для проверки удаления
        delete_event_map = {
            "nomenclature": event_types.BEFORE_DELETE_NOMENCLATURE,
            "group": event_types.BEFORE_DELETE_GROUP,
            "range": event_types.BEFORE_DELETE_RANGE,
            "storage": event_types.BEFORE_DELETE_STORAGE
        }
        
        event_type = delete_event_map.get(reference_type)
        if event_type:
            # Уведомляем о планируемом удалении
            # Если какой-то обработчик выбросит исключение - удаление будет отменено
            event_manager.notify(event_type, item_id)
        
        items = self.__get_data_list(reference_type)
        repository_key = self.__get_repository_key(reference_type)
        
        # Ищем и удаляем элемент
        for i, item in enumerate(items):
            if item.unique_code == item_id:
                del self.__repo.data[repository_key][i]
                
                # Уведомляем о необходимости экспорта
                event_manager.notify(event_types.DATA_EXPORT_NEEDED)
                return True
        
        raise operation_exception(f"Элемент с ID {item_id} не найден")

    def get(self, reference_type: str, item_id: str) -> abstact_model:
        """
        Получение элемента справочника по ID
        """
        return self.find_by_id(reference_type, item_id)

    def find_by_id(self, reference_type: str, item_id: str) -> abstact_model:
        """
        Поиск элемента по ID с использованием Прототипа
        """
        items = self.__get_data_list(reference_type)
        
        if not items:
            return None
        
        # Используем прототип для фильтрации
        filters = [
            filter_dto().create({
                "field_name": "unique_code",
                "value": item_id,
                "type": FilterType.EQUALS.value
            })
        ]
        
        result = prototype.filter(items, filters)
        return result[0] if result else None

    def get_all(self, reference_type: str) -> list:
        """
        Получение всех элементов справочника
        """
        return self.__get_data_list(reference_type)

    def __create_nomenclature_from_data(self, data: dict) -> nomenclature_model:
        """Создает номенклатуру из данных"""
        name = data.get("name", "")
        group_id = data.get("group_id")
        range_id = data.get("range_id")
        
        # Находим связанные объекты
        group = self.find_by_id("group", group_id) if group_id else None
        range_obj = self.find_by_id("range", range_id) if range_id else None
        
        if not group:
            raise operation_exception("Группа не найдена")
        if not range_obj:
            raise operation_exception("Единица измерения не найдена")
        
        return nomenclature_model.create(name, group, range_obj)

    def __create_range_from_data(self, data: dict) -> range_model:
        """Создает единицу измерения из данных"""
        name = data.get("name", "")
        value = data.get("value", 1)
        base_id = data.get("base_id")
        
        base = self.find_by_id("range", base_id) if base_id else None
        
        return range_model.create(name, value, base)

    def __update_nomenclature(self, item: nomenclature_model, data: dict):
        """Обновляет номенклатуру"""
        if "name" in data:
            item.name = data["name"]
        if "group_id" in data:
            group = self.find_by_id("group", data["group_id"])
            if group:
                item.group = group
        if "range_id" in data:
            range_obj = self.find_by_id("range", data["range_id"])
            if range_obj:
                item.range = range_obj

    def __update_range(self, item: range_model, data: dict):
        """Обновляет единицу измерения"""
        if "name" in data:
            item.name = data["name"]
        if "value" in data:
            item.value = data["value"]
        if "base_id" in data:
            base = self.find_by_id("range", data["base_id"]) if data["base_id"] else None
            item.base = base
