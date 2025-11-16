from Src.Core.abstract_dto import abstact_dto
from Src.Core.validator import validator
from Src.Core.filter_type import FilterType

"""
DTO модель для фильтрации данных
Пример использования:
[
    {
        "field_name": "name",
        "value": "мука", 
        "type": "LIKE"
    },
    {
        "field_name": "unique_code",
        "value": "0c101a7e-5934-4155-83a6-d2c388fcc11a",
        "type": "EQUALS"
    },
    {
        "field_name": "group/name",
        "value": "Ингредиенты",
        "type": "EQUALS"
    }
]
"""
class filter_dto(abstact_dto):
    __field_name: str = ""
    __value: str = ""
    __type: FilterType = FilterType.EQUALS

    @property
    def field_name(self) -> str:
        return self.__field_name

    @field_name.setter
    def field_name(self, value: str):
        validator.validate(value, str)
        self.__field_name = value

    @property
    def value(self) -> str:
        return self.__value

    @value.setter
    def value(self, value: str):
        validator.validate(value, str)
        self.__value = value

    @property
    def type(self) -> FilterType:
        return self.__type

    @type.setter
    def type(self, value: FilterType):
        validator.validate(value, FilterType)
        self.__type = value

    def create(self, data) -> "filter_dto":
        """
        Фабричный метод для создания DTO из словаря
        
        Args:
            data (dict): словарь с данными фильтра
            
        Returns:
            filter_dto: созданный объект DTO
        """
        validator.validate(data, dict)
        
        if "field_name" in data:
            self.field_name = data["field_name"]
        if "value" in data:
            self.value = data["value"]
        if "type" in data:
            try:
                self.type = FilterType[data["type"]]
            except KeyError:
                self.type = FilterType.EQUALS
        
        return self
