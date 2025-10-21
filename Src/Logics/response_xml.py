from Src.Core.abstract_response import abstract_response
from Src.Core.common import common
from Src.Core.validator import validator, operation_exception


class response_xml(abstract_response):
    def build(self, data: list) -> str:
        super().build(data)

        root_name = "items"
        if len(data) > 0:
            root_name = data[0].__class__.__name__.lower() + "s"

        xml_content = f'<?xml version="1.0" encoding="UTF-8"?>\n<{root_name}>\n'

        for item in data:
            item_name = item.__class__.__name__.lower()
            xml_content += f'  <{item_name}>\n'

            fields = common.get_fields(item)
            for field in fields:
                value = getattr(item, field, "")
                # Преобразуем сложные объекты в строки
                if hasattr(value, 'name'):
                    xml_content += f'    <{field}>{value.name}</{field}>\n'
                elif hasattr(value, 'unique_code'):
                    xml_content += f'    <{field}>{value.unique_code}</{field}>\n'
                else:
                    xml_content += f'    <{field}>{value}</{field}>\n'

            xml_content += f'  </{item_name}>\n'

        xml_content += f'</{root_name}>'
        return xml_content