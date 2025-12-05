from Src.reposity import reposity
from Src.Logics.turnover_service import turnover_service
from Src.Models.settings_model import settings_model
from Src.Core.validator import validator, operation_exception, argument_exception
from Src.Core.observe_service import observe_service
from Src.Core.event_type import event_type
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
        
        # Логируем инициализацию сервиса
        observe_service.create_event(event_type.info(), {
            "message": "Инициализация сервиса расчета остатков",
            "service": "balance_service"
        })

    def calculate_balance_with_block_period(self, target_date: datetime, storage_id: str = None) -> list:
        """
        Расчет остатков на указанную дату с учетом даты блокировки
        
        Args:
            target_date (datetime): целевая дата для расчета остатков
            storage_id (str): ID склада
            
        Returns:
            list: данные остатков
        """
        validator.validate(target_date, datetime)
        
        # Логируем начало расчета остатков
        observe_service.create_event(event_type.info(), {
            "message": f"Расчет остатков на дату: {target_date}, склад: {storage_id if storage_id else 'все склады'}",
            "service": "balance_service"
        })
        
        block_period = self.__settings.block_period
        
        if block_period is None:
            # Если дата блокировки не установлена, рассчитываем обычным способом
            observe_service.create_event(event_type.debug(), {
                "message": "Дата блокировки не установлена, используем обычный расчет",
                "service": "balance_service"
            })
            return self._calculate_balance_simple(target_date, storage_id)
        
        # Проверяем, что целевая дата не раньше даты блокировки
        if target_date < block_period:
            error_msg = "Целевая дата не может быть раньше даты блокировки"
            observe_service.create_event(event_type.error(), {
                "message": error_msg,
                "service": "balance_service",
                "details": {
                    "target_date": target_date.isoformat(),
                    "block_period": block_period.isoformat()
                }
            })
            raise operation_exception(error_msg)
        
        observe_service.create_event(event_type.debug(), {
            "message": f"Использование даты блокировки: {block_period}",
            "service": "balance_service"
        })
        
        # Получаем кэшированные обороты до даты блокировки
        cached_turnovers = self.__turnover_service.get_cached_turnovers(block_period)
        
        # Если кэш отсутствует, рассчитываем его
        if not cached_turnovers:
            observe_service.create_event(event_type.info(), {
                "message": f"Кэш оборотов отсутствует, выполняем расчет до даты блокировки",
                "service": "balance_service"
            })
            self.__turnover_service.calculate_turnovers_to_block_period(block_period)
            cached_turnovers = self.__turnover_service.get_cached_turnovers(block_period)
        else:
            observe_service.create_event(event_type.debug(), {
                "message": f"Используется кэш оборотов: {len(cached_turnovers)} записей",
                "service": "balance_service"
            })
        
        # Рассчитываем обороты с даты блокировки до целевой даты
        observe_service.create_event(event_type.debug(), {
            "message": f"Расчет оборотов за период: {block_period} - {target_date}",
            "service": "balance_service"
        })
        
        recent_turnovers = self.__turnover_service.calculate_turnovers_for_period(
            block_period, target_date
        )
        
        observe_service.create_event(event_type.debug(), {
            "message": f"Рассчитаны обороты за период: {len(recent_turnovers)} комбинаций",
            "service": "balance_service"
        })
        
        # Объединяем и группируем результаты
        result = self._merge_and_group_turnovers(cached_turnovers, recent_turnovers, storage_id)
        
        # Логируем результат расчета
        observe_service.create_event(event_type.info(), {
            "message": f"Расчет остатков завершен: {len(result)} позиций",
            "service": "balance_service"
        })
        
        return result

    def _calculate_balance_simple(self, target_date: datetime, storage_id: str = None) -> list:
        """
        Простой расчет остатков без использования блокировки
        
        Args:
            target_date (datetime): целевая дата
            storage_id (str): ID склада
            
        Returns:
            list: данные остатков
        """
        observe_service.create_event(event_type.debug(), {
            "message": "Простой расчет остатков без использования блокировки",
            "service": "balance_service"
        })
        
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
            storage_id (str): ID склада
            
        Returns:
            list: объединенные данные остатков
        """
        nomenclatures = self.__repo.data.get(reposity.nomenclature_key(), [])
        storages = self.__repo.data.get(reposity.storage_key(), [])
        
        observe_service.create_event(event_type.debug(), {
            "message": f"Объединение кэшированных и свежих оборотов",
            "service": "balance_service",
            "details": {
                "cached_turnovers": len(cached_turnovers),
                "recent_turnovers": len(recent_turnovers),
                "nomenclatures": len(nomenclatures),
                "storages": len(storages)
            }
        })
        
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
