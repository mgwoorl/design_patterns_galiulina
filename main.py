import connexion
from flask import request, Response
from Src.start_service import start_service
from Src.Logics.factory_entities import factory_entities
from Src.Models.settings_model import settings_model, ResponseFormat
from Src.reposity import reposity

app = connexion.FlaskApp(__name__)
service = start_service()
service.start()

"""
Проверить доступность REST API
"""


@app.route("/api/accessibility", methods=['GET'])
def formats():
    return "SUCCESS"


"""
Получить данные в указанном формате
"""


@app.route("/api/data/<entity_type>/<format_type>", methods=['GET'])
def get_data(entity_type: str, format_type: str):
    try:
        # Маппинг типов сущностей
        entity_map = {
            "ranges": reposity.range_key(),
            "groups": reposity.group_key(),
            "nomenclatures": reposity.nomenclature_key(),
            "receipts": reposity.receipt_key()
        }

        # Маппинг форматов
        format_map = {
            "csv": ResponseFormat.CSV,
            "markdown": ResponseFormat.MARKDOWN,
            "json": ResponseFormat.JSON,
            "xml": ResponseFormat.XML
        }

        if entity_type not in entity_map:
            return {"error": "Unknown entity type"}, 400

        if format_type not in format_map:
            return {"error": "Unknown format type"}, 400

        # Получение данных
        data = service.data.get(entity_map[entity_type], [])

        # Создание форматера
        settings = settings_model()
        settings.response_format = format_map[format_type]
        factory = factory_entities(settings)
        formatter = factory.create_default(data)

        # Формирование ответа
        result = formatter.build(data)

        # Установка Content-Type
        content_types = {
            "csv": "text/csv",
            "markdown": "text/markdown",
            "json": "application/json",
            "xml": "application/xml"
        }

        return Response(
            result,
            content_type=content_types[format_type],
            headers={'Content-Disposition': f'attachment; filename={entity_type}.{format_type}'}
        )

    except Exception as e:
        return {"error": str(e)}, 500


"""
Получить список доступных типов данных
"""


@app.route("/api/entities", methods=['GET'])
def get_entities():
    return {
        "entities": ["ranges", "groups", "nomenclatures", "receipts"],
        "formats": ["csv", "markdown", "json", "xml"]
    }


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)