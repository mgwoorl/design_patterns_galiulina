import connexion
from flask import Response
from Src.start_service import start_service
from Src.Logics.factory_entities import factory_entities
from Src.Models.settings_model import settings_model, ResponseFormat
from Src.reposity import reposity
from Src.Logics.convert_factory import convert_factory
from Src.Logics.osv_service import osv_service
from Src.Logics.export_service import export_service
from Src.settings_manager import settings_manager
from Src.Core.validator import argument_exception, operation_exception
from datetime import datetime
import json

app = connexion.FlaskApp(__name__)

# Инициализация сервисов
service = start_service()

# Загрузка настроек и проверка первого старта
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

    data = service.data.get(entity_map[entity_type], [])

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
    receipts = service.data.get(reposity.receipt_key(), [])
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
    receipts = service.data.get(reposity.receipt_key(), [])
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
    start_date_str = connexion.request.args.get('start_date')
    end_date_str = connexion.request.args.get('end_date')
    storage_id = connexion.request.args.get('storage_id')

    if not all([start_date_str, end_date_str, storage_id]):
        return {"error": "Missing required parameters: start_date, end_date, storage_id"}, 400

    try:
        start_date = datetime.fromisoformat(start_date_str)
        end_date = datetime.fromisoformat(end_date_str)
    except ValueError as e:
        raise argument_exception(f"Неверный формат даты: {str(e)}")

    report_data = osv_service_instance.generate_osv_report(start_date, end_date, storage_id)

    return Response(
        json.dumps(report_data, ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8"
    )


@app.route("/api/save-to-file", methods=['POST'])
def save_to_file():
    filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    success = export_service_instance.export_all_data(filename)

    if success:
        return {"message": f"Data saved to {filename}", "filename": filename}
    else:
        return {"error": "Failed to save data"}, 500


if __name__ == '__main__':
    app.run(host="localhost", port=8080)
