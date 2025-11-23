from Src.Core.abstract_model import abstact_model
from Src.Core.validator import validator
from datetime import datetime

"""
Модель кэшированных оборотов до даты блокировки
"""
class turnover_cache_model(abstact_model):
    __nomenclature_id: str = ""
    __storage_id: str = ""
    __period_end: datetime = None
    __debit_turnover: float = 0.0
    __credit_turnover: float = 0.0
    __calculated_at: datetime = None

    @property
    def nomenclature_id(self) -> str:
        return self.__nomenclature_id

    @nomenclature_id.setter
    def nomenclature_id(self, value: str):
        validator.validate(value, str)
        self.__nomenclature_id = value

    @property
    def storage_id(self) -> str:
        return self.__storage_id

    @storage_id.setter
    def storage_id(self, value: str):
        validator.validate(value, str)
        self.__storage_id = value

    @property
    def period_end(self) -> datetime:
        return self.__period_end

    @period_end.setter
    def period_end(self, value: datetime):
        validator.validate(value, datetime)
        self.__period_end = value

    @property
    def debit_turnover(self) -> float:
        return self.__debit_turnover

    @debit_turnover.setter
    def debit_turnover(self, value: float):
        validator.validate(value, (int, float))
        self.__debit_turnover = float(value)

    @property
    def credit_turnover(self) -> float:
        return self.__credit_turnover

    @credit_turnover.setter
    def credit_turnover(self, value: float):
        validator.validate(value, (int, float))
        self.__credit_turnover = float(value)

    @property
    def calculated_at(self) -> datetime:
        return self.__calculated_at

    @calculated_at.setter
    def calculated_at(self, value: datetime):
        validator.validate(value, datetime)
        self.__calculated_at = value

    @staticmethod
    def create(nomenclature_id: str, storage_id: str, period_end: datetime, 
               debit_turnover: float, credit_turnover: float) -> "turnover_cache_model":
        item = turnover_cache_model()
        item.nomenclature_id = nomenclature_id
        item.storage_id = storage_id
        item.period_end = period_end
        item.debit_turnover = debit_turnover
        item.credit_turnover = credit_turnover
        item.calculated_at = datetime.now()
        return item
