import unittest
import time
from datetime import datetime, timedelta
import random
from Src.Logics.turnover_service import turnover_service
from Src.Logics.balance_service import balance_service
from Src.Models.settings_model import settings_model
from Src.reposity import reposity
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.storage_model import storage_model
from Src.Models.transaction_model import transaction_model
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model

class test_performance(unittest.TestCase):

    # Проверить производительность с разными датами блокировки
    # Время выполнения не должно превышать лимит
    def test_performance_different_block_periods(self):
        # Подготовка
        repo = reposity()
        repo.initalize()
        
        storage = storage_model.create("Главный склад", "ул. Тестовая, 1")
        group = group_model.create("Тестовая группа")
        range_gram = range_model()
        range_gram.name = "грамм"
        range_gram.value = 1
        
        nomenclatures = []
        for i in range(10):
            nom = nomenclature_model.create(f"Номенклатура {i}", group, range_gram)
            nomenclatures.append(nom)
        
        transactions = []
        start_date = datetime(2023, 1, 1)
        
        for i in range(1000):
            nom = random.choice(nomenclatures)
            days_offset = random.randint(0, 365)
            transaction_date = start_date + timedelta(days=days_offset)
            quantity = random.uniform(-100, 100)
            
            transaction = transaction_model.create(
                transaction_date, nom, storage, quantity, "г"
            )
            transactions.append(transaction)
        
        repo.data[reposity.storage_key()] = [storage]
        repo.data[reposity.nomenclature_key()] = nomenclatures
        repo.data[reposity.transaction_key()] = transactions
        
        settings = settings_model()
        turnover_service_instance = turnover_service(repo)
        balance_service_instance = balance_service(repo, settings)
        target_date = datetime(2024, 1, 1)
        block_periods = [
            datetime(2023, 3, 1),
            datetime(2023, 6, 1),
            datetime(2023, 9, 1),
            datetime(2023, 12, 1)
        ]
        
        results = []

        # Действие - тестирование для каждой даты блокировки
        for block_period in block_periods:
            start_time = time.time()
            
            settings.block_period = block_period
            turnover_service_instance.calculate_turnovers_to_block_period(block_period)
            balances = balance_service_instance.calculate_balance_with_block_period(target_date)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            results.append({
                'block_period': block_period.isoformat(),
                'execution_time': execution_time,
                'balances_count': len(balances)
            })

        # Проверки
        for result in results:
            assert result['execution_time'] < 10.0
            assert result['balances_count'] > 0

        # Сохранение результатов
        markdown_result = "# Результаты нагрузочного теста\n\n"
        markdown_result += "| Дата блокировки | Время выполнения (сек) | Количество остатков |\n"
        markdown_result += "|-----------------|------------------------|---------------------|\n"
        
        for result in results:
            markdown_result += f"| {result['block_period']} | {result['execution_time']:.3f} | {result['balances_count']} |\n"
        
        with open("performance_results.md", "w", encoding="utf-8") as f:
            f.write(markdown_result)

    # Проверить производительность с большим набором данных
    # Время выполнения должно быть в разумных пределах
    def test_performance_large_dataset(self):
        # Подготовка
        repo = reposity()
        repo.initalize()
        
        storage = storage_model.create("Главный склад", "ул. Тестовая, 1")
        group = group_model.create("Тестовая группа")
        range_gram = range_model()
        range_gram.name = "грамм"
        range_gram.value = 1
        
        nomenclatures = []
        for i in range(10):
            nom = nomenclature_model.create(f"Номенклатура {i}", group, range_gram)
            nomenclatures.append(nom)
        
        transactions = []
        start_date = datetime(2023, 1, 1)
        
        for i in range(1500):
            nom = random.choice(nomenclatures)
            days_offset = random.randint(0, 365)
            transaction_date = start_date + timedelta(days=days_offset)
            quantity = random.uniform(-100, 100)
            
            transaction = transaction_model.create(
                transaction_date, nom, storage, quantity, "г"
            )
            transactions.append(transaction)
        
        repo.data[reposity.storage_key()] = [storage]
        repo.data[reposity.nomenclature_key()] = nomenclatures
        repo.data[reposity.transaction_key()] = transactions
        
        settings = settings_model()
        turnover_service_instance = turnover_service(repo)
        balance_service_instance = balance_service(repo, settings)
        block_period = datetime(2023, 6, 1)
        target_date = datetime(2024, 1, 1)

        # Действие
        start_time = time.time()
        
        settings.block_period = block_period
        turnover_service_instance.calculate_turnovers_to_block_period(block_period)
        balances = balance_service_instance.calculate_balance_with_block_period(target_date)
        
        end_time = time.time()
        execution_time = end_time - start_time

        # Проверки
        assert execution_time < 15.0
        assert len(balances) == len(nomenclatures)

    # Проверить производительность с использованием кэшированных данных
    # Расчет с кэшем должен быть быстрее
    def test_performance_with_cached_data(self):
        # Подготовка
        repo = reposity()
        repo.initalize()
        
        storage = storage_model.create("Главный склад", "ул. Тестовая, 1")
        group = group_model.create("Тестовая группа")
        range_gram = range_model()
        range_gram.name = "грамм"
        range_gram.value = 1
        
        nomenclatures = []
        for i in range(5):
            nom = nomenclature_model.create(f"Номенклатура {i}", group, range_gram)
            nomenclatures.append(nom)
        
        transactions = []
        start_date = datetime(2023, 1, 1)
        
        for i in range(500):
            nom = random.choice(nomenclatures)
            days_offset = random.randint(0, 365)
            transaction_date = start_date + timedelta(days=days_offset)
            quantity = random.uniform(-50, 50)
            
            transaction = transaction_model.create(
                transaction_date, nom, storage, quantity, "г"
            )
            transactions.append(transaction)
        
        repo.data[reposity.storage_key()] = [storage]
        repo.data[reposity.nomenclature_key()] = nomenclatures
        repo.data[reposity.transaction_key()] = transactions
        
        settings = settings_model()
        turnover_service_instance = turnover_service(repo)
        balance_service_instance = balance_service(repo, settings)
        target_date = datetime(2024, 1, 1)
        block_period = datetime(2023, 6, 1)

        # Действие - первый расчет с расчетом оборотов
        start_time1 = time.time()
        settings.block_period = block_period
        turnover_service_instance.calculate_turnovers_to_block_period(block_period)
        balances1 = balance_service_instance.calculate_balance_with_block_period(target_date)
        end_time1 = time.time()
        time_with_calculation = end_time1 - start_time1

        # Действие - второй расчет с использованием кэша
        start_time2 = time.time()
        balances2 = balance_service_instance.calculate_balance_with_block_period(target_date)
        end_time2 = time.time()
        time_with_cache = end_time2 - start_time2

        # Проверки
        assert time_with_cache < time_with_calculation
        assert len(balances1) == len(balances2)

if __name__ == '__main__':
    unittest.main()
