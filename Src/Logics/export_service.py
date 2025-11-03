import json
from datetime import datetime
from Src.Core.validator import validator, operation_exception
from Src.reposity import reposity
from Src.Logics.convert_factory import convert_factory

"""
Сервис для экспорта данных в файл
"""
class export_service:
    __repo: reposity
    __convert_factory: convert_factory

    def __init__(self, repository: reposity):
        self.__repo = repository
        self.__convert_factory = convert_factory()

    def export_all_data(self, file_path: str) -> bool:
        validator.validate(file_path, str)

        export_data = {
            "export_date": datetime.now().isoformat(),
            "ranges": self.__convert_entities(self.__repo.data.get(reposity.range_key(), [])),
            "groups": self.__convert_entities(self.__repo.data.get(reposity.group_key(), [])),
            "nomenclatures": self.__convert_entities(self.__repo.data.get(reposity.nomenclature_key(), [])),
            "storages": self.__convert_entities(self.__repo.data.get(reposity.storage_key(), [])),
            "transactions": self.__convert_entities(self.__repo.data.get(reposity.transaction_key(), [])),
            "receipts": self.__convert_entities(self.__repo.data.get(reposity.receipt_key(), []))
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        return True

    def __convert_entities(self, entities: list) -> list:
        result = []
        for entity in entities:
            converted = self.__convert_factory.convert(entity)
            result.append(converted)
        return result
