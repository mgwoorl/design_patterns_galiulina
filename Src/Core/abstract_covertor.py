import abc
from Src.Core.validator import validator

"""
Абстрактный базовый класс для всех конверторов.
Определяет интерфейс для преобразования полей объектов.
"""

class abstract_covertor(abc.ABC):

    @abc.abstractmethod
    def convert(self, field_name: str, value) -> dict:
        """
        Конвертирует значение поля в сериализуемый формат

        Args:
            field_name (str): наименование поля
            value: значение поля

        Returns:
            dict: словарь в формате ключ - наименование поля, значение - данные поля
        """
        pass

    @abc.abstractmethod
    def can_convert(self, value) -> bool:
        """
        Проверяет, может ли конвертор обработать данный тип значения

        Args:
            value: значение для проверки

        Returns:
            bool: True если конвертор может обработать значение
        """
        pass
