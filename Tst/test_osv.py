import unittest
from datetime import datetime
from Src.Logics.osv_service import osv_service
from Src.reposity import reposity
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.storage_model import storage_model
from Src.Models.transaction_model import transaction_model
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model

"""
Набор тестов для сервиса оборотно-сальдовой ведомости
"""
class test_osv(unittest.TestCase):

    def test_notThrow_osv_report_generation(self):
        """
        Проверяет формирование отчета ОСВ без исключений
        """
        repo = reposity()
        repo.initalize()

        storage = storage_model.create("Главный склад", "ул. Тестовая, 1")
        group = group_model.create("Ингредиенты")
        range_gram = range_model()
        range_gram.name = "грамм"
        range_gram.value = 1
        nomenclature = nomenclature_model.create("Мука", group, range_gram)

        transaction1 = transaction_model.create(
            datetime(2024, 10, 1), nomenclature, storage, 100.0, "г"
        )
        transaction2 = transaction_model.create(
            datetime(2024, 10, 15), nomenclature, storage, -50.0, "г"
        )

        repo.data[reposity.storage_key()] = [storage]
        repo.data[reposity.nomenclature_key()] = [nomenclature]
        repo.data[reposity.transaction_key()] = [transaction1, transaction2]

        service = osv_service(repo)

        report = service.generate_osv_report(
            datetime(2024, 10, 10),
            datetime(2024, 10, 20),
            storage.unique_code
        )

        assert len(report) > 0
        assert report[0]["nomenclature_name"] == "Мука"
        assert report[0]["unit_measurement"] == "грамм"
        assert report[0]["start_balance"] == 100.0
        assert report[0]["income"] == 0.0
        assert report[0]["outcome"] == 50.0
        assert report[0]["end_balance"] == 50.0

    def test_notNone_osv_with_new_nomenclature(self):
        """
        Проверяет что ОСВ включает новые номенклатуры
        """
        repo = reposity()
        repo.initalize()

        storage = storage_model.create("Главный склад", "ул. Тестовая, 1")
        group = group_model.create("Ингредиенты")
        range_gram = range_model()
        range_gram.name = "грамм"
        range_gram.value = 1
        nomenclature = nomenclature_model.create("Новая номенклатура", group, range_gram)

        repo.data[reposity.storage_key()] = [storage]
        repo.data[reposity.nomenclature_key()] = [nomenclature]
        repo.data[reposity.transaction_key()] = []

        service = osv_service(repo)

        report = service.generate_osv_report(
            datetime(2024, 10, 1),
            datetime(2024, 10, 31),
            storage.unique_code
        )

        assert len(report) == 1
        assert report[0]["nomenclature_name"] == "Новая номенклатура"
        assert report[0]["unit_measurement"] == "грамм"
        assert report[0]["start_balance"] == 0.0
        assert report[0]["income"] == 0.0
        assert report[0]["outcome"] == 0.0
        assert report[0]["end_balance"] == 0.0

if __name__ == '__main__':
    unittest.main()
