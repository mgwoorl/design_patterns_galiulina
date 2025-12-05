"""
Главный модуль приложения
"""
import connexion
from flask import Response, request
from Src.start_service import start_service
from Src.Logics.factory_entities import factory_entities
from Src.Models.settings_model import settings_model, ResponseFormat
from Src.reposity import reposity
from Src.Logics.convert_factory import convert_factory
from Src.Logics.osv_service import osv_service
from Src.Logics.export_service import export_service
from Src.settings_manager import settings_manager
from Src.Core.validator import argument_exception, operation_exception
from Src.Dtos.filter_dto import filter_dto
from Src.Core.prototype import prototype
from Src.Core.filter_type import FilterType
from Src.Core.common import common
from Src.Logics.balance_service import balance_service
from Src.Logics.turnover_service import turnover_service
from Src.Logics.reference_service import reference_service
from Src.Core.observe_service import observe_service
from Src.Core.event_type import event_type
from Src.Dtos.block_date_dto import block_date_dto
from datetime import datetime
import json

# Импортируем модули логирования
from Src.Core.logger_service import logger_service
from Src.Core.log_level import LogLevel

app = connexion.FlaskApp(__name__)

# Создаем глобальный логгер
logger = logger_service()

# Логируем запуск приложения
logger.info("Запуск приложения", "main")

service = start_service()

settings_mgr = settings_manager()
settings_mgr.file_name = "settings.json"
settings_mgr.load()

if settings_mgr.settings.is_first_start:
    logger.info("Первый запуск приложения, инициализация данных", "main")
    service.start()
    settings_mgr.settings.is_first_start = False
    settings_mgr.save()
    logger.info("Данные успешно инициализированы", "main")
else:
    logger.debug("Загрузка данных из существующего состояния", "main")
    service.data.initalize()

settings = settings_model()
factory = factory_entities(settings)

osv_service_instance = osv_service(service.data)
export_service_instance = export_service(service.data)
balance_service_instance = balance_service(service.data, settings_mgr.settings)
turnover_service_instance = turnover_service(service.data)

reference_service_instance = reference_service()

logger.info("Все сервисы инициализированы, приложение готово к работе", "main")

@app.route("/api/accessibility", methods=['GET'])
def accessibility():
    # Логируем вызов API
    logger.info("API вызов: GET /api/accessibility", "api")
    return "SUCCESS"

@app.route("/api/entities", methods=['GET'])
def get_entities():
    # Логируем вызов API
    logger.info("API вызов: GET /api/entities", "api")
    
    return {
        "entities": ["ranges", "groups", "nomenclatures", "receipts", "storages", "transactions"],
        "formats": ["csv", "markdown", "json", "xml"]
    }

@app.route("/api/data/<entity_type>/<format_type>", methods=['GET'])
def get_data(entity_type: str, format_type: str):
    # Логируем вызов API
    logger.info(f"API вызов: GET /api/data/{entity_type}/{format_type}", "api")
    
    entity_map = {
        "ranges": reposity.range_key(),
        "groups": reposity.group_key(),
        "nomenclatures": reposity.nomenclature_key(),
        "receipts": reposity.receipt_key(),
        "storages": reposity.storage_key(),
        "transactions": reposity.transaction_key()
    }

    if entity_type not in entity_map:
        logger.error(f"Неизвестный тип сущности: {entity_type}", "api")
        return {"error": f"Unknown entity type: {entity_type}"}, 400

    if format_type not in ["csv", "markdown", "json", "xml"]:
        logger.error(f"Неизвестный формат: {format_type}", "api")
        return {"error": f"Unknown format type: {format_type}"}, 400

    data = service.data.data.get(entity_map[entity_type], [])

    if not data:
        logger.warning(f"Нет данных для сущности: {entity_type}", "api")
        return {"error": f"No data for entity: {entity_type}"}, 404

    settings.response_format = ResponseFormat(format_type)
    formatter = factory.create_default(data)
    result = formatter.build(data)

    content_types = {
        "csv": "text/plain; charset=utf-8",
        "markdown": "text/plain; charset=utf-8",
        "json": "application/json; charset=utf-8",
        "xml": "application/xml; charset=utf-8"
    }

    logger.info(f"Получены данные {entity_type} в формате {format_type}: {len(data)} записей", "api")
    
    return Response(
        result,
        content_type=content_types.get(format_type, "text/plain")
    )

@app.route("/api/receipts", methods=['GET'])
def get_recipes():
    # Логируем вызов API
    logger.info("API вызов: GET /api/recipes", "api")
    
    receipts = service.data.data.get(reposity.receipt_key(), [])
    factory_conv = convert_factory()

    result = []
    for receipt in receipts:
        converted_data = factory_conv.convert(receipt)
        result.append(converted_data)

    logger.info(f"Получены рецепты: {len(receipts)} шт.", "api")
    
    return Response(
        json.dumps(result, ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8"
    )

@app.route("/api/receipt/<receipt_id>", methods=['GET'])
def get_receipt(receipt_id: str):
    # Логируем вызов API
    logger.info(f"API вызов: GET /api/receipt/{receipt_id}", "api")
    
    receipts = service.data.data.get(reposity.receipt_key(), [])
    factory_conv = convert_factory()

    found_receipt = None
    for receipt in receipts:
        if receipt.unique_code == receipt_id:
            found_receipt = receipt
            break

    if not found_receipt:
        logger.error(f"Рецепт с ID {receipt_id} не найден", "api")
        return {"error": f"Receipt with id {receipt_id} not found"}, 404

    converted_data = factory_conv.convert(found_receipt)

    logger.info(f"Получен рецепт с ID: {receipt_id}", "api")
    
    return Response(
        json.dumps(converted_data, ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8"
    )

@app.route("/api/reports/osv", methods=['GET'])
def get_osv_report():
    # Логируем вызов API
    logger.info("API вызов: GET /api/reports/osv", "api")
    
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    storage_id = request.args.get('storage_id')

    if not all([start_date_str, end_date_str, storage_id]):
        logger.error("Отсутствуют обязательные параметры: start_date, end_date, storage_id", "api")
        return {"error": "Missing required parameters: start_date, end_date, storage_id"}, 400

    try:
        start_date = datetime.fromisoformat(start_date_str)
        end_date = datetime.fromisoformat(end_date_str)
    except ValueError as e:
        logger.error(f"Некорректный формат даты: {str(e)}", "api")
        return {"error": f"Invalid date format: {str(e)}"}, 400

    try:
        report_data = osv_service_instance.generate_osv_report(start_date, end_date, storage_id)
        
        logger.info(f"Сформирован отчет ОСВ с {start_date} по {end_date} для склада {storage_id}: {len(report_data)} позиций", "api")

        return Response(
            json.dumps(report_data, ensure_ascii=False, indent=2),
            content_type="application/json; charset=utf-8"
        )

    except operation_exception as e:
        logger.error(f"Ошибка при формировании отчета ОСВ: {str(e)}", "api")
        return {"error": str(e)}, 400
    except Exception as e:
        logger.error(f"Внутренняя ошибка сервера: {str(e)}", "api")
        return {"error": f"Internal server error: {str(e)}"}, 500

@app.route("/api/save-to-file", methods=['POST', 'GET'])
def save_to_file():
    # Логируем вызов API
    logger.info("API вызов: POST /api/save-to-file", "api")
    
    filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    try:
        success = export_service_instance.export_all_data(filename)

        if success:
            logger.info(f"Данные успешно экспортированы в файл: {filename}", "api")
            return {
                "message": f"Data saved to {filename}",
                "filename": filename,
                "success": True
            }
        else:
            logger.error("Ошибка при сохранении данных", "api")
            return {"error": "Failed to save data", "success": False}, 500

    except Exception as e:
        logger.error(f"Ошибка при экспорте данных: {str(e)}", "api")
        return {"error": str(e), "success": False}, 500

@app.route("/api/filters/<model_type>", methods=['GET'])
def get_filters_by_model(model_type: str):
    # Логируем вызов API
    logger.info(f"API вызов: GET /api/filters/{model_type}", "api")
    
    model_map = {
        "ranges": reposity.range_key(),
        "groups": reposity.group_key(),
        "nomenclatures": reposity.nomenclature_key(),
        "receipts": reposity.receipt_key(),
        "storages": reposity.storage_key(),
        "transactions": reposity.transaction_key()
    }

    if model_type not in model_map:
        logger.error(f"Неизвестный тип модели: {model_type}", "api")
        return Response(
            json.dumps({
                "success": False,
                "error": f"Unknown model type: {model_type}"
            }, ensure_ascii=False),
            status=400,
            content_type="application/json; charset=utf-8"
        )

    data_key = model_map[model_type]
    data = service.data.data.get(data_key, [])

    if len(data) == 0:
        logger.warning(f"Нет данных для модели: {model_type}", "api")
        return Response(
            json.dumps({
                "success": False,
                "error": f"No data for model: {model_type}"
            }, ensure_ascii=False),
            status=404,
            content_type="application/json; charset=utf-8"
        )

    first_elem = data[0]
    fields_name = common.get_fields(first_elem)

    result = {
        "filter_field_names": fields_name,
        "filter_types": FilterType.get_all_types()
    }

    logger.info(f"Получены фильтры для модели {model_type}: {len(fields_name)} полей", "api")
    
    return Response(
        json.dumps(result, ensure_ascii=False, indent=2),
        status=200,
        content_type="application/json; charset=utf-8"
    )

@app.route("/api/data/<model_type>/<format_type>", methods=['POST'])
def get_data_filtered(model_type: str, format_type: str):
    # Логируем вызов API
    logger.info(f"API вызов: POST /api/data/{model_type}/{format_type}", "api")
    
    try:
        filters_data = request.get_json()

        if not filters_data or not isinstance(filters_data, list):
            logger.error("Ожидается массив фильтров в теле запроса", "api")
            return Response(
                json.dumps({
                    "success": False,
                    "error": "Expected array of filters in request body"
                }, ensure_ascii=False),
                status=400,
                content_type="application/json; charset=utf-8"
            )

        model_map = {
            "ranges": reposity.range_key(),
            "groups": reposity.group_key(),
            "nomenclatures": reposity.nomenclature_key(),
            "receipts": reposity.receipt_key(),
            "storages": reposity.storage_key(),
            "transactions": reposity.transaction_key()
        }

        if model_type not in model_map:
            logger.error(f"Неизвестный тип модели: {model_type}", "api")
            return Response(
                json.dumps({
                    "success": False,
                    "error": f"Unknown model type: {model_type}. Available: {list(model_map.keys())}"
                }, ensure_ascii=False),
                status=400,
                content_type="application/json; charset=utf-8"
            )

        if format_type not in ["csv", "markdown", "json", "xml"]:
            logger.error(f"Неизвестный формат: {format_type}", "api")
            return Response(
                json.dumps({
                    "success": False,
                    "error": f"Unknown format type: {format_type}"
                }, ensure_ascii=False),
                status=400,
                content_type="application/json; charset=utf-8"
            )

        data_key = model_map[model_type]
        data = service.data.data.get(data_key, [])

        if len(data) == 0:
            logger.warning(f"Нет данных для модели: {model_type}", "api")
            return Response(
                json.dumps({
                    "success": True,
                    "count": 0,
                    "data": []
                }, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            )

        filters = []
        for filter_item in filters_data:
            filter_dto_obj = filter_dto().create(filter_item)
            filters.append(filter_dto_obj)

        filtered_data = prototype.filter(data, filters)

        settings.response_format = ResponseFormat(format_type)
        formatter = factory.create_default(filtered_data)
        result = formatter.build(filtered_data)

        content_types = {
            "csv": "text/plain; charset=utf-8",
            "markdown": "text/plain; charset=utf-8",
            "json": "application/json; charset=utf-8",
            "xml": "application/xml; charset=utf-8"
        }

        logger.info(f"Применены фильтры к данным {model_type}: {len(filters)} фильтров, результат: {len(filtered_data)} записей", "api")

        return Response(
            result,
            content_type=content_types.get(format_type, "text/plain")
        )

    except operation_exception as e:
        logger.error(f"Бизнес-ошибка при фильтрации данных: {str(e)}", "api")
        return Response(
            json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False),
            status=400,
            content_type="application/json; charset=utf-8"
        )
    except Exception as e:
        logger.error(f"Внутренняя ошибка сервера при фильтрации данных: {str(e)}", "api")
        return Response(
            json.dumps({
                "success": False,
                "error": f"Internal server error: {str(e)}"
            }, ensure_ascii=False),
            status=500,
            content_type="application/json; charset=utf-8"
        )

@app.route("/api/reports/osv/filter", methods=['POST'])
def get_osv_report_with_filters():
    # Логируем вызов API
    logger.info("API вызов: POST /api/reports/osv/filter", "api")
    
    try:
        filters_data = request.get_json()

        if not filters_data or not isinstance(filters_data, list):
            logger.error("Ожидается массив фильтров в теле запроса", "api")
            return Response(
                json.dumps({
                    "success": False,
                    "error": "Expected array of filters in request body"
                }, ensure_ascii=False),
                status=400,
                content_type="application/json; charset=utf-8"
            )

        filters = []
        for filter_item in filters_data:
            filter_dto_obj = filter_dto().create(filter_item)
            filters.append(filter_dto_obj)

        report_data = osv_service_instance.generate_osv_report_with_filters(filters)

        logger.info(f"Сформирован отчет ОСВ с фильтрами: {len(filters)} фильтров, результат: {len(report_data)} позиций", "api")

        return Response(
            json.dumps({
                "success": True,
                "count": len(report_data),
                "data": report_data
            }, ensure_ascii=False, indent=2),
            content_type="application/json; charset=utf-8"
        )

    except operation_exception as e:
        logger.error(f"Бизнес-ошибка при формировании отчета ОСВ с фильтрами: {str(e)}", "api")
        return Response(
            json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False),
            status=400,
            content_type="application/json; charset=utf-8"
        )
    except Exception as e:
        logger.error(f"Внутренняя ошибка сервера при формировании отчета ОСВ: {str(e)}", "api")
        return Response(
            json.dumps({
                "success": False,
                "error": f"Internal server error: {str(e)}"
            }, ensure_ascii=False),
            status=500,
            content_type="application/json; charset=utf-8"
        )

@app.route("/api/settings/block-period", methods=['POST'])
def set_block_period():
    # Логируем вызов API
    logger.info("API вызов: POST /api/settings/block-period", "api")
    
    try:
        data = request.get_json()
        
        if not data or 'block_period' not in data:
            logger.error("Отсутствует параметр block_period", "api")
            return Response(
                json.dumps({
                    "success": False,
                    "error": "Missing block_period parameter"
                }, ensure_ascii=False),
                status=400,
                content_type="application/json; charset=utf-8"
            )
        
        try:
            block_period = datetime.fromisoformat(data['block_period'])
            
            logger.info(f"Установка даты блокировки: {block_period}", "api")
            
            turnover_service_instance.calculate_turnovers_to_block_period(block_period)
            
            turnover_service_instance.save_turnovers_to_file("turnovers_cache.json")
            
            success = settings_mgr.set_block_period(block_period)
            
            if success:
                dto = block_date_dto().create({"new_block_date": block_period})
                observe_service.create_event(event_type.change_block_period(), dto)
                
                logger.info(f"Дата блокировки успешно установлена: {block_period.isoformat()}", "api")
                
                return Response(
                    json.dumps({
                        "success": True,
                        "message": f"Block period set to {block_period.isoformat()}",
                        "block_period": block_period.isoformat()
                    }, ensure_ascii=False),
                    status=200,
                    content_type="application/json; charset=utf-8"
                )
            else:
                logger.error("Ошибка сохранения даты блокировки", "api")
                return Response(
                    json.dumps({
                        "success": False,
                        "error": "Failed to save block period"
                    }, ensure_ascii=False),
                    status=500,
                    content_type="application/json; charset=utf-8"
                )
                
        except ValueError as e:
            logger.error(f"Некорректный формат даты: {str(e)}", "api")
            return Response(
                json.dumps({
                    "success": False,
                    "error": f"Invalid date format: {str(e)}"
                }, ensure_ascii=False),
                status=400,
                content_type="application/json; charset=utf-8"
            )
            
    except Exception as e:
        logger.error(f"Внутренняя ошибка сервера при установке даты блокировки: {str(e)}", "api")
        return Response(
            json.dumps({
                "success": False,
                "error": f"Internal server error: {str(e)}"
            }, ensure_ascii=False),
            status=500,
            content_type="application/json; charset=utf-8"
        )

@app.route("/api/settings/block-period", methods=['GET'])
def get_block_period():
    # Логируем вызов API
    logger.info("API вызов: GET /api/settings/block-period", "api")
    
    try:
        block_period = settings_mgr.get_block_period()
        
        result = {
            "success": True,
            "block_period": block_period.isoformat() if block_period else None
        }
        
        logger.debug(f"Получена дата блокировки: {block_period.isoformat() if block_period else 'не установлена'}", "api")
        
        return Response(
            json.dumps(result, ensure_ascii=False),
            status=200,
            content_type="application/json; charset=utf-8"
        )
        
    except Exception as e:
        logger.error(f"Ошибка получения даты блокировки: {str(e)}", "api")
        return Response(
            json.dumps({
                "success": False,
                "error": f"Internal server error: {str(e)}"
            }, ensure_ascii=False),
            status=500,
            content_type="application/json; charset=utf-8"
        )

@app.route("/api/balances", methods=['GET'])
def get_balances():
    # Логируем вызов API
    logger.info("API вызов: GET /api/balances", "api")
    
    try:
        date_str = request.args.get('date')
        storage_id = request.args.get('storage_id')
        
        if not date_str:
            logger.error("Отсутствует параметр date", "api")
            return Response(
                json.dumps({
                    "success": False,
                    "error": "Missing date parameter"
                }, ensure_ascii=False),
                status=400,
                content_type="application/json; charset=utf-8"
            )
        
        try:
            target_date = datetime.fromisoformat(date_str)
            
            logger.info(f"Запрос остатков на дату: {target_date}, склад: {storage_id if storage_id else 'все склады'}", "api")
            
            turnover_service_instance.load_turnovers_from_file("turnovers_cache.json")
            
            balances = balance_service_instance.calculate_balance_with_block_period(
                target_date, storage_id
            )
            
            logger.info(f"Рассчитаны остатки на {target_date}: {len(balances)} позиций", "api")
            
            return Response(
                json.dumps({
                    "success": True,
                    "count": len(balances),
                    "data": balances
                }, ensure_ascii=False, indent=2),
                status=200,
                content_type="application/json; charset=utf-8"
            )
            
        except ValueError as e:
            logger.error(f"Некорректный формат даты: {str(e)}", "api")
            return Response(
                json.dumps({
                    "success": False,
                    "error": f"Invalid date format: {str(e)}"
                }, ensure_ascii=False),
                status=400,
                content_type="application/json; charset=utf-8"
            )
        except operation_exception as e:
            logger.error(f"Бизнес-ошибка при расчете остатков: {str(e)}", "api")
            return Response(
                json.dumps({
                    "success": False,
                    "error": str(e)
                }, ensure_ascii=False),
                status=400,
                content_type="application/json; charset=utf-8"
            )
            
    except Exception as e:
        logger.error(f"Внутренняя ошибка сервера при расчете остатков: {str(e)}", "api")
        return Response(
            json.dumps({
                "success": False,
                "error": f"Internal server error: {str(e)}"
            }, ensure_ascii=False),
            status=500,
            content_type="application/json; charset=utf-8"
        )

@app.route("/api/reference/<reference_type>", methods=['GET'])
def get_reference(reference_type: str):
    """
    Получить элемент справочника по ID
    """
    # Логируем вызов API
    logger.info(f"API вызов: GET /api/reference/{reference_type}", "api")
    
    try:
        item_id = request.args.get('id')
        
        if item_id:
            factory_conv = convert_factory()
            
            model_map = {
                "nomenclature": reposity.nomenclature_key(),
                "group": reposity.group_key(),
                "range": reposity.range_key(),
                "storage": reposity.storage_key()
            }
            
            if reference_type not in model_map:
                logger.error(f"Неизвестный тип справочника: {reference_type}", "api")
                return {"error": f"Unknown reference type: {reference_type}"}, 400
            
            key = model_map[reference_type]
            items = service.data.data.get(key, [])
            
            item = None
            for it in items:
                if it.unique_code == item_id:
                    item = it
                    break
            
            if not item:
                logger.error(f"Элемент с ID {item_id} не найден", "api")
                return {"error": f"Item with id {item_id} not found"}, 404
            
            result = factory_conv.convert(item)
            
            logger.info(f"Получен элемент справочника {reference_type} с ID: {item_id}", "api")
            
            return Response(
                json.dumps(result, ensure_ascii=False, indent=2),
                content_type="application/json; charset=utf-8"
            )
        else:
            logger.error("Отсутствует параметр id", "api")
            return {"error": "ID parameter is required for GET"}, 400
            
    except Exception as e:
        logger.error(f"Внутренняя ошибка сервера при получении элемента справочника: {str(e)}", "api")
        return {"error": f"Internal server error: {str(e)}"}, 500

@app.route("/api/reference/<reference_type>", methods=['PUT'])
def add_reference(reference_type: str):
    """
    Добавить новый элемент справочника
    """
    # Логируем вызов API
    logger.info(f"API вызов: PUT /api/reference/{reference_type}", "api")
    
    try:
        data = request.get_json()
        
        if not data:
            logger.error("Отсутствуют данные в теле запроса", "api")
            return {"error": "No data provided"}, 400
        
        logger.info(f"Добавление элемента справочника {reference_type}", "api", {"properties": data})
        
        reference_service.add(reference_type, data)
        
        logger.info(f"Элемент справочника {reference_type} успешно добавлен", "api")
        
        return {
            "success": True,
            "message": f"Reference {reference_type} added successfully"
        }
            
    except argument_exception as e:
        logger.error(f"Ошибка аргументов при добавлении элемента справочника: {str(e)}", "api")
        return {"error": str(e)}, 400
    except operation_exception as e:
        logger.error(f"Бизнес-ошибка при добавлении элемента справочника: {str(e)}", "api")
        return {"error": str(e)}, 400
    except Exception as e:
        logger.error(f"Внутренняя ошибка сервера при добавлении элемента справочника: {str(e)}", "api")
        return {"error": f"Internal server error: {str(e)}"}, 500

@app.route("/api/reference/<reference_type>", methods=['PATCH'])
def update_reference(reference_type: str):
    """
    Изменить элемент справочника
    """
    # Логируем вызов API
    logger.info(f"API вызов: PATCH /api/reference/{reference_type}", "api")
    
    try:
        data = request.get_json()
        
        if not data:
            logger.error("Отсутствуют данные в теле запроса", "api")
            return {"error": "No data provided"}, 400
        
        if 'unique_code' not in data:
            logger.error("Отсутствует поле unique_code", "api")
            return {"error": "unique_code is required"}, 400
        
        logger.info(f"Изменение элемента справочника {reference_type} с ID: {data['unique_code']}", "api", {"properties": data})
        
        reference_service.change(reference_type, data)
        
        logger.info(f"Элемент справочника {reference_type} с ID {data['unique_code']} успешно изменен", "api")
        
        return {
            "success": True,
            "message": f"Reference {reference_type} updated successfully"
        }
            
    except argument_exception as e:
        logger.error(f"Ошибка аргументов при изменении элемента справочника: {str(e)}", "api")
        return {"error": str(e)}, 400
    except operation_exception as e:
        logger.error(f"Бизнес-ошибка при изменении элемента справочника: {str(e)}", "api")
        return {"error": str(e)}, 404
    except Exception as e:
        logger.error(f"Внутренняя ошибка сервера при изменении элемента справочника: {str(e)}", "api")
        return {"error": f"Internal server error: {str(e)}"}, 500

@app.route("/api/reference/<reference_type>", methods=['DELETE'])
def delete_reference(reference_type: str):
    """
    Удалить элемент справочника
    """
    # Логируем вызов API
    logger.info(f"API вызов: DELETE /api/reference/{reference_type}", "api")
    
    try:
        data = request.get_json()
        
        if not data:
            logger.error("Отсутствуют данные в теле запроса", "api")
            return {"error": "No data provided"}, 400
        
        if 'unique_code' not in data:
            logger.error("Отсутствует поле unique_code", "api")
            return {"error": "unique_code is required"}, 400
        
        logger.info(f"Удаление элемента справочника {reference_type} с ID: {data['unique_code']}", "api")
        
        reference_service.remove(reference_type, data)
        
        logger.info(f"Элемент справочника {reference_type} с ID {data['unique_code']} успешно удален", "api")
        
        return {
            "success": True,
            "message": f"Reference {reference_type} deleted successfully"
        }
            
    except argument_exception as e:
        logger.error(f"Ошибка аргументов при удалении элемента справочника: {str(e)}", "api")
        return {"error": str(e)}, 400
    except operation_exception as e:
        logger.error(f"Бизнес-ошибка при удалении элемента справочника: {str(e)}", "api")
        return {"error": str(e)}, 409
    except Exception as e:
        logger.error(f"Внутренняя ошибка сервера при удалении элемента справочника: {str(e)}", "api")
        return {"error": f"Internal server error: {str(e)}"}, 500

if __name__ == '__main__':
    logger.info("Запуск приложения на localhost:8080", "main")
    app.run(host="localhost", port=8080)
