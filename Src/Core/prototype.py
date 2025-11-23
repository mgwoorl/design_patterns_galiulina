from Src.Core.validator import validator, argument_exception
from Src.Dtos.filter_dto import filter_dto
from Src.Core.filter_type import FilterType
from Src.Core.abstract_model import abstact_model
from datetime import datetime

"""
Класс-прототип для фильтрации данных с поддержкой различных операций сравнения
Поддерживает фильтрацию по всем DOMAIN моделям: номенклатура, группа, единица измерения, рецепт
"""
class prototype:
    __data: list = []

    @property
    def data(self):
        return self.__data

    def __init__(self, data: list):
        validator.validate(data, list)
        self.__data = data

    def clone(self, data: list = None) -> "prototype":
        """
        Создает клон прототипа с новыми данными
        
        Args:
            data (list): новые данные или None для копирования текущих
            
        Returns:
            prototype: новый объект прототипа
        """
        inner_data = data if data is not None else self.__data
        return prototype(inner_data)

    @staticmethod
    def filter(data: list, filters: list) -> list:
        """
        Фильтрует данные по списку фильтров
        
        Args:
            data (list): исходные данные
            filters (list): список объектов filter_dto
            
        Returns:
            list: отфильтрованные данные
        """
        if len(data) == 0:
            return data
            
        if len(filters) == 0:
            return data

        result = data

        for filter_dto in filters:
            filtered_result = []

            for item in result:
                if prototype._apply_filter(item, filter_dto):
                    filtered_result.append(item)

            result = filtered_result

        return result

    @staticmethod
    def _apply_filter(item, filter_dto: filter_dto) -> bool:
        """
        Применяет один фильтр к элементу
        
        Args:
            item: элемент данных
            filter_dto (filter_dto): DTO фильтра
            
        Returns:
            bool: True если элемент проходит фильтр
        """
        try:
            # Поддержка вложенных свойств через "/"
            if '/' in filter_dto.field_name:
                parts = filter_dto.field_name.split('/')
                current_value = item

                for part in parts:
                    if hasattr(current_value, part):
                        current_value = getattr(current_value, part)
                    else:
                        return False

                field_value = current_value
            else:
                # Работаем с объектами
                if hasattr(item, filter_dto.field_name):
                    field_value = getattr(item, filter_dto.field_name)
                else:
                    return False

            # Применяем фильтр в зависимости от типа
            return prototype._compare_values(field_value, filter_dto.value, filter_dto.type)

        except Exception:
            return False

    @staticmethod
    def _compare_values(field_value, filter_value: str, filter_type: FilterType) -> bool:
        """
        Сравнивает значения в зависимости от типа фильтра
        
        Args:
            field_value: значение поля
            filter_value (str): значение фильтра
            filter_type (FilterType): тип операции сравнения
            
        Returns:
            bool: результат сравнения
        """
        # Для строковых операций
        str_field_value = str(field_value)
        str_filter_value = str(filter_value)

        if filter_type == FilterType.EQUALS:
            return str_field_value == str_filter_value
        elif filter_type == FilterType.LIKE:
            return str_filter_value.lower() in str_field_value.lower()
        elif filter_type == FilterType.NOT_EQUAL:
            return str_field_value != str_filter_value
        else:
            # Числовое сравнение
            try:
                num_field = float(field_value)
                num_filter = float(filter_value)

                if filter_type == FilterType.GREATER:
                    return num_field > num_filter
                elif filter_type == FilterType.GREATER_EQUAL:
                    return num_field >= num_filter
                elif filter_type == FilterType.LESS:
                    return num_field < num_filter
                elif filter_type == FilterType.LESS_EQUAL:
                    return num_field <= num_filter
                else:
                    return str_field_value == str_filter_value

            except (ValueError, TypeError):
                # Строковое сравнение как fallback
                if filter_type == FilterType.GREATER:
                    return str_field_value > str_filter_value
                elif filter_type == FilterType.GREATER_EQUAL:
                    return str_field_value >= str_filter_value
                elif filter_type == FilterType.LESS:
                    return str_field_value < str_filter_value
                elif filter_type == FilterType.LESS_EQUAL:
                    return str_field_value <= str_filter_value
                else:
                    return str_field_value == str_filter_value
