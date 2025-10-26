from Src.Core.abstract_response import abstract_response
from Src.Core.common import common
from Src.Core.validator import validator, operation_exception
from Src.Logics.convert_factory import convert_factory
import json


class response_json(abstract_response):
    def build(self, data: list) -> str:
        super().build(data)

        result = []
        factory = convert_factory()
        
        for item in data:
            # Используем фабрику конвертеров для преобразования объекта
            converted_data = factory.convert(item)
            result.append(converted_data)

        return json.dumps(result, ensure_ascii=False, indent=2)
