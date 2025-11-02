import unittest
from datetime import datetime
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor
from Src.Logics.convert_factory import convert_factory
from Src.Models.range_model import range_model
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model

"""
Набор тестов для конвертеров и фабрики
"""

class test_convertors(unittest.TestCase):

    # Проверить конвертацию простых типов basic_convertor
    def test_basic_convertor_simple_types(self):
        # Подготовка
        convertor = basic_convertor()

        # Действие и проверка строк
        result = convertor.convert("name", "Test")
        assert result == {"name": "Test"}

        # Действие и проверка целых чисел
        result = convertor.convert("value", 123)
        assert result == {"value": 123}

        # Действие и проверка дробных чисел
        result = convertor.convert("price", 45.67)
        assert result == {"price": 45.67}

        # Действие и проверка булевых значений
        result = convertor.convert("is_valid", True)
        assert result == {"is_valid": True}

        # Действие и проверка None значений
        result = convertor.convert("none_value", None)
        assert result == {"none_value": None}

    # Проверить что basic_convertor не конвертирует сложные типы
    def test_basic_convertor_complex_types(self):
        # Подготовка
        convertor = basic_convertor()

        # Действие и проверка datetime
        result = convertor.convert("created", datetime.now())
        assert result == {}

        # Действие и проверка списков
        result = convertor.convert("list", [1, 2, 3])
        assert result == {}

        # Действие и проверка словарей
        result = convertor.convert("dict", {"key": "value"})
        assert result == {}

    # Проверить конвертацию datetime_convertor
    def test_datetime_convertor(self):
        # Подготовка
        convertor = datetime_convertor()
        test_datetime = datetime(2023, 10, 28, 12, 30, 45)

        # Действие
        result = convertor.convert("created", test_datetime)

        # Проверка
        assert result == {"created": "2023-10-28 12:30:45"}

    # Проверить что datetime_convertor не конвертирует другие типы
    def test_datetime_convertor_other_types(self):
        # Подготовка
        convertor = datetime_convertor()

        # Действие и проверка строк
        result = convertor.convert("name", "Test")
        assert result == {}

        # Действие и проверка чисел
        result = convertor.convert("value", 123)
        assert result == {}

    # Проверить конвертацию reference_convertor
    def test_reference_convertor(self):
        # Подготовка
        convertor = reference_convertor()
        range_obj = range_model.create("Грамм", 1, None)

        # Действие
        result = convertor.convert("range", range_obj)

        # Проверка
        assert "range" in result
        assert result["range"]["unique_code"] == range_obj.unique_code
        assert result["range"]["name"] == "Грамм"
        assert result["range"]["type"] == "range_model"

    # Проверить что convert_factory возвращает словарь
    def test_convert_factory_returns_dict(self):
        # Подготовка
        factory = convert_factory()

        class TestClass:
            def __init__(self):
                self.name = "Test"
                self.value = 123

        obj = TestClass()

        # Действие
        result = factory.convert(obj)

        # Проверка
        assert isinstance(result, dict) == True
        assert "name" in result
        assert "value" in result

    # Проверить работу convert_factory с реальными моделями
    def test_convert_factory_with_range_model(self):
        # Подготовка
        factory = convert_factory()
        range_obj = range_model.create("Грамм", 1, None)

        # Действие
        result = factory.convert(range_obj)

        # Проверка
        assert isinstance(result, dict) == True
        assert "name" in result
        assert "unique_code" in result
        assert "value" in result

    # Проверить обработку None объектов
    def test_convert_factory_with_none(self):
        # Подготовка
        factory = convert_factory()

        # Действие
        result = factory.convert(None)

        # Проверка
        assert result == {}

    # Проверить рекурсивную обработку вложенных объектов
    def test_convert_factory_with_nested_objects(self):
        # Подготовка
        factory = convert_factory()

        range_gramm = range_model.create("Грамм", 1, None)
        group_ingredients = group_model.create("Ингредиенты")
        nomenclature = nomenclature_model.create("Пшеничная мука", group_ingredients, range_gramm)

        # Действие
        result = factory.convert(nomenclature)

        # Проверка
        assert isinstance(result, dict) == True
        assert "name" in result
        assert "unique_code" in result
        # Проверяем что group и range обработаны рекурсивно
        assert "group" in result
        assert "range" in result
        assert isinstance(result["group"], dict)
        assert isinstance(result["range"], dict)

    # Проверить обработку списков
    def test_convert_factory_with_lists(self):
        # Подготовка
        factory = convert_factory()

        class TestClass:
            def __init__(self):
                self.items = [1, 2, 3]
                self.objects = [range_model.create("Грамм", 1, None)]

        obj = TestClass()

        # Действие
        result = factory.convert(obj)

        # Проверка
        assert isinstance(result, dict) == True
        assert "items" in result
        assert "objects" in result
        assert isinstance(result["items"], list)
        assert isinstance(result["objects"], list)
        # Проверяем что объекты в списке обработаны рекурсивно
        assert isinstance(result["objects"][0], dict)


if __name__ == '__main__':
    unittest.main()
