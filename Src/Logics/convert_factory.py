from Src.Core.abstract_covertor import abstract_covertor
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor
from Src.Core.validator import validator

"""
Фабрика конвертеров по шаблону "Фабрика".
Управляет созданием и использованием конверторов с рекурсивной обработкой
"""

class convert_factory:
    
    def __init__(self):
        self.__convertors = [
            basic_convertor(),
            datetime_convertor(), 
            reference_convertor()
        ]
    
    def convert(self, obj: object) -> dict:
        """
        Конвертирует любой объект любого типа в словарь.
        Рекурсивно обрабатывает вложенные объекты согласно исходной структуры
        
        Args:
            obj: любой объект для конвертации
            
        Returns:
            dict: объединенный словарь от всех конвертеров
        """
        validator.validate(obj, object)
        
        result = {}
        
        # Получаем все поля объекта
        fields = self._get_all_fields(obj)
        
        for field_name in fields:
            try:
                # Пропускаем системные приватные поля
                if field_name.startswith('__') and field_name.endswith('__'):
                    continue
                    
                attr_value = getattr(obj, field_name)
                
                # Рекурсивно обрабатываем значение
                converted_value = self._convert_value(field_name, attr_value)
                
                if converted_value is not None:
                    result[field_name] = converted_value
                        
            except Exception as e:
                # Пропускаем поля, к которым нет доступа
                continue
                
        return result
    
    def _get_all_fields(self, obj: object) -> list:
        """
        Получает все поля объекта, включая свойства
        """
        fields = []
        
        # Получаем все атрибуты объекта
        for attr_name in dir(obj):
            # Пропускаем методы
            if callable(getattr(obj, attr_name)):
                continue
                
            fields.append(attr_name)
            
        return fields
    
    def _convert_value(self, field_name: str, value) -> any:
        """
        Рекурсивно конвертирует значение с использованием всех конвертеров
        
        Args:
            field_name: имя поля
            value: значение для конвертации
            
        Returns:
            any: сериализуемое значение
        """
        # Обрабатываем списки рекурсивно
        if isinstance(value, list):
            return [self._convert_list_item(item) for item in value]
        
        # Обрабатываем вложенные объекты рекурсивно
        elif self._is_complex_object(value):
            # Рекурсивный вызов для вложенного объекта
            return self.convert(value)
        
        # Используем все конвертеры для простых значений
        else:
            for convertor in self.__convertors:
                result = convertor.convert(field_name, value)
                if result:
                    return list(result.values())[0]
            return value
    
    def _convert_list_item(self, item) -> any:
        """
        Обрабатывает элемент списка рекурсивно
        """
        if self._is_complex_object(item):
            return self.convert(item)
        else:
            for convertor in self.__convertors:
                result = convertor.convert("item", item)
                if result:
                    return list(result.values())[0]
            return item
    
    def _is_complex_object(self, value) -> bool:
        """
        Проверяет, является ли значение сложным объектом для рекурсивной обработки
        """
        return (value is not None and 
                not isinstance(value, (int, float, str, bool, list)) and
                hasattr(value, '__dict__'))
