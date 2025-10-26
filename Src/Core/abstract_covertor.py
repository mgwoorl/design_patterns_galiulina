import abc

"""
Абстрактный базовый класс для всех конверторов.
Определяет интерфейс для преобразования полей объектов.
"""


class abstract_covertor(abc.ABC):

    @abc.abstractmethod
    def convert(self, field_name: str, value) -> any:
        """
        Конвертирует значение поля в сериализуемый формат

        Args:
            field_name (str): наименование поля
            value: значение поля

        Returns:
            any: сериализуемое значение
        """
        pass
