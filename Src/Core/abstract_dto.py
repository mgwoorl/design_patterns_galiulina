import abc
from Src.Core.common import common
from Src.Core.validator import validator, operation_exception

"""
Абстрактный класс для наследования только dto структур
"""


class abstact_dto:
    __name: str = ""
    __id: str = ""

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def id(self) -> str:
        return self.__id

    @id.setter
    def id(self, value):
        self.__id = value

        # Универсальный фабричный метод для загрузщки dto из словаря

    @abc.abstractmethod
    def create(self, data) -> "abstact_dto":
        validator.validate(data, dict)
        fields = common.get_fields(self)
        matching_keys = list(filter(lambda key: key in fields, data.keys()))

        try:
            for key in matching_keys:
                setattr(self, key, data[key])
        except:
            raise operation_exception("Невозможно загрузить данные!")

        return self

import abc
from Src.Core.common import common
from Src.Core.validator import validator, operation_exception

"""
Абстрактный класс для наследования только dto структур
"""


class abstact_dto:
    __name: str = ""
    __id: str = ""

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def id(self) -> str:
        return self.__id

    @id.setter
    def id(self, value):
        self.__id = value

    # Универсальный фабричный метод для загрузки dto из словаря
    @abc.abstractmethod
    def create(self, data) -> "abstact_dto":
        validator.validate(data, dict)
        fields = common.get_fields(self)
        matching_keys = list(filter(lambda key: key in fields, data.keys()))

        try:
            for key in matching_keys:
                setattr(self, key, data[key])
        except:
            raise operation_exception("Невозможно загрузить данные!")

        return self

    @staticmethod
    def object_to_dto(obj):
        """
        Преобразование объекта в DTO словарь
        
        Args:
            obj: любой объект для преобразования
            
        Returns:
            dict: словарь в формате DTO
        """
        if isinstance(obj, dict):
            result = {}
            for key in obj.keys():
                if isinstance(obj[key], dict):
                    if "unique_code" in obj[key]:
                        value = abstact_dto.object_to_dto(obj[key]["unique_code"])
                        key += "_id"
                    else:
                        value = abstact_dto.object_to_dto(obj[key])
                    result[key] = value
                elif key == "value" and len(obj.keys()) == 1:
                    # удаление лишнего словаря, берем только значение
                    return abstact_dto.object_to_dto(obj[key])
                else:
                    new_key = "id" if key == "unique_code" else key
                    if obj[key] is None and key != "name":
                        new_key += "_id"
                    result[new_key] = abstact_dto.object_to_dto(obj[key])
            return result
        elif isinstance(obj, list):
            result = []
            for item in obj:
                result.append(abstact_dto.object_to_dto(item))
            return result
        else:
            return obj
