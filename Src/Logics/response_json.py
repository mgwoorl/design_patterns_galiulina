from Src.Core.abstract_response import abstract_response
from Src.Core.common import common
from Src.Core.validator import validator, operation_exception
from Src.Logics.convert_factory import convert_factory
import json


class response_json(abstract_response):
    
    def build(self, data: list) -> str:
        super().build(data)

        # Используем фабрику для конвертации данных
        factory = convert_factory()
        result = []
        
        for item in data:
            # Конвертируем каждый объект через фабрику
            converted_item = factory.convert(item)
            result.append(converted_item)

        return json.dumps(result, ensure_ascii=False, indent=2)
