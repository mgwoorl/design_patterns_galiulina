from Src.Core.abstract_covertor import abstract_covertor
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor
from Src.Core.validator import validator
from Src.Core.abstract_model import abstact_model

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

        # Получаем все доступные поля объекта
        fields = self._get_accessible_fields(obj)

        for field_name in fields:
            try:
                attr_value = getattr(obj, field_name)

                # Рекурсивно обрабатываем значение
                converted_value = self._convert_value(field_name, attr_value)

                if converted_value is not None:
                    # Очищаем имя поля от префиксов моделей для лучшей читаемости
                    clean_field_name = self._clean_field_name(field_name)
                    result[clean_field_name] = converted_value

            except Exception:
                # Пропускаем поля, к которым нет доступа
                continue

        return result

    def _get_accessible_fields(self, obj: object) -> list:
        """
        Получает все доступные поля объекта, исключая системные
        """
        fields = []

        # Получаем все атрибуты объекта
        for attr_name in dir(obj):
            # Пропускаем системные методы и атрибуты
            if attr_name.startswith('__') and attr_name.endswith('__'):
                continue

            # Пропускаем методы
            if callable(getattr(obj, attr_name)):
                continue

            # Пропускаем приватные поля, которые не относятся к нашим моделям
            if attr_name.startswith('_') and not self._is_model_private_field(attr_name):
                continue

            fields.append(attr_name)

        return fields

    def _is_model_private_field(self, field_name: str) -> bool:
        """
        Проверяет, является ли приватное поле полем нашей модели
        """
        model_prefixes = ['_abstact_model__', '_entity_model__', '_receipt_model__',
                          '_range_model__', '_group_model__', '_nomenclature_model__',
                          '_company_model__', '_storage_model__']
        return any(field_name.startswith(prefix) for prefix in model_prefixes)

    def _clean_field_name(self, field_name: str) -> str:
        """
        Очищает имя поля от префиксов моделей
        """
        # Убираем префиксы типа _receipt_model__
        if field_name.startswith('_') and '__' in field_name:
            parts = field_name.split('__')
            if len(parts) > 1:
                return parts[-1]
        return field_name

    def _convert_value(self, field_name: str, value) -> any:
        """
        Рекурсивно конвертирует значение с использованием всех конвертеров

        Args:
            field_name: имя поля
            value: значение для конвертации

        Returns:
            any: сериализуемое значение
        """
        # Обрабатываем None
        if value is None:
            return None

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
        if item is None:
            return None

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
                hasattr(value, '__dict__') and
                not self._is_system_object(value))

    def _is_system_object(self, value) -> bool:
        """
        Проверяет, является ли объект системным (не сериализуемым)
        """
        # Проверяем класс объекта на системные типы
        class_name = value.__class__.__name__
        system_classes = ['_abc_data', 'type', 'module', 'function', 'method']
        return any(sys_class in class_name for sys_class in system_classes)
