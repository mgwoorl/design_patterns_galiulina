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
from datetime import datetime
import json

"""
Главный модуль приложения
"""
app = connexion.FlaskApp(__name__)

service = start_service()

settings_mgr = settings_manager()
settings_mgr.file_name = "settings.json"
settings_mgr.load()

if settings_mgr.settings.is_first_start:
    service.start()
    settings_mgr.settings.is_first_start = False
    settings_mgr.save()
else:
    service.data.initalize()

settings = settings_model()
factory = factory_entities(settings)

osv_service_instance = osv_service(service.data)
export_service_instance = export_service(service.data)


@app.route("/api/accessibility", methods=['GET'])
def accessibility():
    return "SUCCESS"


@app.route("/api/entities", methods=['GET'])
def get_entities():
    return {
        "entities": ["ranges", "groups", "nomenclatures", "receipts", "storages", "transactions"],
        "formats": ["csv", "markdown", "json", "xml"]
    }


@app.route("/api/data/<entity_type>/<format_type>", methods=['GET'])
def get_data(entity_type: str, format_type: str):
    entity_map = {
        "ranges": reposity.range_key(),
        "groups": reposity.group_key(),
        "nomenclatures": reposity.nomenclature_key(),
        "receipts": reposity.receipt_key(),
        "storages": reposity.storage_key(),
        "transactions": reposity.transaction_key()
    }

    if entity_type not in entity_map:
        return {"error": f"Unknown entity type: {entity_type}"}, 400

    if format_type not in ["csv", "markdown", "json", "xml"]:
        return {"error": f"Unknown format type: {format_type}"}, 400

    data = service.data.data.get(entity_map[entity_type], [])

    if not data:
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

    return Response(
        result,
        content_type=content_types.get(format_type, "text/plain")
    )


@app.route("/api/receipts", methods=['GET'])
def get_receipts():
    receipts = service.data.data.get(reposity.receipt_key(), [])
    factory = convert_factory()

    result = []
    for receipt in receipts:
        converted_data = factory.convert(receipt)
        result.append(converted_data)

    return Response(
        json.dumps(result, ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8"
    )


@app.route("/api/receipt/<receipt_id>", methods=['GET'])
def get_receipt(receipt_id: str):
    receipts = service.data.data.get(reposity.receipt_key(), [])
    factory = convert_factory()

    found_receipt = None
    for receipt in receipts:
        if receipt.unique_code == receipt_id:
            found_receipt = receipt
            break

    if not found_receipt:
        return {"error": f"Receipt with id {receipt_id} not found"}, 404

    converted_data = factory.convert(found_receipt)

    return Response(
        json.dumps(converted_data, ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8"
    )


@app.route("/api/reports/osv", methods=['GET'])
def get_osv_report():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    storage_id = request.args.get('storage_id')

    if not all([start_date_str, end_date_str, storage_id]):
        return {"error": "Missing required parameters: start_date, end_date, storage_id"}, 400

    try:
        start_date = datetime.fromisoformat(start_date_str)
        end_date = datetime.fromisoformat(end_date_str)
    except ValueError as e:
        return {"error": f"Invalid date format: {str(e)}"}, 400

    try:
        report_data = osv_service_instance.generate_osv_report(start_date, end_date, storage_id)

        return Response(
            json.dumps(report_data, ensure_ascii=False, indent=2),
            content_type="application/json; charset=utf-8"
        )

    except operation_exception as e:
        return {"error": str(e)}, 400
    except Exception as e:
        return {"error": f"Internal server error: {str(e)}"}, 500


@app.route("/api/save-to-file", methods=['POST', 'GET'])
def save_to_file():
    filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    try:
        success = export_service_instance.export_all_data(filename)

        if success:
            return {
                "message": f"Data saved to {filename}",
                "filename": filename,
                "success": True
            }
        else:
            return {"error": "Failed to save data", "success": False}, 500

    except Exception as e:
        return {"error": str(e), "success": False}, 500

@app.route("/api/filters/<model_type>", methods=['GET'])
def get_filters_by_model(model_type: str):
    """
    Возвращает поля, по которым можно сделать фильтр, и типы фильтрации
    """
    model_map = {
        "ranges": reposity.range_key(),
        "groups": reposity.group_key(),
        "nomenclatures": reposity.nomenclature_key(),
        "receipts": reposity.receipt_key(),
        "storages": reposity.storage_key(),
        "transactions": reposity.transaction_key()
    }

    if model_type not in model_map:
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

    return Response(
        json.dumps(result, ensure_ascii=False, indent=2),
        status=200,
        content_type="application/json; charset=utf-8"
    )


@app.route("/api/data/<model_type>/<format_type>", methods=['POST'])
def get_data_filtered(model_type: str, format_type: str):
    """
    Получить отфильтрованные данные в указанном формате
    """
    try:
        filters_data = request.get_json()

        if not filters_data or not isinstance(filters_data, list):
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
            return Response(
                json.dumps({
                    "success": False,
                    "error": f"Unknown model type: {model_type}. Available: {list(model_map.keys())}"
                }, ensure_ascii=False),
                status=400,
                content_type="application/json; charset=utf-8"
            )

        if format_type not in ["csv", "markdown", "json", "xml"]:
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

        return Response(
            result,
            content_type=content_types.get(format_type, "text/plain")
        )

    except operation_exception as e:
        return Response(
            json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False),
            status=400,
            content_type="application/json; charset=utf-8"
        )
    except Exception as e:
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
    """
    Генерация отчета ОСВ с использованием DTO фильтров
    """
    try:
        filters_data = request.get_json()

        if not filters_data or not isinstance(filters_data, list):
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

        return Response(
            json.dumps({
                "success": True,
                "count": len(report_data),
                "data": report_data
            }, ensure_ascii=False, indent=2),
            content_type="application/json; charset=utf-8"
        )

    except operation_exception as e:
        return Response(
            json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False),
            status=400,
            content_type="application/json; charset=utf-8"
        )
    except Exception as e:
        return Response(
            json.dumps({
                "success": False,
                "error": f"Internal server error: {str(e)}"
            }, ensure_ascii=False),
            status=500,
            content_type="application/json; charset=utf-8"
        )


if __name__ == '__main__':
    app.run(host="localhost", port=8080)
