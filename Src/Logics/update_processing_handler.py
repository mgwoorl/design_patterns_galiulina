from Src.Core.validator import validator
from Src.reposity import reposity

"""
Обработчик для пост-обработки обновлений
"""
class update_processing_handler:
    
    def __init__(self, repo: reposity):
        self.__repo = repo

    def process_nomenclature_update(self, nomenclature):
        """Обрабатывает обновление номенклатуры"""
        # Обновляем свойства в рецептах
        receipts = self.__repo.data.get(reposity.receipt_key(), [])
        for receipt in receipts:
            for composition_item in receipt.composition:
                if (hasattr(composition_item, 'nomenclature') and 
                    composition_item.nomenclature.unique_code == nomenclature.unique_code):
                    composition_item.nomenclature = nomenclature

        # Обновляем свойства в транзакциях
        transactions = self.__repo.data.get(reposity.transaction_key(), [])
        for transaction in transactions:
            if (hasattr(transaction, 'nomenclature') and 
                transaction.nomenclature.unique_code == nomenclature.unique_code):
                transaction.nomenclature = nomenclature

    def process_range_update(self, range_item):
        """Обрабатывает обновление единицы измерения"""
        # Обновляем в номенклатурах
        nomenclatures = self.__repo.data.get(reposity.nomenclature_key(), [])
        for nomenclature in nomenclatures:
            if (hasattr(nomenclature, 'range') and 
                nomenclature.range and 
                nomenclature.range.unique_code == range_item.unique_code):
                nomenclature.range = range_item

        # Обновляем в других единицах измерения
        ranges = self.__repo.data.get(reposity.range_key(), [])
        for range_obj in ranges:
            if (hasattr(range_obj, 'base') and 
                range_obj.base and 
                range_obj.base.unique_code == range_item.unique_code):
                range_obj.base = range_item
