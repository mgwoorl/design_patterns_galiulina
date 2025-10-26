import connexion
from flask import Response
from Src.start_service import start_service
from Src.Logics.factory_entities import factory_entities
from Src.Models.settings_model import settings_model, ResponseFormat
from Src.reposity import reposity
from Src.Logics.convert_factory import convert_factory
import json

app = connexion.FlaskApp(__name__)

# Инициализация сервиса
service = start_service()
service.start()

# Настройки по умолчанию
settings = settings_model()
factory = factory_entities(settings)

@app.route("/api/accessibility", methods=['GET'])
def accessibility():
    return "SUCCESS"

@app.route("/api/entities", methods=['GET'])
def get_entities():
    return {
        "entities": ["ranges", "groups", "nomenclatures", "receipts"],
        "formats": ["csv", "markdown", "json", "xml"]
    }

@app.route("/api/data/<entity_type>/<format_type>", methods=['GET'])
def get_data(entity_type: str, format_type: str):
    try:
        entity_map = {
            "ranges": reposity.range_key(),
            "groups": reposity.group_key(),
            "nomenclatures": reposity.nomenclature_key(),
            "receipts": reposity.receipt_key()
        }

        format_map = {
            "csv": ResponseFormat.CSV,
            "markdown": ResponseFormat.MARKDOWN,
            "json": ResponseFormat.JSON,
            "xml": ResponseFormat.XML
        }

        if entity_type not in entity_map:
            return {"error": f"Unknown entity type: {entity_type}"}, 400

        if format_type not in format_map:
            return {"error": f"Unknown format type: {format_type}"}, 400

        data = service.data.get(entity_map[entity_type], [])

        if not data:
            return {"error": f"No data for entity: {entity_type}"}, 404

        settings.response_format = format_map[format_type]
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

    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/api/receipts", methods=['GET'])
def get_receipts():
    """
    Возвращает список всех рецептов в JSON формате
    """
    try:
        receipts = service.data.get(reposity.receipt_key(), [])
        factory = convert_factory()
        
        result = []
        for receipt in receipts:
            # Используем фабрику конвертеров для преобразования рецепта
            converted_data = factory.convert(receipt)
            result.append(converted_data)
            
        return Response(
            json.dumps(result, ensure_ascii=False, indent=2),
            content_type="application/json; charset=utf-8"
        )
        
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/api/receipt/<receipt_id>", methods=['GET'])
def get_receipt(receipt_id: str):
    """
    Возвращает конкретный рецепт по указанному коду в JSON формате
    """
    try:
        receipts = service.data.get(reposity.receipt_key(), [])
        factory = convert_factory()
        
        # Ищем рецепт по unique_code
        found_receipt = None
        for receipt in receipts:
            if receipt.unique_code == receipt_id:
                found_receipt = receipt
                break
                
        if not found_receipt:
            return {"error": f"Receipt with id {receipt_id} not found"}, 404
            
        # Используем фабрику конвертеров для преобразования рецепта
        converted_data = factory.convert(found_receipt)
        
        return Response(
            json.dumps(converted_data, ensure_ascii=False, indent=2),
            content_type="application/json; charset=utf-8"
        )
        
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(host="localhost", port=8080)
