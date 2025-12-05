from Src.reposity import reposity
from Src.Models.turnover_cache_model import turnover_cache_model
from Src.Models.transaction_model import transaction_model
from Src.Core.validator import validator, operation_exception, argument_exception
from Src.Core.observe_service import observe_service
from Src.Core.event_type import event_type
from datetime import datetime

"""
Сервис для расчета оборотов с поддержкой даты блокировки
"""
class turnover_service:
    __repo: reposity = None

    def __init__(self, data: reposity):
        if not isinstance(data, reposity):
            raise argument_exception("Некорректный тип данных")
        self.__repo = data
        
        # Логируем инициализацию сервиса
        observe_service.create_event(event_type.info(), {
            "message": "Инициализация сервиса расчетов оборотов",
            "service": "turnover_service"
        })

    def calculate_turnovers_to_block_period(self, block_period: datetime) -> bool:
        """
        Расчет оборотов за период с 1900-01-01 до block_period
        и сохранение результатов в кэш
        
        Args:
            block_period (datetime): дата блокировки
            
        Returns:
            bool: True если расчет успешно завершен
        """
        validator.validate(block_period, datetime)
        
        # Логируем начало расчета
        observe_service.create_event(event_type.info(), {
            "message": f"Расчет оборотов до даты блокировки: {block_period.isoformat()}",
            "service": "turnover_service",
            "details": {"block_period": block_period.isoformat()}
        })
        
        start_date = datetime(1900, 1, 1)
        transactions = self.__repo.data.get(reposity.transaction_key(), [])
        nomenclatures = self.__repo.data.get(reposity.nomenclature_key(), [])
        storages = self.__repo.data.get(reposity.storage_key(), [])
        
        # Очищаем старый кэш для этой даты блокировки
        self._clear_cache_for_period(block_period)
        
        turnover_cache = []
        
        observe_service.create_event(event_type.debug(), {
            "message": f"Начинается расчет по {len(nomenclatures)} номенклатурам и {len(storages)} складам",
            "service": "turnover_service"
        })
        
        processed_count = 0
        for nomenclature in nomenclatures:
            for storage in storages:
                # Фильтруем транзакции по номенклатуре, складу и периоду
                nom_storage_transactions = [
                    t for t in transactions 
                    if t.nomenclature.unique_code == nomenclature.unique_code
                    and t.storage.unique_code == storage.unique_code
                    and start_date <= t.date <= block_period
                ]
                
                if not nom_storage_transactions:
                    continue
                
                # Рассчитываем дебетовый и кредитовый обороты
                debit_turnover = sum(
                    t.quantity for t in nom_storage_transactions if t.quantity > 0
                )
                credit_turnover = sum(
                    abs(t.quantity) for t in nom_storage_transactions if t.quantity < 0
                )
                
                # Создаем запись кэша
                cache_item = turnover_cache_model.create(
                    nomenclature_id=nomenclature.unique_code,
                    storage_id=storage.unique_code,
                    period_end=block_period,
                    debit_turnover=debit_turnover,
                    credit_turnover=credit_turnover
                )
                
                turnover_cache.append(cache_item)
                processed_count += 1
        
        # Сохраняем кэш в репозиторий
        self.__repo.data[reposity.turnover_cache_key()].extend(turnover_cache)
        
        # Логируем успешное завершение расчета
        observe_service.create_event(event_type.info(), {
            "message": f"Расчет оборотов завершен: создано {len(turnover_cache)} записей кэша",
            "service": "turnover_service",
            "details": {
                "block_period": block_period.isoformat(),
                "cache_records": len(turnover_cache),
                "processed_combinations": processed_count
            }
        })
        
        return True

    def _clear_cache_for_period(self, block_period: datetime):
        """
        Очистка кэша для указанной даты блокировки
        
        Args:
            block_period (datetime): дата блокировки
        """
        cache_data = self.__repo.data.get(reposity.turnover_cache_key(), [])
        old_count = len(cache_data)
        self.__repo.data[reposity.turnover_cache_key()] = [
            item for item in cache_data if item.period_end != block_period
        ]
        new_count = len(self.__repo.data[reposity.turnover_cache_key()])
        
        if old_count != new_count:
            observe_service.create_event(event_type.debug(), {
                "message": f"Очищен кэш для даты блокировки {block_period.isoformat()}: удалено {old_count - new_count} записей",
                "service": "turnover_service"
            })

    def get_cached_turnovers(self, block_period: datetime) -> list:
        """
        Получение кэшированных оборотов для указанной даты блокировки
        
        Args:
            block_period (datetime): дата блокировки
            
        Returns:
            list: список кэшированных оборотов
        """
        validator.validate(block_period, datetime)
        
        cache_data = self.__repo.data.get(reposity.turnover_cache_key(), [])
        result = [item for item in cache_data if item.period_end == block_period]
        
        observe_service.create_event(event_type.debug(), {
            "message": f"Запрос кэшированных оборотов для даты {block_period.isoformat()}: найдено {len(result)} записей",
            "service": "turnover_service"
        })
        
        return result

    def calculate_turnovers_for_period(self, start_date: datetime, end_date: datetime) -> list:
        """
        Расчет оборотов за указанный период
        
        Args:
            start_date (datetime): начальная дата
            end_date (datetime): конечная дата
            
        Returns:
            list: список оборотов по номенклатурам и складам
        """
        validator.validate(start_date, datetime)
        validator.validate(end_date, datetime)
        
        if start_date > end_date:
            error_msg = "Дата начала не может быть позже даты окончания"
            observe_service.create_event(event_type.error(), {
                "message": error_msg,
                "service": "turnover_service",
                "details": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()}
            })
            raise operation_exception(error_msg)
        
        # Логируем начало расчета
        observe_service.create_event(event_type.info(), {
            "message": f"Расчет оборотов за период с {start_date.isoformat()} по {end_date.isoformat()}",
            "service": "turnover_service"
        })
        
        transactions = self.__repo.data.get(reposity.transaction_key(), [])
        nomenclatures = self.__repo.data.get(reposity.nomenclature_key(), [])
        storages = self.__repo.data.get(reposity.storage_key(), [])
        
        result = []
        
        processed_count = 0
        for nomenclature in nomenclatures:
            for storage in storages:
                # Фильтруем транзакции по номенклатуре, складу и периоду
                period_transactions = [
                    t for t in transactions 
                    if t.nomenclature.unique_code == nomenclature.unique_code
                    and t.storage.unique_code == storage.unique_code
                    and start_date <= t.date <= end_date
                ]
                
                if not period_transactions:
                    continue
                
                debit_turnover = sum(
                    t.quantity for t in period_transactions if t.quantity > 0
                )
                credit_turnover = sum(
                    abs(t.quantity) for t in period_transactions if t.quantity < 0
                )
                
                result.append({
                    'nomenclature_id': nomenclature.unique_code,
                    'storage_id': storage.unique_code,
                    'debit_turnover': debit_turnover,
                    'credit_turnover': credit_turnover
                })
                processed_count += 1
        
        # Логируем результат расчета
        observe_service.create_event(event_type.info(), {
            "message": f"Расчет оборотов за период завершен: {len(result)} записей",
            "service": "turnover_service",
            "details": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "records_count": len(result),
                "processed_combinations": processed_count
            }
        })
        
        return result

    def save_turnovers_to_file(self, file_path: str) -> bool:
        """
        Сохранение кэшированных оборотов в файл
        
        Args:
            file_path (str): путь к файлу
            
        Returns:
            bool: True если сохранение успешно
        """
        try:
            import json
            from Src.Logics.convert_factory import convert_factory
            
            cache_data = self.__repo.data.get(reposity.turnover_cache_key(), [])
            factory = convert_factory()
            
            # Логируем начало сохранения
            observe_service.create_event(event_type.info(), {
                "message": f"Сохранение кэша оборотов в файл: {file_path}",
                "service": "turnover_service",
                "details": {"file_path": file_path, "cache_records": len(cache_data)}
            })
            
            export_data = {
                "export_date": datetime.now().isoformat(),
                "turnover_cache": [factory.convert(item) for item in cache_data]
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
                
            # Логируем успешное сохранение
            observe_service.create_event(event_type.info(), {
                "message": f"Кэш оборотов успешно сохранен в файл: {file_path}",
                "service": "turnover_service"
            })
                
            return True
        except Exception as e:
            observe_service.create_event(event_type.error(), {
                "message": f"Ошибка при сохранении оборотов: {str(e)}",
                "service": "turnover_service"
            })
            raise operation_exception(f"Ошибка при сохранении оборотов: {str(e)}")

    def load_turnovers_from_file(self, file_path: str) -> bool:
        """
        Загрузка кэшированных оборотов из файла
        
        Args:
            file_path (str): путь к файлу
            
        Returns:
            bool: True если загрузка успешна
        """
        try:
            import json
            import os
            
            if not os.path.exists(file_path):
                observe_service.create_event(event_type.warning(), {
                    "message": f"Файл кэша не найден: {file_path}",
                    "service": "turnover_service"
                })
                return False
                
            # Логируем начало загрузки
            observe_service.create_event(event_type.info(), {
                "message": f"Загрузка кэша оборотов из файла: {file_path}",
                "service": "turnover_service"
            })
                
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if "turnover_cache" not in data:
                observe_service.create_event(event_type.error(), {
                    "message": f"Файл {file_path} не содержит данных кэша оборотов",
                    "service": "turnover_service"
                })
                return False
                
            # Очищаем текущий кэш
            self.__repo.data[reposity.turnover_cache_key()] = []
            
            loaded_count = 0
            # Загружаем данные из файла
            for cache_item_data in data["turnover_cache"]:
                cache_item = turnover_cache_model()
                cache_item.unique_code = cache_item_data.get("unique_code", "")
                cache_item.nomenclature_id = cache_item_data.get("nomenclature_id", "")
                cache_item.storage_id = cache_item_data.get("storage_id", "")
                
                period_end_str = cache_item_data.get("period_end")
                if period_end_str:
                    cache_item.period_end = datetime.fromisoformat(period_end_str)
                    
                cache_item.debit_turnover = cache_item_data.get("debit_turnover", 0.0)
                cache_item.credit_turnover = cache_item_data.get("credit_turnover", 0.0)
                
                calculated_at_str = cache_item_data.get("calculated_at")
                if calculated_at_str:
                    cache_item.calculated_at = datetime.fromisoformat(calculated_at_str)
                    
                self.__repo.data[reposity.turnover_cache_key()].append(cache_item)
                loaded_count += 1
                
            # Логируем успешную загрузку
            observe_service.create_event(event_type.info(), {
                "message": f"Кэш оборотов успешно загружен из файла: {loaded_count} записей",
                "service": "turnover_service",
                "details": {"file_path": file_path, "loaded_records": loaded_count}
            })
                
            return True
        except Exception as e:
            observe_service.create_event(event_type.error(), {
                "message": f"Ошибка при загрузке оборотов: {str(e)}",
                "service": "turnover_service"
            })
            raise operation_exception(f"Ошибка при загрузке оборотов: {str(e)}")
