from enum import Enum

"""
Перечисление типов фильтров для операций сравнения
"""
class FilterType(Enum):
    EQUALS = "EQUALS"           # Полное совпадение
    LIKE = "LIKE"               # Вхождение строки
    GREATER = "GREATER"         # Больше
    GREATER_EQUAL = "GREATER_EQUAL"  # Больше или равно
    LESS = "LESS"               # Меньше
    LESS_EQUAL = "LESS_EQUAL"   # Меньше или равно
    NOT_EQUAL = "NOT_EQUAL"     # Не равно

    @classmethod
    def get_all_types(cls) -> list:
        """
        Возвращает список всех доступных типов фильтров
        
        Returns:
            list: список значений перечисления
        """
        return [member.value for member in cls]
