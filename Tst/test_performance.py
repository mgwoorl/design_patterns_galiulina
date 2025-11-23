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

    def _create_performance_data(self, repo, transaction_count=1000):
        # Подготовка
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

        for i in range(transaction_count):
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

    def _print_load_test_header(self, file):
        file.write("╔════════════════════════╤══════════════════╤══════════════════════╤══════════════╗\n")
        file.write("║ Период блокировки      │ Базовые балансы  │ Расчет на 2024-01-01 │ Период расч. ║\n")
        file.write("╠════════════════════════╪══════════════════╪══════════════════════╪══════════════╣\n")

    def _print_load_test_row(self, file, block_period, base_time, calc_time, days):
        file.write(f"║ {block_period:<22} │ {base_time:<16} │ {calc_time:<20} │ {days:<12} ║\n")

    def _print_load_test_footer(self, file):
        file.write("╚════════════════════════╧══════════════════╧══════════════════════╧══════════════╝\n")

    # Проверить производительность с разными датами блокировки
    # Время выполнения не должно превышать лимит
    def test_performance_different_block_periods(self):
        # Подготовка
        repo = reposity()
        repo.initalize()
        self._create_performance_data(repo, 1000)

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
        
        # Действие
        with open("performance_results.txt", "w", encoding="utf-8") as f:
            f.write("Нагрузочное тестирование расчета балансов\n")
            f.write("=" * 60 + "\n\n")
            self._print_load_test_header(f)

            for block_period in block_periods:
                start_time_base = time.time()
                settings.block_period = block_period
                turnover_service_instance.calculate_turnovers_to_block_period(block_period)
                end_time_base = time.time()
                base_execution_time = end_time_base - start_time_base

                start_time_calc = time.time()
                balances = balance_service_instance.calculate_balance_with_block_period(target_date)
                end_time_calc = time.time()
                calc_execution_time = end_time_calc - start_time_calc

                period_days = (target_date - block_period).days

                self._print_load_test_row(
                    f,
                    block_period.strftime("%Y-%m-%d"),
                    f"{base_execution_time:.4f} сек",
                    f"{calc_execution_time:.4f} сек",
                    f"{period_days} дней"
                )

                results.append({
                    'block_period': block_period.isoformat(),
                    'base_execution_time': base_execution_time,
                    'calc_execution_time': calc_execution_time,
                    'balances_count': len(balances),
                    'period_days': period_days
                })

            self._print_load_test_footer(f)

        # Проверки
        for result in results:
            self.assertLess(result['base_execution_time'], 10.0)
            self.assertLess(result['calc_execution_time'], 10.0)
            self.assertGreater(result['balances_count'], 0)

        self._save_results_to_file(results)

    def _save_results_to_file(self, results):
        with open("performance_results.md", "w", encoding="utf-8") as f:
            f.write("# Результаты нагрузочного тестирования\n\n")
            
            f.write("## Таблица результатов\n\n")
            f.write("| Период блокировки | Базовые балансы | Расчет на 2024-01-01 | Период расчета |\n")
            f.write("|------------------|-----------------|---------------------|----------------|\n")

            for result in results:
                f.write(f"| {result['block_period']} | {result['base_execution_time']:.4f} сек | {result['calc_execution_time']:.4f} сек | {result['period_days']} дней |\n")

            f.write("\n## Анализ производительности\n\n")
            
            avg_base_time = sum(r['base_execution_time'] for r in results) / len(results)
            avg_calc_time = sum(r['calc_execution_time'] for r in results) / len(results)
            
            f.write(f"- Среднее время базовых балансов: {avg_base_time:.4f} сек\n")
            f.write(f"- Среднее время расчета целевой даты: {avg_calc_time:.4f} сек\n")
            f.write(f"- Количество тестовых периодов: {len(results)}\n")
            f.write(f"- Общее количество транзакций: 1000\n")
            f.write("- Статус: Все тесты пройдены успешно\n")

    # Проверить производительность с большим набором данных
    # Время выполнения должно быть в разумных пределах
    def test_performance_large_dataset(self):
        # Подготовка
        repo = reposity()
        repo.initalize()
        self._create_performance_data(repo, 1500)

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
        self.assertLess(execution_time, 15.0)
        self.assertGreater(len(balances), 0)

    # Проверить производительность с использованием кэшированных данных
    # Расчет с кэшем должен быть быстрее или равен по времени
    def test_performance_with_cached_data(self):
        # Подготовка
        repo = reposity()
        repo.initalize()
        self._create_performance_data(repo, 2000)

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
        self.assertLessEqual(time_with_cache, time_with_calculation + 0.001)
        self.assertEqual(len(balances1), len(balances2))

        for i in range(len(balances1)):
            self.assertEqual(balances1[i]['end_balance'], balances2[i]['end_balance'])


if __name__ == '__main__':
    unittest.main()
