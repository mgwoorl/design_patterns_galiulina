"""
Сервис для работы со справочниками (Номенклатура, Группа, Единица измерения, Склад)
Реализует операции добавления, изменения, удаления с использованием паттерна Наблюдатель
"""
from Src.Core.validator import validator
from Src.start_service import start_service
from Src.Core.observe_service import observe_service
from Src.Core.event_type import event_type
from Src.Core.abstract_subscriber import abstract_subscriber
from Src.Dtos.reference_dto import reference_dto

class reference_service(abstract_subscriber):
    __service = start_service()

    def __init__(self):
        self.__service.start()
        observe_service.add(self)

    """
    Добавить элемент справочника
    """
    @staticmethod
    def add(reference: str, properties: dict):
        validator.validate(reference, str)
        validator.validate(properties, dict)
        params = reference_dto().create({"name": reference, "model_dto_dict": properties})
        observe_service.create_event(event_type.add_reference(), params)

    """
    Изменить элемент справочника
    """
    @staticmethod
    def change(reference: str, properties: dict):
        validator.validate(reference, str)
        validator.validate(properties, dict)
        if "unique_code" not in properties:
            from Src.Core.validator import argument_exception
            raise argument_exception("Отсутствует поле unique_code")
        params = reference_dto().create({
            "name": reference, 
            "id": properties["unique_code"], 
            "model_dto_dict": properties
        })
        observe_service.create_event(event_type.change_reference(), params)

    """
    Удалить элемент справочника
    """
    @staticmethod
    def remove(reference: str, properties: dict):
        validator.validate(reference, str)
        validator.validate(properties, dict)
        if "unique_code" not in properties:
            from Src.Core.validator import argument_exception
            raise argument_exception("Отсутствует поле unique_code")
        params = reference_dto().create({
            "name": reference, 
            "id": properties["unique_code"], 
            "model_dto_dict": properties
        })
        observe_service.create_event(event_type.remove_reference(), params)

    """
    Обработка событий справочника
    """
    def handle(self, event: str, params: reference_dto):
        super().handle(event, params)

        if event == event_type.add_reference():
            from Src.Core.validator import argument_exception
            validator.validate(params, reference_dto)
            model_type = params.name

            from Src.reposity import reposity
            from Src.Models.nomenclature_model import nomenclature_model
            from Src.Models.group_model import group_model
            from Src.Models.range_model import range_model
            from Src.Models.storage_model import storage_model
            from Src.Dtos.nomenclature_dto import nomenclature_dto
            from Src.Dtos.category_dto import category_dto
            from Src.Dtos.range_dto import range_dto

            match = {
                reposity.nomenclature_key(): (nomenclature_dto, nomenclature_model),
                reposity.range_key(): (range_dto, range_model),
                reposity.group_key(): (category_dto, group_model),
                reposity.storage_key(): None
            }

            if model_type not in match.keys():
                raise argument_exception(f"Получена неизвестная модель {model_type}. Доступны только следующие модели: {list(match.keys())}")

            if match[model_type] is None:
                raise argument_exception(f"Добавление для типа {model_type} не реализовано")

            dto_class, model_class = match[model_type]
            dto = dto_class().create(params.model_dto_dict)
            model = model_class.from_dto(dto, self.__service.data.data)

            if model not in self.__service.data.data[model_type]:
                self.__service.data.data[model_type].append(model)

        elif event == event_type.change_reference():
            from Src.Core.validator import operation_exception, argument_exception
            validator.validate(params, reference_dto)
            model_type = params.name

            old_model = None
            for item in self.__service.data.data.get(model_type, []):
                if item.unique_code == params.id:
                    old_model = item
                    break

            if not old_model:
                raise operation_exception(f"Объект с кодом {params.id} не найден.")

            from Src.Logics.convert_factory import convert_factory
            from Src.Core.abstract_dto import object_to_dto
            factory = convert_factory()

            dto_dict = object_to_dto(factory.convert(old_model))
            dto_dict.update(params.model_dto_dict)

            from Src.Models.nomenclature_model import nomenclature_model
            from Src.Models.group_model import group_model
            from Src.Models.range_model import range_model
            from Src.Dtos.nomenclature_dto import nomenclature_dto
            from Src.Dtos.category_dto import category_dto
            from Src.Dtos.range_dto import range_dto
            from Src.reposity import reposity
            from Src.Dtos.update_dependencies_dto import update_dependencies_dto

            match = {
                reposity.nomenclature_key(): (nomenclature_dto, nomenclature_model),
                reposity.range_key(): (range_dto, range_model),
                reposity.group_key(): (category_dto, group_model)
            }

            if model_type not in match:
                raise argument_exception(f"Изменение для типа {model_type} не реализовано")

            dto_class, model_class = match[model_type]
            dto = dto_class().create(dto_dict)

            cache = {}
            for key in self.__service.data.data.keys():
                for item in self.__service.data.data[key]:
                    cache[item.unique_code] = item

            model = model_class.from_dto(dto, cache)

            update_dto = update_dependencies_dto().create({
                "old_model": old_model, 
                "new_model": model
            })

            observe_service.create_event(event_type.update_dependencies(), update_dto)

            self.__service.data.data[model_type].remove(old_model)
            self.__service.data.data[model_type].append(model)

        elif event == event_type.remove_reference():
            from Src.Core.validator import operation_exception
            validator.validate(params, reference_dto)
            model_type = params.name

            model = None
            for item in self.__service.data.data.get(model_type, []):
                if item.unique_code == params.id:
                    model = item
                    break

            if not model:
                raise operation_exception(f"Объект с кодом {params.id} не найден.")

            from Src.Dtos.check_dependencies_dto import check_dependencies_dto
            check_dto = check_dependencies_dto().create({"model": model})

            observe_service.create_event(event_type.check_dependencies(), check_dto)

            self.__service.data.data[model_type].remove(model)
