from Src.Core.abstract_covertor import abstract_covertor
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor
from Src.Core.validator import validator
from Src.Core.abstract_model import abstact_model
from Src.Core.common import common

"""
Фабрика конвертеров по шаблону "Фабрика".
Управляет созданием и использованием конверторов с рекурсивной обработкой
"""

class convert_factory:

    def __init__(self):
        """
        Инициализация фабрики конверторов
        """
        self._convertors = [
            basic_convertor(),
            datetime_convertor(), 
            reference_convertor()
        ]
    
    def convert(self, obj) -> dict:
        """
        Конвертирует любой объект любого типа в словарь.
        
        Args:
            obj: любой объект для конвертации
            
        Returns:
            dict: объединенный словарь от всех конвертеров
        """
        if obj is None:
            return {}
            
        result = {}

        # Для моделей используем common.get_fields(), для обычных объектов - dir()
        if isinstance(obj, abstact_model):
            fields = common.get_fields(obj)
        else:
            # Для обычных объектов используем dir() и фильтруем приватные поля
            fields = [attr for attr in dir(obj) if not attr.startswith('_') and not callable(getattr(obj, attr))]

        for field in fields:
            try:
                value = getattr(obj, field)

                # Обрабатываем значение в зависимости от типа
                converted_value = self._convert_value(value)

                if converted_value is not None:
                    result[field] = converted_value

            except Exception:
                # Пропускаем поля, к которым нет доступа
                continue

        return result
    
    def _convert_value(self, value) -> any:
        """
        Конвертирует значение в зависимости от типа
        
        Args:
            value: значение для конвертации
            
        Returns:
            any: сериализуемое значение
        """
        # Обрабатываем None
        if value is None:
            return None
            
        # Обрабатываем списки рекурсивно
        if isinstance(value, list):
            converted_list = []
            for item in value:
                converted_item = self._convert_value(item)
                if converted_item is not None:
                    converted_list.append(converted_item)
            return converted_list if converted_list else None
        
        # Обрабатываем модели рекурсивно
        if isinstance(value, abstact_model):
            return self.convert(value)
        
        # Ищем подходящий конвертор через can_convert
        convertor = self._find_convertor(value)
        if convertor:
            result_dict = convertor.convert("field", value)
            return list(result_dict.values())[0] if result_dict else value
        
        # Для остальных типов возвращаем как есть
        return value
    
    def _find_convertor(self, value) -> abstract_covertor:
        """
        Находит подходящий конвертор для значения через can_convert
        
        Args:
            value: значение для конвертации
            
        Returns:
            abstract_covertor: подходящий конвертор или None
        """
        for convertor in self._convertors:
            if convertor.can_convert(value):
                return convertor
        return None
