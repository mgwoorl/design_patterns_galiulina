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

app = connexion.FlaskApp(__name__)

from Src.Core.logger_service import logger

logger.info("Инициализация приложения", "main")

service = start_service()

settings_mgr = settings_manager()
settings_mgr.file_name = "settings.json"
settings_mgr.load()

logger.configure()

if settings_mgr.settings.is_first_start:
    logger.info("Первый запуск приложения, загрузка начальных данных", "main")
    service.start()
    settings_mgr.settings.is_first_start = False
    settings_mgr.save()
else:
    logger.info("Повторный запуск приложения", "main")
    service.data.initalize()

settings = settings_model()
factory = factory_entities(settings)

osv_service_instance = osv_service(service.data)
export_service_instance = export_service(service.data)
balance_service_instance = balance_service(service.data, settings_mgr.settings)
turnover_service_instance = turnover_service(service.data)

reference_service_instance = reference_service()

logger.info("Все сервисы инициализированы", "main")

@app.route("/api/accessibility", methods=['GET'])
def accessibility():
    logger.debug("Проверка доступности API", "main")
    return "SUCCESS"

@app.route("/api/entities", methods=['GET'])
def get_entities():
    logger.debug("Запрос списка сущностей", "main")
    return {
        "entities": ["ranges", "groups", "nomenclatures", "receipts", "storages", "transactions"],
        "formats": ["csv", "markdown", "json", "xml"]
    }

@app.route("/api/data/<entity_type>/<format_type>", methods=['GET'])
def get_data(entity_type: str, format_type: str):
    logger.info(f"Запрос данных: {entity_type} в формате {format_type}", "main", {
        "entity_type": entity_type,
        "format_type": format_type,
        "method": "GET"
    })
    
    entity_map = {
        "ranges": reposity.range_key(),
        "groups": reposity.group_key(),
        "nomenclatures": reposity.nomenclature_key(),
        "receipts": reposity.receipt_key(),
        "storages": reposity.storage_key(),
        "transactions": reposity.transaction_key()
    }

    if entity_type not in entity_map:
        logger.error(f"Неизвестный тип сущности: {entity_type}", "main")
        return {"error": f"Unknown entity type: {entity_type}"}, 400

    if format_type not in ["csv", "markdown", "json", "xml"]:
        logger.error(f"Неизвестный формат: {format_type}", "main")
        return {"error": f"Unknown format type: {format_type}"}, 400

    data = service.data.data.get(entity_map[entity_type], [])

    if not data:
        logger.warning(f"Нет данных для сущности: {entity_type}", "main")
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

    logger.info(f"Данные успешно возвращены: {entity_type}, записей: {len(data)}", "main")
    return Response(
        result,
        content_type=content_types.get(format_type, "text/plain")
    )

@app.route("/api/receipts", methods=['GET'])
def get_receipts():
    logger.debug("Запрос всех рецептов", "main")
    receipts = service.data.data.get(reposity.receipt_key(), [])
    factory_conv = convert_factory()

    result = []
    for receipt in receipts:
        converted_data = factory_conv.convert(receipt)
        result.append(converted_data)

    logger.info(f"Возвращено рецептов: {len(result)}", "main")
    return Response(
        json.dumps(result, ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8"
    )

@app.route("/api/receipt/<receipt_id>", methods=['GET'])
def get_receipt(receipt_id: str):
    logger.debug(f"Запрос рецепта с ID: {receipt_id}", "main")
    receipts = service.data.data.get(reposity.receipt_key(), [])
    factory_conv = convert_factory()

    found_receipt = None
    for receipt in receipts:
        if receipt.unique_code == receipt_id:
            found_receipt = receipt
            break

    if not found_receipt:
        logger.error(f"Рецепт с ID {receipt_id} не найден", "main")
        return {"error": f"Receipt with id {receipt_id} not found"}, 404

    converted_data = factory_conv.convert(found_receipt)

    logger.info(f"Рецепт с ID {receipt_id} успешно возвращен", "main")
    return Response(
        json.dumps(converted_data, ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8"
    )

@app.route("/api/reports/osv", methods=['GET'])
def get_osv_report():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    storage_id = request.args.get('storage_id')

    logger.info("Запрос отчета ОСВ", "main", {
        "start_date": start_date_str,
        "end_date": end_date_str,
        "storage_id": storage_id,
        "method": "GET"
    })

    if not all([start_date_str, end_date_str, storage_id]):
        logger.error("Отсутствуют обязательные параметры для отчета ОСВ", "main")
        return {"error": "Missing required parameters: start_date, end_date, storage_id"}, 400

    try:
        start_date = datetime.fromisoformat(start_date_str)
        end_date = datetime.fromisoformat(end_date_str)
    except ValueError as e:
        logger.error(f"Некорректный формат даты: {str(e)}", "main")
        return {"error": f"Invalid date format: {str(e)}"}, 400

    try:
        report_data = osv_service_instance.generate_osv_report(start_date, end_date, storage_id)

        logger.info(f"Отчет ОСВ успешно сформирован: {len(report_data)} записей", "main")
        return Response(
            json.dumps(report_data, ensure_ascii=False, indent=2),
            content_type="application/json; charset=utf-8"
        )

    except operation_exception as e:
        logger.error(f"Ошибка при формировании отчета ОСВ: {str(e)}", "main")
        return {"error": str(e)}, 400
    except Exception as e:
        logger.error(f"Внутренняя ошибка сервера: {str(e)}", "main")
        return {"error": f"Internal server error: {str(e)}"}, 500

@app.route("/api/save-to-file", methods=['POST', 'GET'])
def save_to_file():
    logger.info("Запрос сохранения данных в файл", "main")
    filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    try:
        success = export_service_instance.export_all_data(filename)

        if success:
            logger.info(f"Данные успешно сохранены в файл: {filename}", "main")
            return {
                "message": f"Data saved to {filename}",
                "filename": filename,
                "success": True
            }
        else:
            logger.error("Не удалось сохранить данные", "main")
            return {"error": "Failed to save data", "success": False}, 500

    except Exception as e:
        logger.error(f"Ошибка при сохранении данных: {str(e)}", "main")
        return {"error": str(e), "success": False}, 500

@app.route("/api/filters/<model_type>", methods=['GET'])
def get_filters_by_model(model_type: str):
    logger.debug(f"Запрос фильтров для модели: {model_type}", "main")
    model_map = {
        "ranges": reposity.range_key(),
        "groups": reposity.group_key(),
        "nomenclatures": reposity.nomenclature_key(),
        "receipts": reposity.receipt_key(),
        "storages": reposity.storage_key(),
        "transactions": reposity.transaction_key()
    }

    if model_type not in model_map:
        logger.error(f"Неизвестный тип модели: {model_type}", "main")
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
        logger.warning(f"Нет данных для модели: {model_type}", "main")
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

    logger.debug(f"Возвращены фильтры для модели: {model_type}, полей: {len(fields_name)}", "main")
    return Response(
        json.dumps(result, ensure_ascii=False, indent=2),
        status=200,
        content_type="application/json; charset=utf-8"
    )

@app.route("/api/data/<model_type>/<format_type>", methods=['POST'])
def get_data_filtered(model_type: str, format_type: str):
    try:
        filters_data = request.get_json()
        
        logger.info(f"Запрос данных с фильтрацией: {model_type} в формате {format_type}", "main", {
            "model_type": model_type,
            "format_type": format_type,
            "method": "POST",
            "filters_count": len(filters_data) if filters_data else 0
        })

        if not filters_data or not isinstance(filters_data, list):
            logger.error("Ожидается массив фильтров в теле запроса", "main")
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
            logger.error(f"Неизвестный тип модели: {model_type}", "main")
            return Response(
                json.dumps({
                    "success": False,
                    "error": f"Unknown model type: {model_type}. Available: {list(model_map.keys())}"
                }, ensure_ascii=False),
                status=400,
                content_type="application/json; charset=utf-8"
            )

        if format_type not in ["csv", "markdown", "json", "xml"]:
            logger.error(f"Неизвестный формат: {format_type}", "main")
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
            logger.warning(f"Нет данных для модели: {model_type}", "main")
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

        logger.info(f"Данные с фильтрацией успешно возвращены: {model_type}, записей: {len(filtered_data)}", "main")
        return Response(
            result,
            content_type=content_types.get(format_type, "text/plain")
        )

    except operation_exception as e:
        logger.error(f"Ошибка операции: {str(e)}", "main")
        return Response(
            json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False),
            status=400,
            content_type="application/json; charset=utf-8"
        )
    except Exception as e:
        logger.error(f"Внутренняя ошибка сервера: {str(e)}", "main", {"exception": str(e)})
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
    try:
        filters_data = request.get_json()
        
        logger.info("Запрос отчета ОСВ с фильтрами", "main", {
            "method": "POST",
            "filters_count": len(filters_data) if filters_data else 0
        })

        if not filters_data or not isinstance(filters_data, list):
            logger.error("Ожидается массив фильтров в теле запроса", "main")
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

        logger.info(f"Отчет ОСВ с фильтрами успешно сформирован: {len(report_data)} записей", "main")
        return Response(
            json.dumps({
                "success": True,
                "count": len(report_data),
                "data": report_data
            }, ensure_ascii=False, indent=2),
            content_type="application/json; charset=utf-8"
        )

    except operation_exception as e:
        logger.error(f"Ошибка при формировании отчета ОСВ: {str(e)}", "main")
        return Response(
            json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False),
            status=400,
            content_type="application/json; charset=utf-8"
        )
    except Exception as e:
        logger.error(f"Внутренняя ошибка сервера: {str(e)}", "main")
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
    try:
        data = request.get_json()
        
        logger.info("Запрос установки даты блокировки", "main", {
            "method": "POST",
            "data": data
        })
        
        if not data or 'block_period' not in data:
            logger.error("Отсутствует параметр block_period", "main")
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
            
            turnover_service_instance.calculate_turnovers_to_block_period(block_period)
            
            turnover_service_instance.save_turnovers_to_file("turnovers_cache.json")
            
            success = settings_mgr.set_block_period(block_period)
            
            if success:
                dto = block_date_dto().create({"new_block_date": block_period})
                observe_service.create_event(event_type.change_block_period(), dto)
                
                logger.info(f"Дата блокировки успешно установлена: {block_period.isoformat()}", "main")
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
                logger.error("Не удалось сохранить дату блокировки", "main")
                return Response(
                    json.dumps({
                        "success": False,
                        "error": "Failed to save block period"
                    }, ensure_ascii=False),
                    status=500,
                    content_type="application/json; charset=utf-8"
                )
                
        except ValueError as e:
            logger.error(f"Некорректный формат даты: {str(e)}", "main")
            return Response(
                json.dumps({
                    "success": False,
                    "error": f"Invalid date format: {str(e)}"
                }, ensure_ascii=False),
                status=400,
                content_type="application/json; charset=utf-8"
            )
            
    except Exception as e:
        logger.error(f"Внутренняя ошибка сервера: {str(e)}", "main")
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
    try:
        logger.debug("Запрос текущей даты блокировки", "main")
        block_period = settings_mgr.get_block_period()
        
        result = {
            "success": True,
            "block_period": block_period.isoformat() if block_period else None
        }
        
        logger.debug(f"Возвращена дата блокировки: {result['block_period']}", "main")
        return Response(
            json.dumps(result, ensure_ascii=False),
            status=200,
            content_type="application/json; charset=utf-8"
        )
        
    except Exception as e:
        logger.error(f"Внутренняя ошибка сервера: {str(e)}", "main")
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
    try:
        date_str = request.args.get('date')
        storage_id = request.args.get('storage_id')
        
        logger.info("Запрос остатков", "main", {
            "date": date_str,
            "storage_id": storage_id,
            "method": "GET"
        })
        
        if not date_str:
            logger.error("Отсутствует параметр date", "main")
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
            
            turnover_service_instance.load_turnovers_from_file("turnovers_cache.json")
            
            balances = balance_service_instance.calculate_balance_with_block_period(
                target_date, storage_id
            )
            
            logger.info(f"Остатки успешно рассчитаны: {len(balances)} записей", "main")
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
            logger.error(f"Некорректный формат даты: {str(e)}", "main")
            return Response(
                json.dumps({
                    "success": False,
                    "error": f"Invalid date format: {str(e)}"
                }, ensure_ascii=False),
                status=400,
                content_type="application/json; charset=utf-8"
            )
        except operation_exception as e:
            logger.error(f"Ошибка операции: {str(e)}", "main")
            return Response(
                json.dumps({
                    "success": False,
                    "error": str(e)
                }, ensure_ascii=False),
                status=400,
                content_type="application/json; charset=utf-8"
            )
            
    except Exception as e:
        logger.error(f"Внутренняя ошибка сервера: {str(e)}", "main")
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
    try:
        item_id = request.args.get('id')
        
        logger.info(f"Запрос элемента справочника: {reference_type}", "main", {
            "reference_type": reference_type,
            "item_id": item_id,
            "method": "GET"
        })
        
        if item_id:
            factory_conv = convert_factory()
            
            model_map = {
                "nomenclature": reposity.nomenclature_key(),
                "group": reposity.group_key(),
                "range": reposity.range_key(),
                "storage": reposity.storage_key()
            }
            
            if reference_type not in model_map:
                logger.error(f"Неизвестный тип справочника: {reference_type}", "main")
                return {"error": f"Unknown reference type: {reference_type}"}, 400
            
            key = model_map[reference_type]
            items = service.data.data.get(key, [])
            
            item = None
            for it in items:
                if it.unique_code == item_id:
                    item = it
                    break
            
            if not item:
                logger.error(f"Элемент с ID {item_id} не найден", "main")
                return {"error": f"Item with id {item_id} not found"}, 404
            
            result = factory_conv.convert(item)
            
            logger.info(f"Элемент справочника {reference_type} с ID {item_id} успешно возвращен", "main")
            return Response(
                json.dumps(result, ensure_ascii=False, indent=2),
                content_type="application/json; charset=utf-8"
            )
        else:
            logger.error("ID параметр обязателен для GET запроса", "main")
            return {"error": "ID parameter is required for GET"}, 400
            
    except Exception as e:
        logger.error(f"Внутренняя ошибка сервера: {str(e)}", "main")
        return {"error": f"Internal server error: {str(e)}"}, 500

@app.route("/api/reference/<reference_type>", methods=['PUT'])
def add_reference(reference_type: str):
    """
    Добавить новый элемент справочника
    """
    try:
        data = request.get_json()
        
        logger.info(f"Добавление элемента справочника: {reference_type}", "main", {
            "reference_type": reference_type,
            "method": "PUT",
            "data": data
        })
        
        if not data:
            logger.error("Не предоставлены данные", "main")
            return {"error": "No data provided"}, 400
        
        reference_service.add(reference_type, data)
        
        logger.info(f"Элемент справочника {reference_type} успешно добавлен", "main")
        return {
            "success": True,
            "message": f"Reference {reference_type} added successfully"
        }
            
    except argument_exception as e:
        logger.error(f"Ошибка аргумента: {str(e)}", "main")
        return {"error": str(e)}, 400
    except operation_exception as e:
        logger.error(f"Ошибка операции: {str(e)}", "main")
        return {"error": str(e)}, 400
    except Exception as e:
        logger.error(f"Внутренняя ошибка сервера: {str(e)}", "main")
        return {"error": f"Internal server error: {str(e)}"}, 500

@app.route("/api/reference/<reference_type>", methods=['PATCH'])
def update_reference(reference_type: str):
    """
    Изменить элемент справочника
    """
    try:
        data = request.get_json()
        
        logger.info(f"Изменение элемента справочника: {reference_type}", "main", {
            "reference_type": reference_type,
            "method": "PATCH",
            "data": data
        })
        
        if not data:
            logger.error("Не предоставлены данные", "main")
            return {"error": "No data provided"}, 400
        
        if 'unique_code' not in data:
            logger.error("Отсутствует unique_code", "main")
            return {"error": "unique_code is required"}, 400
        
        reference_service.change(reference_type, data)
        
        logger.info(f"Элемент справочника {reference_type} успешно изменен", "main")
        return {
            "success": True,
            "message": f"Reference {reference_type} updated successfully"
        }
            
    except argument_exception as e:
        logger.error(f"Ошибка аргумента: {str(e)}", "main")
        return {"error": str(e)}, 400
    except operation_exception as e:
        logger.error(f"Ошибка операции: {str(e)}", "main")
        return {"error": str(e)}, 404
    except Exception as e:
        logger.error(f"Внутренняя ошибка сервера: {str(e)}", "main")
        return {"error": f"Internal server error: {str(e)}"}, 500

@app.route("/api/reference/<reference_type>", methods=['DELETE'])
def delete_reference(reference_type: str):
    """
    Удалить элемент справочника
    """
    try:
        data = request.get_json()
        
        logger.info(f"Удаление элемента справочника: {reference_type}", "main", {
            "reference_type": reference_type,
            "method": "DELETE",
            "data": data
        })
        
        if not data:
            logger.error("Не предоставлены данные", "main")
            return {"error": "No data provided"}, 400
        
        if 'unique_code' not in data:
            logger.error("Отсутствует unique_code", "main")
            return {"error": "unique_code is required"}, 400
        
        reference_service.remove(reference_type, data)
        
        logger.info(f"Элемент справочника {reference_type} успешно удален", "main")
        return {
            "success": True,
            "message": f"Reference {reference_type} deleted successfully"
        }
            
    except argument_exception as e:
        logger.error(f"Ошибка аргумента: {str(e)}", "main")
        return {"error": str(e)}, 400
    except operation_exception as e:
        logger.error(f"Ошибка операции: {str(e)}", "main")
        return {"error": str(e)}, 409
    except Exception as e:
        logger.error(f"Внутренняя ошибка сервера: {str(e)}", "main")
        return {"error": f"Internal server error: {str(e)}"}, 500

if __name__ == '__main__':
    logger.info("Запуск сервера на localhost:8080", "main")
    app.run(host="localhost", port=8080)
