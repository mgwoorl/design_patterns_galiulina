from Src.Core.validator import validator, operation_exception
from Src.reposity import reposity
from Src.Models.receipt_model import receipt_model
from Src.Models.transaction_model import transaction_model

"""
Обработчик для проверки возможности удаления
"""
class delete_validation_handler:
    
    def __init__(self, repo: reposity):
        self.__repo = repo

    def check_nomenclature_usage(self, nomenclature_id: str):
        """Проверяет использование номенклатуры"""
        # Проверка в рецептах
        receipts = self.__repo.data.get(reposity.receipt_key(), [])
        for receipt in receipts:
            for composition_item in receipt.composition:
                if (hasattr(composition_item, 'nomenclature') and 
                    composition_item.nomenclature.unique_code == nomenclature_id):
                    raise operation_exception(
                        f"Номенклатура используется в рецепте '{receipt.name}'"
                    )

        # Проверка в транзакциях
        transactions = self.__repo.data.get(reposity.transaction_key(), [])
        for transaction in transactions:
            if (hasattr(transaction, 'nomenclature') and 
                transaction.nomenclature.unique_code == nomenclature_id):
                raise operation_exception(
                    "Номенклатура используется в транзакциях"
                )

    def check_group_usage(self, group_id: str):
        """Проверяет использование группы"""
        nomenclatures = self.__repo.data.get(reposity.nomenclature_key(), [])
        for nomenclature in nomenclatures:
            if (hasattr(nomenclature, 'group') and 
                nomenclature.group and 
                nomenclature.group.unique_code == group_id):
                raise operation_exception(
                    f"Группа используется в номенклатуре '{nomenclature.name}'"
                )

    def check_range_usage(self, range_id: str):
        """Проверяет использование единицы измерения"""
        # Проверка в номенклатурах
        nomenclatures = self.__repo.data.get(reposity.nomenclature_key(), [])
        for nomenclature in nomenclatures:
            if (hasattr(nomenclature, 'range') and 
                nomenclature.range and 
                nomenclature.range.unique_code == range_id):
                raise operation_exception(
                    f"Единица измерения используется в номенклатуре '{nomenclature.name}'"
                )

        # Проверка в других единицах измерения как базовой
        ranges = self.__repo.data.get(reposity.range_key(), [])
        for range_item in ranges:
            if (hasattr(range_item, 'base') and 
                range_item.base and 
                range_item.base.unique_code == range_id):
                raise operation_exception(
                    f"Единица измерения используется как базовая для '{range_item.name}'"
                )

    def check_storage_usage(self, storage_id: str):
        """Проверяет использование склада"""
        transactions = self.__repo.data.get(reposity.transaction_key(), [])
        for transaction in transactions:
            if (hasattr(transaction, 'storage') and 
                transaction.storage.unique_code == storage_id):
                raise operation_exception(
                    "Склад используется в транзакциях"
                )
