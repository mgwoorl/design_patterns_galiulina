from Src.reposity import reposity
from Src.Logics.turnover_service import turnover_service
from Src.Models.settings_model import settings_model
from Src.Core.validator import validator, operation_exception, argument_exception
from datetime import datetime

"""
Сервис для расчета остатков с учетом даты блокировки
"""
class balance_service:
    __repo: reposity = None
    __turnover_service: turnover_service = None
    __settings: settings_model = None

    def __init__(self, data: reposity, settings: settings_model):
        if not isinstance(data, reposity):
            raise argument_exception("Некорректный тип данных")
        if not isinstance(settings, settings_model):
            raise argument_exception("Некорректный тип настроек")
            
        self.__repo = data
        self.__settings = settings
        self.__turnover_service = turnover_service(data)

    def calculate_balance_with_block_period(self, target_date: datetime, storage_id: str = None) -> list:
        """
        Расчет остатков на указанную дату с учетом даты блокировки
        
        Args:
            target_date (datetime): целевая дата для расчета остатков
            storage_id (str): ID склада (опционально)
            
        Returns:
            list: данные остатков
        """
        validator.validate(target_date, datetime)
        
        block_period = self.__settings.block_period
        
        if block_period is None:
            # Если дата блокировки не установлена, рассчитываем обычным способом
            return self._calculate_balance_simple(target_date, storage_id)
        
        # Проверяем, что целевая дата не раньше даты блокировки
        if target_date < block_period:
            raise operation_exception("Целевая дата не может быть раньше даты блокировки")
        
        # Получаем кэшированные обороты до даты блокировки
        cached_turnovers = self.__turnover_service.get_cached_turnovers(block_period)
        
        # Если кэш отсутствует, рассчитываем его
        if not cached_turnovers:
            self.__turnover_service.calculate_turnovers_to_block_period(block_period)
            cached_turnovers = self.__turnover_service.get_cached_turnovers(block_period)
        
        # Рассчитываем обороты с даты блокировки до целевой даты
        recent_turnovers = self.__turnover_service.calculate_turnovers_for_period(
            block_period, target_date
        )
        
        # Объединяем и группируем результаты
        return self._merge_and_group_turnovers(cached_turnovers, recent_turnovers, storage_id)

    def _calculate_balance_simple(self, target_date: datetime, storage_id: str = None) -> list:
        """
        Простой расчет остатков без использования блокировки
        
        Args:
            target_date (datetime): целевая дата
            storage_id (str): ID склада (опционально)
            
        Returns:
            list: данные остатков
        """
        transactions = self.__repo.data.get(reposity.transaction_key(), [])
        nomenclatures = self.__repo.data.get(reposity.nomenclature_key(), [])
        storages = self.__repo.data.get(reposity.storage_key(), [])
        
        result = []
        
        for nomenclature in nomenclatures:
            storage_filter = storages
            if storage_id:
                storage_filter = [s for s in storages if s.unique_code == storage_id]
                if not storage_filter:
                    continue
            
            for storage in storage_filter:
                # Фильтруем транзакции по номенклатуре, складу и дате
                nom_transactions = [
                    t for t in transactions
                    if t.nomenclature.unique_code == nomenclature.unique_code
                    and t.storage.unique_code == storage.unique_code
                    and t.date <= target_date
                ]
                
                # Рассчитываем баланс
                balance = sum(t.quantity for t in nom_transactions)
                
                result.append({
                    "nomenclature_id": nomenclature.unique_code,
                    "nomenclature_name": nomenclature.name,
                    "storage_id": storage.unique_code,
                    "storage_name": storage.name,
                    "balance": balance,
                    "calculation_date": target_date
                })
        
        return result

    def _merge_and_group_turnovers(self, cached_turnovers: list, recent_turnovers: list, storage_id: str = None) -> list:
        """
        Объединение и группировка кэшированных и свежих оборотов
        
        Args:
            cached_turnovers (list): кэшированные обороты
            recent_turnovers (list): свежие обороты
            storage_id (str): ID склада (опционально)
            
        Returns:
            list: объединенные данные остатков
        """
        nomenclatures = self.__repo.data.get(reposity.nomenclature_key(), [])
        storages = self.__repo.data.get(reposity.storage_key(), [])
        
        result = []
        
        for nomenclature in nomenclatures:
            storage_filter = storages
            if storage_id:
                storage_filter = [s for s in storages if s.unique_code == storage_id]
                if not storage_filter:
                    continue
            
            for storage in storage_filter:
                # Находим кэшированные обороты
                cached_item = next(
                    (item for item in cached_turnovers 
                     if item.nomenclature_id == nomenclature.unique_code 
                     and item.storage_id == storage.unique_code),
                    None
                )
                
                # Находим свежие обороты
                recent_item = next(
                    (item for item in recent_turnovers 
                     if item['nomenclature_id'] == nomenclature.unique_code 
                     and item['storage_id'] == storage.unique_code),
                    None
                )
                
                # Рассчитываем итоговый баланс
                start_balance = 0.0
                if cached_item:
                    start_balance = cached_item.debit_turnover - cached_item.credit_turnover
                
                period_debit = recent_item['debit_turnover'] if recent_item else 0.0
                period_credit = recent_item['credit_turnover'] if recent_item else 0.0
                
                end_balance = start_balance + period_debit - period_credit
                
                result.append({
                    "nomenclature_id": nomenclature.unique_code,
                    "nomenclature_name": nomenclature.name,
                    "storage_id": storage.unique_code,
                    "storage_name": storage.name,
                    "start_balance": start_balance,
                    "period_debit": period_debit,
                    "period_credit": period_credit,
                    "end_balance": end_balance,
                    "calculation_date": self.__settings.block_period
                })
        
        return result
