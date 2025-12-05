from Src.reposity import reposity
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Dtos.filter_dto import filter_dto
from Src.Core.prototype import prototype
from Src.Core.observe_service import observe_service
from Src.Core.event_type import event_type
from datetime import datetime
from Src.Core.validator import validator, operation_exception, argument_exception


class osv_service:
    __repo: reposity = None

    def __init__(self, data: reposity):
        if not isinstance(data, reposity):
            raise argument_exception("Некорректный тип данных")
        self.__repo = data
        
        # Логируем инициализацию сервиса
        observe_service.create_event(event_type.info(), {
            "message": "Инициализация сервиса ОСВ",
            "service": "osv_service"
        })

    def generate_osv_report(self, start_date: datetime, end_date: datetime, storage_id: str) -> list:
        """
        Генерирует оборотно-сальдовую ведомость

        Args:
            start_date (datetime): начальная дата
            end_date (datetime): конечная дата
            storage_id (str): ID склада

        Returns:
            list: данные отчета ОСВ
        """
        validator.validate(start_date, datetime)
        validator.validate(end_date, datetime)
        validator.validate(storage_id, str)

        # Логируем начало формирования отчета
        observe_service.create_event(event_type.info(), {
            "message": f"Формирование отчета ОСВ: {start_date} - {end_date}, склад: {storage_id}",
            "service": "osv_service"
        })

        if start_date > end_date:
            error_msg = "Дата начала не может быть позже даты окончания"
            observe_service.create_event(event_type.error(), {
                "message": error_msg,
                "service": "osv_service",
                "details": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            })
            raise operation_exception(error_msg)

        return self._generate_report_data(start_date, end_date, storage_id)

    def generate_osv_report_with_filters(self, filters: list) -> list:
        """
        Генерирует оборотно-сальдовую ведомость с использованием DTO фильтров
        с применением прототипа внутри процесса формирования

        Args:
            filters (list): список объектов filter_dto с условиями фильтрации

        Returns:
            list: данные отчета ОСВ
        """
        validator.validate(filters, list)

        # Логируем начало формирования отчета с фильтрами
        observe_service.create_event(event_type.info(), {
            "message": f"Формирование отчета ОСВ с фильтрами: {len(filters)} фильтров",
            "service": "osv_service"
        })

        if len(filters) == 0:
            error_msg = "Не указаны фильтры для формирования отчета"
            observe_service.create_event(event_type.error(), {
                "message": error_msg,
                "service": "osv_service"
            })
            raise operation_exception(error_msg)

        # Извлекаем параметры из фильтров
        start_date, end_date, storage_id = self._parse_filters(filters)
        
        observe_service.create_event(event_type.debug(), {
            "message": "Параметры отчета извлечены из фильтров",
            "service": "osv_service",
            "details": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "storage_id": storage_id,
                "filters_count": len(filters)
            }
        })

        # Получаем базовые данные отчета с использованием прототипа
        report_data = self._generate_report_data_with_prototype(start_date, end_date, storage_id, filters)
        
        # Логируем результат формирования отчета
        observe_service.create_event(event_type.info(), {
            "message": f"Отчет ОСВ сформирован: {len(report_data)} позиций",
            "service": "osv_service"
        })

        return report_data

    def _generate_report_data(self, start_date: datetime, end_date: datetime, storage_id: str) -> list:
        """
        Генерирует данные отчета ОСВ

        Args:
            start_date (datetime): начальная дата
            end_date (datetime): конечная дата
            storage_id (str): ID склада

        Returns:
            list: данные отчета
        """
        transactions = self.__repo.data.get(reposity.transaction_key(), [])
        nomenclatures = self.__repo.data.get(reposity.nomenclature_key(), [])
        storages = self.__repo.data.get(reposity.storage_key(), [])

        # Проверяем что склад существует
        storage = next((s for s in storages if s.unique_code == storage_id), None)
        if not storage:
            error_msg = f"Склад с ID {storage_id} не найден"
            observe_service.create_event(event_type.error(), {
                "message": error_msg,
                "service": "osv_service"
            })
            raise operation_exception(error_msg)
        
        observe_service.create_event(event_type.debug(), {
            "message": "Получены данные для отчета ОСВ",
            "service": "osv_service",
            "details": {
                "transactions": len(transactions),
                "nomenclatures": len(nomenclatures),
                "storages": len(storages),
                "selected_storage": storage.name
            }
        })

        result = []

        for nomenclature in nomenclatures:
            # Фильтруем транзакции по номенклатуре и складу
            nom_transactions = [t for t in transactions
                                if t.nomenclature.unique_code == nomenclature.unique_code
                                and t.storage.unique_code == storage_id]

            # Рассчитываем балансы
            start_balance = sum(self.__convert_to_base_units(t)
                                for t in nom_transactions
                                if t.date < start_date)

            income = sum(self.__convert_to_base_units(t)
                         for t in nom_transactions
                         if start_date <= t.date <= end_date and t.count > 0)

            outcome = sum(abs(self.__convert_to_base_units(t))
                          for t in nom_transactions
                          if start_date <= t.date <= end_date and t.count < 0)

            end_balance = start_balance + income - outcome

            # Конвертируем в единицы измерения номенклатуры
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
                "nomenclature": nomenclature.name,
                "start_balance": round(display_start_balance, 3),
                "income": round(display_income, 3),
                "outcome": round(display_outcome, 3),
                "end_balance": round(display_end_balance, 3),
                "nomenclature_id": nomenclature.unique_code
            }

            result.append(report_item)
            
            # Логируем детали по каждой номенклатуре
            observe_service.create_event(event_type.debug(), {
                "message": f"Расчет для номенклатуры: {nomenclature.name}",
                "service": "osv_service",
                "details": {
                    "nomenclature": nomenclature.name,
                    "start_balance": display_start_balance,
                    "income": display_income,
                    "outcome": display_outcome,
                    "end_balance": display_end_balance,
                    "transactions_count": len(nom_transactions)
                }
            })

        return result

    def _generate_report_data_with_prototype(self, start_date: datetime, end_date: datetime,
                                             storage_id: str, filters: list) -> list:
        """
        Генерирует данные отчета ОСВ с использованием прототипа для фильтрации номенклатур

        Args:
            start_date (datetime): начальная дата
            end_date (datetime): конечная дата
            storage_id (str): ID склада
            filters (list): список фильтров для номенклатур

        Returns:
            list: данные отчета
        """
        transactions = self.__repo.data.get(reposity.transaction_key(), [])
        nomenclatures = self.__repo.data.get(reposity.nomenclature_key(), [])
        storages = self.__repo.data.get(reposity.storage_key(), [])

        # Проверяем что склад существует
        storage = next((s for s in storages if s.unique_code == storage_id), None)
        if not storage:
            error_msg = f"Склад с ID {storage_id} не найден"
            observe_service.create_event(event_type.error(), {
                "message": error_msg,
                "service": "osv_service"
            })
            raise operation_exception(error_msg)

        # Фильтруем номенклатуры с помощью прототипа
        nomenclature_filters = [f for f in filters if f.field_name not in ["period", "storage"]]

        if nomenclature_filters:
            # Используем прототип для фильтрации номенклатур
            observe_service.create_event(event_type.debug(), {
                "message": f"Применение фильтров к номенклатурам: {len(nomenclature_filters)} фильтров",
                "service": "osv_service"
            })
            
            filtered_nomenclatures = prototype.filter(nomenclatures, nomenclature_filters)
            
            observe_service.create_event(event_type.debug(), {
                "message": f"Результат фильтрации номенклатур",
                "service": "osv_service",
                "details": {
                    "total_nomenclatures": len(nomenclatures),
                    "filtered_nomenclatures": len(filtered_nomenclatures)
                }
            })
        else:
            filtered_nomenclatures = nomenclatures

        result = []

        for nomenclature in filtered_nomenclatures:
            # Фильтруем транзакции по номенклатуре и складу
            nom_transactions = [t for t in transactions
                                if t.nomenclature.unique_code == nomenclature.unique_code
                                and t.storage.unique_code == storage_id]

            # Рассчитываем балансы
            start_balance = sum(self.__convert_to_base_units(t)
                                for t in nom_transactions
                                if t.date < start_date)

            income = sum(self.__convert_to_base_units(t)
                         for t in nom_transactions
                         if start_date <= t.date <= end_date and t.count > 0)

            outcome = sum(abs(self.__convert_to_base_units(t))
                          for t in nom_transactions
                          if start_date <= t.date <= end_date and t.count < 0)

            end_balance = start_balance + income - outcome

            # Конвертируем в единицы измерения номенклатуры
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
                "nomenclature": nomenclature.name,
                "start_balance": round(display_start_balance, 3),
                "income": round(display_income, 3),
                "outcome": round(display_outcome, 3),
                "end_balance": round(display_end_balance, 3),
                "nomenclature_id": nomenclature.unique_code
            }

            result.append(report_item)

        return result

    def _parse_filters(self, filters: list) -> tuple:
        """
        Парсит фильтры и извлекает параметры для отчета

        Args:
            filters (list): список фильтров

        Returns:
            tuple: (start_date, end_date, storage_id)
        """
        start_date = None
        end_date = None
        storage_id = None

        for filter_item in filters:
            if filter_item.field_name == "period":
                try:
                    date_value = datetime.fromisoformat(filter_item.value)
                    if filter_item.type.value in ["GREATER", "GREATER_EQUAL"]:
                        start_date = date_value
                    elif filter_item.type.value in ["LESS", "LESS_EQUAL"]:
                        end_date = date_value
                    elif filter_item.type.value == "EQUALS":
                        # Если указано равенство, используем эту дату как и начало и конец
                        start_date = date_value
                        end_date = date_value
                        
                    observe_service.create_event(event_type.debug(), {
                        "message": f"Извлечена дата из фильтра: {date_value}",
                        "service": "osv_service"
                    })
                        
                except ValueError:
                    error_msg = f"Некорректный формат даты: {filter_item.value}"
                    observe_service.create_event(event_type.error(), {
                        "message": error_msg,
                        "service": "osv_service"
                    })
                    raise operation_exception(error_msg)
            elif filter_item.field_name == "storage" and filter_item.type.value == "EQUALS":
                storage_id = filter_item.value
                observe_service.create_event(event_type.debug(), {
                    "message": f"Извлечен ID склада из фильтра: {storage_id}",
                    "service": "osv_service"
                })

        # Проверяем что все обязательные параметры найдены
        if start_date is None:
            error_msg = "Не указана начальная дата периода"
            observe_service.create_event(event_type.error(), {
                "message": error_msg,
                "service": "osv_service"
            })
            raise operation_exception(error_msg)

        if end_date is None:
            error_msg = "Не указана конечная дата периода"
            observe_service.create_event(event_type.error(), {
                "message": error_msg,
                "service": "osv_service"
            })
            raise operation_exception(error_msg)

        if storage_id is None:
            error_msg = "Не указан фильтр по складу"
            observe_service.create_event(event_type.error(), {
                "message": error_msg,
                "service": "osv_service"
            })
            raise operation_exception(error_msg)

        if start_date > end_date:
            error_msg = "Дата начала не может быть позже даты окончания"
            observe_service.create_event(event_type.error(), {
                "message": error_msg,
                "service": "osv_service",
                "details": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            })
            raise operation_exception(error_msg)

        return start_date, end_date, storage_id

    def __convert_to_base_units(self, transaction) -> float:
        """
        Конвертирует количество транзакции в базовые единицы

        Args:
            transaction: объект транзакции

        Returns:
            float: количество в базовых единицах
        """
        try:
            if transaction.nomenclature and transaction.nomenclature.range:
                range_obj = transaction.nomenclature.range
                # Конвертируем в базовые единицы
                if hasattr(range_obj, 'base_unit') and range_obj.base_unit:
                    # Если есть коэффициент конвертации, используем его
                    if hasattr(range_obj, 'coefficient') and range_obj.coefficient:
                        return transaction.count * range_obj.coefficient
                    else:
                        return transaction.count
                else:
                    return transaction.count
            else:
                return transaction.count
        except Exception:
            return transaction.count

    def __convert_from_base_units(self, count: float, range_obj: range_model) -> float:
        """
        Конвертирует количество из базовых единиц в единицы измерения номенклатуры

        Args:
            count (float): количество в базовых единицах
            range_obj (range_model): модель единицы измерения

        Returns:
            float: количество в единицах измерения номенклатуры
        """
        try:
            if range_obj and hasattr(range_obj, 'base_unit') and range_obj.base_unit:
                # Если есть коэффициент конвертации, используем его
                if hasattr(range_obj, 'coefficient') and range_obj.coefficient:
                    return count / range_obj.coefficient
                else:
                    return count
            else:
                return count
        except Exception:
            return count
