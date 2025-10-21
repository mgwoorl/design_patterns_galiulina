from Src.reposity import reposity
from Src.Models.range_model import range_model
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Core.validator import validator, argument_exception, operation_exception
import os
import json
from Src.Models.receipt_model import receipt_model
from Src.Models.receipt_item_model import receipt_item_model
from Src.Dtos.nomenclature_dto import nomenclature_dto
from Src.Dtos.range_dto import range_dto
from Src.Dtos.category_dto import category_dto


class start_service:
    __repo: reposity = reposity()
    __default_receipt: receipt_model
    __cache = {}
    __full_file_name: str = ""

    def __init__(self):
        self.__repo.initalize()

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(start_service, cls).__new__(cls)
        return cls.instance

    @property
    def file_name(self) -> str:
        return self.__full_file_name

    @file_name.setter
    def file_name(self, value: str):
        validator.validate(value, str)
        full_file_name = os.path.abspath(value)
        if os.path.exists(full_file_name):
            self.__full_file_name = full_file_name.strip()
        else:
            raise argument_exception(f'Не найден файл настроек {full_file_name}')

    def load(self) -> bool:
        if self.__full_file_name == "":
            raise operation_exception("Не найден файл настроек!")

        try:
            with open(self.__full_file_name, 'r', encoding='utf-8') as file_instance:
                settings = json.load(file_instance)

                if "default_receipt" in settings.keys():
                    data = settings["default_receipt"]
                    return self.convert(data)

            return False
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            return False

    def __save_item(self, key: str, dto, item):
        validator.validate(key, str)
        item.unique_code = dto.id
        self.__cache.setdefault(dto.id, item)
        self.__repo.data[key].append(item)

    def __convert_ranges(self, data: dict) -> bool:
        validator.validate(data, dict)
        ranges = data['ranges'] if 'ranges' in data else []
        if len(ranges) == 0:
            return False

        for range_item in ranges:
            dto = range_dto().create(range_item)
            item = range_model.from_dto(dto, self.__cache)
            self.__save_item(reposity.range_key(), dto, item)
        return True

    def __convert_groups(self, data: dict) -> bool:
        validator.validate(data, dict)
        categories = data['categories'] if 'categories' in data else []
        if len(categories) == 0:
            return False

        for category in categories:
            dto = category_dto().create(category)
            item = group_model.from_dto(dto, self.__cache)
            self.__save_item(reposity.group_key(), dto, item)
        return True

    def __convert_nomenclatures(self, data: dict) -> bool:
        validator.validate(data, dict)
        nomenclatures = data['nomenclatures'] if 'nomenclatures' in data else []
        if len(nomenclatures) == 0:
            return False

        for nomenclature in nomenclatures:
            dto = nomenclature_dto().create(nomenclature)
            item = nomenclature_model.from_dto(dto, self.__cache)
            self.__save_item(reposity.nomenclature_key(), dto, item)
        return True

    def convert(self, data: dict) -> bool:
        validator.validate(data, dict)

        cooking_time = data['cooking_time'] if 'cooking_time' in data else ""
        portions = int(data['portions']) if 'portions' in data else 0
        name = data['name'] if 'name' in data else "НЕ ИЗВЕСТНО"
        self.__default_receipt = receipt_model.create(name, cooking_time, portions)

        steps = data['steps'] if 'steps' in data else []
        for step in steps:
            if step.strip() != "":
                self.__default_receipt.steps.append(step)

        self.__convert_ranges(data)
        self.__convert_groups(data)
        self.__convert_nomenclatures(data)

        compositions = data['composition'] if 'composition' in data else []
        for composition in compositions:
            nomenclature_id = composition['nomenclature_id'] if 'nomenclature_id' in composition else ""
            range_id = composition['range_id'] if 'range_id' in composition else ""
            value = composition['value'] if 'value' in composition else ""
            nomenclature = self.__cache[nomenclature_id] if nomenclature_id in self.__cache else None
            range_obj = self.__cache[range_id] if range_id in self.__cache else None
            item = receipt_item_model.create(nomenclature, range_obj, value)
            self.__default_receipt.composition.append(item)

        self.__repo.data[reposity.receipt_key()].append(self.__default_receipt)
        return True

    @property
    def data(self):
        return self.__repo.data

    def start(self):
        import os
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.file_name = os.path.join(base_dir, "..", "settings.json")
        self.file_name = os.path.abspath(self.file_name)

        result = self.load()
        if result == False:
            raise operation_exception("Невозможно сформировать стартовый набор данных!")