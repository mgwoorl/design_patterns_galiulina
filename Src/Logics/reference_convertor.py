from Src.Core.abstract_covertor import abstract_covertor
from Src.Core.abstract_model import abstact_model

"""
Конвертор для ссылочных типов данных.
Преобразует объекты моделей в их идентификаторы и названия.
"""

class reference_convertor(abstract_covertor):
    
    def convert(self, field_name: str, value) -> dict:
        """
        Конвертирует значение поля в сериализуемый формат

        Args:
            field_name (str): наименование поля
            value: значение поля

        Returns:
            dict: словарь с конвертированным значением или пустой словарь
        """
        # Обрабатываем Reference типы (abstact_model и его наследники)
        if isinstance(value, abstact_model):
            result = {
                'unique_code': value.unique_code,
                'type': value.__class__.__name__
            }
            
            # Добавляем имя, если оно есть у объекта
            if hasattr(value, 'name'):
                result['name'] = value.name
                
            return {field_name: result}
            
        return {}
