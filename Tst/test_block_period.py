import unittest
from datetime import datetime
from Src.Logics.turnover_service import turnover_service
from Src.Logics.balance_service import balance_service
from Src.Models.settings_model import settings_model
from Src.reposity import reposity
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.storage_model import storage_model
from Src.Models.transaction_model import transaction_model
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model

class test_block_period(unittest.TestCase):

    # Проверить создание сервиса расчета оборотов
    # Сервис должен создаться без исключений
    def test_notThrow_turnover_service_create(self):
        # Подготовка
        repo = reposity()
        repo.initalize()

        # Действие
        service = turnover_service(repo)

        # Проверки
        assert service is not None

    # Проверить расчет оборотов до даты блокировки
    # Расчет должен завершиться успешно
    def test_notThrow_calculate_turnovers_to_block_period(self):
        # Подготовка
        repo = reposity()
        repo.initalize()
        service = turnover_service(repo)
        block_period = datetime(2024, 7, 1)

        # Действие
        result = service.calculate_turnovers_to_block_period(block_period)

        # Проверки
        assert result == True

    # Проверить получение кэшированных оборотов
    # Должны вернуться данные после расчета
    def test_notNone_get_cached_turnovers(self):
        # Подготовка
        repo = reposity()
        repo.initalize()
        service = turnover_service(repo)
        block_period = datetime(2024, 7, 1)
        service.calculate_turnovers_to_block_period(block_period)

        # Действие
        cached_turnovers = service.get_cached_turnovers(block_period)

        # Проверки
        assert cached_turnovers is not None
        assert len(cached_turnovers) > 0

    # Проверить неизменность результата при смене даты блокировки
    # Итоговые остатки должны быть одинаковыми
    def test_consistency_balance_with_block_period_change(self):
        # Подготовка
        repo = reposity()
        repo.initalize()
        
        storage = storage_model.create("Тестовый склад", "ул. Тестовая, 1")
        group = group_model.create("Тестовая группа")
        range_gram = range_model()
        range_gram.name = "грамм"
        range_gram.value = 1
        nomenclature = nomenclature_model.create("Тестовая номенклатура", group, range_gram)
        
        transaction1 = transaction_model.create(
            datetime(2024, 1, 1), nomenclature, storage, 100.0, "г"
        )
        transaction2 = transaction_model.create(
            datetime(2024, 6, 1), nomenclature, storage, -50.0, "г"
        )
        transaction3 = transaction_model.create(
            datetime(2024, 9, 1), nomenclature, storage, 200.0, "г"
        )
        
        repo.data[reposity.storage_key()] = [storage]
        repo.data[reposity.nomenclature_key()] = [nomenclature]
        repo.data[reposity.transaction_key()] = [transaction1, transaction2, transaction3]
        
        settings = settings_model()
        turnover_service_instance = turnover_service(repo)
        balance_service_instance = balance_service(repo, settings)
        target_date = datetime(2024, 10, 1)

        # Действие - первый расчет
        settings.block_period = datetime(2024, 7, 1)
        turnover_service_instance.calculate_turnovers_to_block_period(settings.block_period)
        balance1 = balance_service_instance.calculate_balance_with_block_period(target_date)

        # Действие - второй расчет с другой датой блокировки
        settings.block_period = datetime(2024, 5, 1)
        turnover_service_instance.calculate_turnovers_to_block_period(settings.block_period)
        balance2 = balance_service_instance.calculate_balance_with_block_period(target_date)

        # Проверки
        assert len(balance1) == len(balance2)
        if len(balance1) > 0 and len(balance2) > 0:
            assert balance1[0]['end_balance'] == balance2[0]['end_balance']

    # Проверить расчет оборотов за период
    # Должен вернуться список оборотов
    def test_notThrow_calculate_turnovers_for_period(self):
        # Подготовка
        repo = reposity()
        repo.initalize()
        service = turnover_service(repo)
        start_date = datetime(2024, 7, 1)
        end_date = datetime(2024, 9, 1)

        # Действие
        result = service.calculate_turnovers_for_period(start_date, end_date)

        # Проверки
        assert result is not None
        assert isinstance(result, list)

    # Проверить корректность расчета оборотов
    # Дебетовый и кредитовый обороты должны быть правильными
    def test_correctness_turnover_calculation(self):
        # Подготовка
        repo = reposity()
        repo.initalize()
        
        storage = storage_model.create("Тестовый склад", "ул. Тестовая, 1")
        group = group_model.create("Тестовая группа")
        range_gram = range_model()
        range_gram.name = "грамм"
        range_gram.value = 1
        nomenclature = nomenclature_model.create("Тестовая номенклатура", group, range_gram)
        
        transaction1 = transaction_model.create(
            datetime(2024, 1, 1), nomenclature, storage, 100.0, "г"
        )
        transaction2 = transaction_model.create(
            datetime(2024, 6, 1), nomenclature, storage, -50.0, "г"
        )
        
        repo.data[reposity.storage_key()] = [storage]
        repo.data[reposity.nomenclature_key()] = [nomenclature]
        repo.data[reposity.transaction_key()] = [transaction1, transaction2]
        
        service = turnover_service(repo)
        block_period = datetime(2024, 7, 1)

        # Действие
        service.calculate_turnovers_to_block_period(block_period)
        cached_turnovers = service.get_cached_turnovers(block_period)

        # Проверки
        if cached_turnovers:
            cache_item = cached_turnovers[0]
            assert cache_item.debit_turnover == 100.0
            assert cache_item.credit_turnover == 50.0

    # Проверить расчет остатков без установленной даты блокировки
    # Должен работать обычный расчет
    def test_notThrow_balance_without_block_period(self):
        # Подготовка
        repo = reposity()
        repo.initalize()
        settings = settings_model()
        settings.block_period = None
        balance_service_instance = balance_service(repo, settings)
        target_date = datetime(2024, 10, 1)

        # Действие
        balances = balance_service_instance.calculate_balance_with_block_period(target_date)

        # Проверки
        assert balances is not None
        assert isinstance(balances, list)

    # Проверить сохранение и загрузку оборотов из файла
    # Данные должны сохраняться и загружаться корректно
    def test_save_and_load_turnovers(self):
        # Подготовка
        repo = reposity()
        repo.initalize()
        service = turnover_service(repo)
        block_period = datetime(2024, 7, 1)
        service.calculate_turnovers_to_block_period(block_period)

        # Действие - сохранение
        save_result = service.save_turnovers_to_file("test_turnovers.json")

        # Действие - загрузка
        new_repo = reposity()
        new_repo.initalize()
        new_service = turnover_service(new_repo)
        load_result = new_service.load_turnovers_from_file("test_turnovers.json")

        # Проверки
        assert save_result == True
        assert load_result == True
        
        loaded_turnovers = new_service.get_cached_turnovers(block_period)
        assert len(loaded_turnovers) > 0

if __name__ == '__main__':
    unittest.main()
