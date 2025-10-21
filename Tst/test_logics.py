import unittest
from Src.Logics.response_csv import response_csv
from Src.Models.group_model import group_model
from Src.Logics.factory_entities import factory_entities
from Src.Core.response_format import ResponseFormat
from Src.Core.validator import validator
from Src.Core.abstract_response import abstract_response
from Src.Models.settings_model import settings_model


# Тесты для проверки логики
class test_logics(unittest.TestCase):

    # Проверим формирование CSV
    def test_notNone_response_csv_build(self):
        # Подготовка
        response = response_csv()
        data = []
        entity = group_model.create("test")
        data.append(entity)

        # Действие
        result = response.build(data)

        # Проверка
        assert result is not None

    def test_notNone_factory_create(self):
        # Подготовка
        settings = settings_model()
        settings.response_format = ResponseFormat.CSV
        factory = factory_entities(settings)
        data = []
        entity = group_model.create("test")
        data.append(entity)

        # Действие
        logic = factory.create_default(data)

        # Проверка
        assert logic is not None
        validator.validate(logic, abstract_response)
        text = logic.build(data)
        assert len(text) > 0


if __name__ == '__main__':
    unittest.main()