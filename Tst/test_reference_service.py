import unittest
from Src.Logics.reference_service import reference_service
from Src.Logics.delete_validation_handler import delete_validation_handler
from Src.reposity import reposity
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model
from Src.Models.storage_model import storage_model
from Src.Models.receipt_model import receipt_model
from Src.Models.receipt_item_model import receipt_item_model
from Src.Models.transaction_model import transaction_model
from datetime import datetime

class test_reference_service(unittest.TestCase):

    def setUp(self):
        """Подготовка тестовых данных"""
        self.repo = reposity()
        self.repo.initalize()
        
        # Создаем тестовые данные
        self.group = group_model.create("Тестовая группа")
        self.group.unique_code = "test_group_1"
        
        self.range_gram = range_model.create("Грамм", 1, None)
        self.range_gram.unique_code = "test_range_1"
        
        self.range_kg = range_model.create("Килограмм", 1000, self.range_gram)
        self.range_kg.unique_code = "test_range_2"
        
        self.nomenclature = nomenclature_model.create("Тестовая номенклатура", self.group, self.range_kg)
        self.nomenclature.unique_code = "test_nom_1"
        
        self.storage = storage_model.create("Тестовый склад", "ул. Тестовая, 1")
        self.storage.unique_code = "test_storage_1"
        
        # Добавляем в репозиторий
        self.repo.data[reposity.group_key()] = [self.group]
        self.repo.data[reposity.range_key()] = [self.range_gram, self.range_kg]
        self.repo.data[reposity.nomenclature_key()] = [self.nomenclature]
        self.repo.data[reposity.storage_key()] = [self.storage]
        
        self.service = reference_service(self.repo)

    # Проверить создание reference_service без исключений
    def test_notThrow_reference_service_create(self):
        # Подготовка

        # Действие
        service = reference_service(self.repo)

        # Проверка
        assert service is not None

    # Проверить добавление элемента в справочник групп
    def test_notThrow_add_reference_item(self):
        # Подготовка
        data = {
            "name": "Новая группа"
        }
        
        # Действие
        item = self.service.add("group", data)

        # Проверка
        assert item is not None
        assert item.name == "Новая группа"

    # Проверить получение элемента справочника по ID
    def test_notThrow_get_reference_item(self):
        # Подготовка

        # Действие
        item = self.service.get("group", "test_group_1")

        # Проверка
        assert item is not None
        assert item.name == "Тестовая группа"

    # Проверить обновление элемента справочника
    def test_notThrow_update_reference_item(self):
        # Подготовка
        update_data = {
            "name": "Обновленная группа"
        }
        
        # Действие
        success = self.service.update("group", "test_group_1", update_data)

        # Проверка
        assert success == True
        
        updated_item = self.service.get("group", "test_group_1")
        assert updated_item.name == "Обновленная группа"

    # Проверить блокировку удаления используемой номенклатуры
    def test_throw_delete_used_nomenclature(self):
        # Подготовка
        receipt = receipt_model.create("Тестовый рецепт", "30 мин", 2)
        receipt_item = receipt_item_model.create(self.nomenclature, self.range_gram, 100)
        receipt.composition.append(receipt_item)
        
        self.repo.data[reposity.receipt_key()] = [receipt]
        
        from Src.Core.event_manager import event_manager
        from Src.Core.event_types import event_types
        
        delete_handler = delete_validation_handler(self.repo)
        event_manager.subscribe(
            event_types.BEFORE_DELETE_NOMENCLATURE,
            lambda item_id: delete_handler.check_nomenclature_usage(item_id)
        )
        
        # Действие
        success = self.service.delete("nomenclature", "test_nom_1")

        # Проверка
        assert success == False

    # Проверить удаление неиспользуемого элемента
    def test_notThrow_delete_unused_item(self):
        # Подготовка
        data = {
            "name": "Группа для удаления"
        }
        item = self.service.add("group", data)
        
        from Src.Core.event_manager import event_manager
        from Src.Core.event_types import event_types
        
        delete_handler = delete_validation_handler(self.repo)
        event_manager.subscribe(
            event_types.BEFORE_DELETE_GROUP,
            lambda item_id: delete_handler.check_group_usage(item_id)
        )
        
        # Действие
        success = self.service.delete("group", item.unique_code)

        # Проверка
        assert success == True

if __name__ == '__main__':
    unittest.main()
