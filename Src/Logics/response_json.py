from Src.Core.abstract_response import abstract_response
from Src.Core.common import common
from Src.Core.validator import validator, operation_exception
import json


class response_json(abstract_response):
    def build(self, data: list) -> str:
        super().build(data)

        result = []
        for item in data:
            item_dict = {}
            fields = common.get_fields(item)
            for field in fields:
                value = getattr(item, field, None)
                # Преобразуем сложные объекты в простые значения
                if hasattr(value, 'name'):
                    item_dict[field] = value.name
                elif hasattr(value, 'unique_code'):
                    item_dict[field] = value.unique_code
                else:
                    item_dict[field] = value
            result.append(item_dict)

        return json.dumps(result, ensure_ascii=False, indent=2)