from Src.Core.abstract_covertor import abstract_covertor

"""
Конвертор для базовых типов данных.
Обрабатывает примитивные типы: numeric, str
"""

class basic_convertor(abstract_covertor):

    def convert(self, field_name: str, value) -> dict:
        """
        Конвертирует значение поля в сериализуемый формат

        Args:
            field_name (str): наименование поля
            value: значение поля

        Returns:
            dict: словарь с конвертированным значением или пустой словарь
        """
        # Валидируем и обрабатываем простые типы
        if isinstance(value, (int, float, str, bool)) or value is None:
            return {field_name: value}

        return {}
