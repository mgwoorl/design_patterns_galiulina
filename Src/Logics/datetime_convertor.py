from Src.Core.abstract_covertor import abstract_covertor
from datetime import datetime

"""
Конвертор для типа DateTime.
Обрабатывает поля с датой и временем
"""

class datetime_convertor(abstract_covertor):

    def convert(self, field_name: str, value) -> dict:
        """
        Конвертирует значение поля в сериализуемый формат

        Args:
            field_name (str): наименование поля
            value: значение поля

        Returns:
            dict: словарь с конвертированным значением или пустой словарь
        """
        # Обрабатываем datetime
        if isinstance(value, datetime):
            return {field_name: value.strftime("%Y-%m-%d %H:%M:%S")}

        return {}

    def can_convert(self, value) -> bool:
        """
        Проверяет, может ли конвертор обработать данный тип значения

        Args:
            value: значение для проверки

        Returns:
            bool: True если конвертор может обработать значение
        """
        return isinstance(value, datetime)
