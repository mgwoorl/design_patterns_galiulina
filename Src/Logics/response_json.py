from Src.Core.abstract_response import abstract_response
from Src.Core.common import common
from Src.Core.validator import validator, operation_exception
from Src.Logics.convert_factory import convert_factory
import json


class response_json(abstract_response):
    def __init__(self):
        self.convert_factory_instance = convert_factory()

    def build(self, data: list) -> str:
        super().build(data)

        result = []

        for item in data:
            # Конвертируем каждый объект через фабрику
            converted_item = self.convert_factory_instance.convert(item)
            result.append(converted_item)

        return json.dumps(result, ensure_ascii=False, indent=2)
