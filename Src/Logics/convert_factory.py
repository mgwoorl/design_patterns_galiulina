from Src.Core.abstract_covertor import abstract_covertor
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor
from Src.Core.validator import validator
from Src.Core.abstract_model import abstact_model
from Src.Core.common import common
from datetime import datetime

"""
Фабрика конвертеров по шаблону "Фабрика".
Управляет созданием и использованием конверторов с рекурсивной обработкой
"""

class convert_factory:

    def __init__(self):
        self.__convertors = {
            "basic": basic_convertor(),
            "datetime": datetime_convertor(),
            "reference": reference_convertor()
        }

    def convert(self, obj: object) -> dict:
        """
        Конвертирует любой объект любого типа в словарь.

        Args:
            obj: любой объект для конвертации

        Returns:
            dict: объединенный словарь от всех конвертеров
        """
        validator.validate(obj, object)

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
                converted_value = self._convert_value(field, value)

                if converted_value is not None:
                    result[field] = converted_value

            except Exception:
                # Пропускаем поля, к которым нет доступа
                continue

        return result

    def _convert_value(self, field_name: str, value) -> any:
        """
        Конвертирует значение в зависимости от типа

        Args:
            field_name: имя поля
            value: значение для конвертации

        Returns:
            any: сериализуемое значение
        """
        # Обрабатываем None
        if value is None:
            return None

        # Обрабатываем базовые типы
        if isinstance(value, (int, float, str, bool)):
            result = self.__convertors["basic"].convert(field_name, value)
            return list(result.values())[0] if result else value

        # Обрабатываем datetime
        elif isinstance(value, datetime):
            result = self.__convertors["datetime"].convert(field_name, value)
            return list(result.values())[0] if result else value

        # Обрабатываем reference типы (модели)
        elif isinstance(value, abstact_model):
            result = self.__convertors["reference"].convert(field_name, value)
            return list(result.values())[0] if result else value

        # Обрабатываем списки рекурсивно
        elif isinstance(value, list):
            converted_list = []
            for item in value:
                if item is None:
                    continue
                elif isinstance(item, abstact_model):
                    # Рекурсивно конвертируем объекты в списке
                    converted_item = self.convert(item)
                    if converted_item:
                        converted_list.append(converted_item)
                else:
                    converted_list.append(item)
            return converted_list if converted_list else None

        # Для остальных типов возвращаем как есть
        else:
            return value
