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

            start_balance = sum(self.__convert_to_base_units(t.quantity, t.unit, t.nomenclature.range) 
                               for t in nom_transactions 
                               if t.date < start_date)

            income = sum(self.__convert_to_base_units(t.quantity, t.unit, t.nomenclature.range) 
                        for t in nom_transactions 
                        if start_date <= t.date <= end_date and t.quantity > 0)

            outcome = sum(abs(self.__convert_to_base_units(t.quantity, t.unit, t.nomenclature.range))
                         for t in nom_transactions 
                         if start_date <= t.date <= end_date and t.quantity < 0)

            end_balance = start_balance + income - outcome

            report_item = {
                "nomenclature_name": nomenclature.name,
                "unit_measurement": nomenclature.range.name if nomenclature.range else "шт",
                "start_balance": round(start_balance, 2),
                "income": round(income, 2),
                "outcome": round(outcome, 2),
                "end_balance": round(end_balance, 2)
            }

            result.append(report_item)

        return result

    def __convert_to_base_units(self, quantity: float, unit: str, range_obj: range_model) -> float:
        """
        Конвертирует количество в базовые единицы измерения
        """
        if not range_obj:
            return quantity

        if range_obj.base:
            return quantity * range_obj.value
        else:
            return quantity

        for nomenclature in nomenclatures:
            nom_transactions = [t for t in transactions 
                              if t.nomenclature.unique_code == nomenclature.unique_code 
                              and t.storage.unique_code == storage_id]

            start_balance = sum(self.__convert_to_base_units(t.quantity, t.unit, t.nomenclature.range) 
                               for t in nom_transactions 
                               if t.date < start_date)

            income = sum(self.__convert_to_base_units(t.quantity, t.unit, t.nomenclature.range) 
                        for t in nom_transactions 
                        if start_date <= t.date <= end_date and t.quantity > 0)

            outcome = sum(abs(self.__convert_to_base_units(t.quantity, t.unit, t.nomenclature.range))
                         for t in nom_transactions 
                         if start_date <= t.date <= end_date and t.quantity < 0)

            end_balance = start_balance + income - outcome

            report_item = {
                "nomenclature_name": nomenclature.name,
                "unit_name": nomenclature.range.name if nomenclature.range else "шт",
                "start_balance": round(start_balance, 2),
                "income": round(income, 2),
                "outcome": round(outcome, 2),
                "end_balance": round(end_balance, 2)
            }

            result.append(report_item)

        return result

    def __convert_to_base_units(self, quantity: float, unit: str, range_obj: range_model) -> float:
        if not range_obj:
            return quantity

        if range_obj.base:
            return quantity * range_obj.value
        else:
            return quantity
