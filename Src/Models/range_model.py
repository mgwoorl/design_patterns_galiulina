from Src.Core.entity_model import entity_model
from Src.Core.validator import validator, argument_exception
from Src.Dtos.range_dto import range_dto

"""
Модель единицы измерения
"""
class range_model(entity_model):
    __value: int = 1
    __base: 'range_model' = None

    @property
    def value(self) -> int:
        """
        Значение коэффициента пересчета
        """
        return self.__value
    
    @value.setter
    def value(self, value: int):
        validator.validate(value, int)
        if value <= 0:
             raise argument_exception("Некорректный аргумент!")
        self.__value = value

    @property
    def base(self):
        """
        Базовая единица измерения
        """
        return self.__base
    
    @base.setter
    def base(self, value):
        self.__base = value

    def root_base_unit(self):
        """
        Возвращает корневую (базовую) единицу измерения
        """
        if self.base is None:
            return self
        else:
            return self.base.root_base_unit()

    def convert_to_root_base_unit(self, quantity: float) -> float:
        """
        Конвертирует количество в корневые (базовые) единицы измерения
        """
        if self.base is None:
            return quantity
        else:
            return self.base.convert_to_root_base_unit(quantity * self.value)

    @staticmethod
    def create_kill():
        """
        Создает единицу измерения - килограмм
        """
        inner_gramm = range_model.create_gramm()
        return range_model.create("киллограмм", 1000, inner_gramm)

    @staticmethod
    def create_gramm():
        """
        Создает единицу измерения - грамм
        """
        return range_model.create("грамм", 1, None)
     
    @staticmethod
    def create(name: str, value: int, base):
        """
        Универсальный метод создания единицы измерения
        """
        validator.validate(name, str)
        validator.validate(value, int)

        inner_base = None
        if not base is None: 
            validator.validate(base, range_model)
            inner_base = base
        item = range_model()
        item.name = name
        item.base = inner_base
        item.value = value
        return item
    
    def from_dto(dto: range_dto, cache: dict):
        """
        Фабричный метод создания из DTO
        """
        validator.validate(dto, range_dto)
        validator.validate(cache, dict)
        base = cache[dto.base_id] if dto.base_id in cache else None
        item = range_model.create(dto.name, dto.value, base)
        return item
