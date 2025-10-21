from Src.Core.abstract_response import abstract_response
from Src.Core.common import common
from Src.Core.validator import validator, operation_exception


class response_csv(abstract_response):
    def build(self, data: list) -> str:
        super().build(data)

        if len(data) == 0:
            return ""

        text = ""
        # Шапка
        item = data[0]
        fields = common.get_fields(item)
        text += ";".join(fields) + "\n"

        # Данные
        for item in data:
            row = []
            for field in fields:
                value = getattr(item, field, "")
                # Преобразуем сложные объекты в строки
                if hasattr(value, 'name'):
                    row.append(str(value.name))
                elif hasattr(value, 'unique_code'):
                    row.append(str(value.unique_code))
                else:
                    row.append(str(value))
            text += ";".join(row) + "\n"

        return text