import unittest
import os
import tempfile
from Src.Logics.export_service import export_service
from Src.reposity import reposity
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.storage_model import storage_model
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model

"""
Набор тестов для сервиса экспорта данных
"""
class test_export(unittest.TestCase):

    def test_notThrow_export_all_data(self):
        """
        Проверяет экспорт всех данных без исключений
        """
        repo = reposity()
        repo.initalize()

        storage = storage_model.create("Тестовый склад", "ул. Тестовая, 1")
        group = group_model.create("Тестовая группа")
        range_gram = range_model()
        range_gram.name = "грамм"
        range_gram.value = 1
        nomenclature = nomenclature_model.create("Тестовая номенклатура", group, range_gram)

        repo.data[reposity.storage_key()] = [storage]
        repo.data[reposity.nomenclature_key()] = [nomenclature]

        service = export_service(repo)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            result = service.export_all_data(temp_path)

            assert result is True
            assert os.path.exists(temp_path)
            assert os.path.getsize(temp_path) > 0

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

if __name__ == '__main__':
    unittest.main()
