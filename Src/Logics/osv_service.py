from Src.reposity import reposity
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from datetime import datetime
from Src.Core.validator import validator, operation_exception

"""
Сервис для формирования оборотно-сальдовой ведомости
"""
class osv_service:
    __repo: reposity

    def __init__(self, repository: reposity):
        self.__repo = repository

    def generate_osv_report(self, start_date: datetime, end_date: datetime, storage_id: str) -> list:
        """
        Генерирует оборотно-сальдовую ведомость
        """
        validator.validate(start_date, datetime)
        validator.validate(end_date, datetime)
        validator.validate(storage_id, str)

        if start_date > end_date:
            raise operation_exception("Дата начала не может быть позже даты окончания")

        transactions = self.__repo.data.get(reposity.transaction_key(), [])
        nomenclatures = self.__repo.data.get(reposity.nomenclature_key(), [])
        storages = self.__repo.data.get(reposity.storage_key(), [])

        storage = next((s for s in storages if s.unique_code == storage_id), None)
        if not storage:
            raise operation_exception(f"Склад с ID {storage_id} не найден")

        result = []

        for nomenclature in nomenclatures:
            nom_transactions = [t for t in transactions 
                              if t.nomenclature.unique_code == nomenclature.unique_code 
                              and t.storage.unique_code == storage_id]

            start_balance = sum(self.__convert_to_base_units(t) 
                               for t in nom_transactions 
                               if t.date < start_date)

            income = sum(self.__convert_to_base_units(t) 
                        for t in nom_transactions 
                        if start_date <= t.date <= end_date and t.quantity > 0)

            outcome = sum(abs(self.__convert_to_base_units(t))
                         for t in nom_transactions 
                         if start_date <= t.date <= end_date and t.quantity < 0)

            end_balance = start_balance + income - outcome

            if nomenclature.range:
                display_start_balance = self.__convert_from_base_units(start_balance, nomenclature.range)
                display_income = self.__convert_from_base_units(income, nomenclature.range)
                display_outcome = self.__convert_from_base_units(outcome, nomenclature.range)
                display_end_balance = self.__convert_from_base_units(end_balance, nomenclature.range)
            else:
                display_start_balance = start_balance
                display_income = income
                display_outcome = outcome
                display_end_balance = end_balance

            report_item = {
                "nomenclature_name": nomenclature.name,
                "unit_measurement": nomenclature.range.name if nomenclature.range else "шт",
                "start_balance": round(display_start_balance, 3),
                "income": round(display_income, 3),
                "outcome": round(display_outcome, 3),
                "end_balance": round(display_end_balance, 3)
            }

            result.append(report_item)

        return result

    def __convert_to_base_units(self, transaction) -> float:
        """
        Конвертирует количество транзакции в базовые единицы
        """
        if not transaction.nomenclature or not transaction.nomenclature.range:
            return transaction.quantity

        range_obj = transaction.nomenclature.range
        return range_obj.convert_to_root_base_unit(transaction.quantity)

    def __convert_from_base_units(self, quantity: float, range_obj: range_model) -> float:
        """
        Конвертирует количество из базовых единиц обратно в единицы номенклатуры
        """
        if range_obj.base is None:
            return quantity
        
        base_unit = range_obj.root_base_unit()
        if base_unit == range_obj:
            return quantity
        
        current = range_obj
        conversion_rate = 1.0
        
        while current.base is not None:
            conversion_rate *= current.value
            current = current.base
            
        return quantity / conversion_rate
