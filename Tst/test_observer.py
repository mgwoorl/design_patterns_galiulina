"""
Набор тестов для системы наблюдателей и сервиса справочников
"""
import unittest
from Src.start_service import start_service
from Src.Logics.reference_service import reference_service
from Src.Core.validator import operation_exception

class test_observer(unittest.TestCase):

    # Проверить добавление справочника без исключений
    # Добавление должно завершиться успешно
    def test_notThrow_add_reference(self):
        # Подготовка
        start = start_service()
        start.start()
        
        # Действие
        reference_service.add("group", {"name": "Новая группа"})
        
        # Проверки
        assert True

    # Проверить блокировку удаления при наличии зависимостей
    # Должно возникнуть исключение при попытке удаления
    def test_throw_delete_with_dependencies(self):
        # Подготовка
        start = start_service()
        start.start()
        
        nomenclatures = start.data.data.get("nomenclature_model", [])
        
        # Действие и проверки
        if nomenclatures:
            nomenclature_id = nomenclatures[0].unique_code
            
            try:
                reference_service.remove("nomenclature", {"unique_code": nomenclature_id})
                assert False, "Должно было возникнуть исключение"
            except operation_exception as e:
                assert "Отказ в удалении" in str(e)

if __name__ == '__main__':
    unittest.main()
