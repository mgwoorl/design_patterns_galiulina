"""
Сервис для работы со справочниками (Номенклатура, Группа, Единица измерения, Склад)
Реализует операции добавления, изменения, удаления с использованием паттерна Наблюдатель
"""
from Src.Core.validator import validator, argument_exception, operation_exception
from Src.start_service import start_service
from Src.Core.observe_service import observe_service
from Src.Core.event_type import event_type
from Src.Core.abstract_subscriber import abstract_subscriber
from Src.Dtos.reference_dto import reference_dto
from Src.reposity import reposity
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model
from Src.Models.storage_model import storage_model
from Src.Dtos.nomenclature_dto import nomenclature_dto
from Src.Dtos.category_dto import category_dto
from Src.Dtos.range_dto import range_dto
from Src.Logics.convert_factory import convert_factory
from Src.Core.abstract_dto import object_to_dto
from Src.Dtos.update_dependencies_dto import update_dependencies_dto
from Src.Dtos.check_dependencies_dto import check_dependencies_dto

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
        
        # Логируем операцию добавления
        observe_service.create_event(event_type.info(), {
            "message": f"Начало добавления элемента справочника: {reference}",
            "service": "reference_service",
            "details": {
                "operation": "add",
                "reference_type": reference,
                "properties": properties
            }
        })
        
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
            error_msg = "Отсутствует поле unique_code"
            observe_service.create_event(event_type.error(), {
                "message": error_msg,
                "service": "reference_service"
            })
            raise argument_exception(error_msg)
        
        # Логируем операцию изменения
        observe_service.create_event(event_type.info(), {
            "message": f"Начало изменения элемента справочника: {reference}",
            "service": "reference_service",
            "details": {
                "operation": "change",
                "reference_type": reference,
                "unique_code": properties["unique_code"],
                "properties": properties
            }
        })
        
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
            error_msg = "Отсутствует поле unique_code"
            observe_service.create_event(event_type.error(), {
                "message": error_msg,
                "service": "reference_service"
            })
            raise argument_exception(error_msg)
        
        # Логируем операцию удаления
        observe_service.create_event(event_type.info(), {
            "message": f"Начало удаления элемента справочника: {reference}",
            "service": "reference_service",
            "details": {
                "operation": "remove",
                "reference_type": reference,
                "unique_code": properties["unique_code"]
            }
        })
        
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
            validator.validate(params, reference_dto)
            model_type = params.name

            # Логируем обработку добавления
            observe_service.create_event(event_type.debug(), {
                "message": f"Обработка добавления справочника: {model_type}",
                "service": "reference_service",
                "details": {
                    "model_type": model_type,
                    "params": params.model_dto_dict
                }
            })

            match = {
                reposity.nomenclature_key(): (nomenclature_dto, nomenclature_model),
                reposity.range_key(): (range_dto, range_model),
                reposity.group_key(): (category_dto, group_model),
                reposity.storage_key(): None
            }

            if model_type not in match.keys():
                error_msg = f"Получена неизвестная модель {model_type}"
                observe_service.create_event(event_type.error(), {
                    "message": error_msg,
                    "service": "reference_service",
                    "details": {
                        "available_models": list(match.keys()),
                        "received_model": model_type
                    }
                })
                raise argument_exception(f"{error_msg}. Доступны только следующие модели: {list(match.keys())}")

            if match[model_type] is None:
                error_msg = f"Добавление для типа {model_type} не реализовано"
                observe_service.create_event(event_type.error(), {
                    "message": error_msg,
                    "service": "reference_service"
                })
                raise argument_exception(error_msg)

            try:
                dto_class, model_class = match[model_type]
                dto = dto_class().create(params.model_dto_dict)
                model = model_class.from_dto(dto, self.__service.data.data)

                if model not in self.__service.data.data[model_type]:
                    self.__service.data.data[model_type].append(model)
                    # Логируем успешное добавление
                    observe_service.create_event(event_type.info(), {
                        "message": f"Элемент справочника успешно добавлен: {model_type}",
                        "service": "reference_service",
                        "details": {
                            "model_type": model_type,
                            "unique_code": model.unique_code,
                            "name": model.name if hasattr(model, 'name') else None
                        }
                    })
                else:
                    # Логируем попытку добавить существующий элемент
                    observe_service.create_event(event_type.warning(), {
                        "message": f"Попытка добавить существующий элемент: {model_type}",
                        "service": "reference_service",
                        "details": {
                            "model_type": model_type,
                            "unique_code": model.unique_code
                        }
                    })
                    
            except Exception as e:
                observe_service.create_event(event_type.error(), {
                    "message": f"Ошибка при добавлении элемента справочника {model_type}: {str(e)}",
                    "service": "reference_service",
                    "details": {
                        "model_type": model_type,
                        "error": str(e)
                    }
                })
                raise

        elif event == event_type.change_reference():
            validator.validate(params, reference_dto)
            model_type = params.name

            # Логируем обработку изменения
            observe_service.create_event(event_type.debug(), {
                "message": f"Обработка изменения справочника: {model_type}",
                "service": "reference_service",
                "details": {
                    "model_type": model_type,
                    "unique_code": params.id,
                    "new_properties": params.model_dto_dict
                }
            })

            old_model = None
            for item in self.__service.data.data.get(model_type, []):
                if item.unique_code == params.id:
                    old_model = item
                    break

            if not old_model:
                error_msg = f"Объект с кодом {params.id} не найден."
                observe_service.create_event(event_type.error(), {
                    "message": error_msg,
                    "service": "reference_service",
                    "details": {
                        "model_type": model_type,
                        "unique_code": params.id
                    }
                })
                raise operation_exception(error_msg)

            try:
                factory = convert_factory()
                dto_dict = object_to_dto(factory.convert(old_model))
                dto_dict.update(params.model_dto_dict)

                match = {
                    reposity.nomenclature_key(): (nomenclature_dto, nomenclature_model),
                    reposity.range_key(): (range_dto, range_model),
                    reposity.group_key(): (category_dto, group_model)
                }

                if model_type not in match:
                    error_msg = f"Изменение для типа {model_type} не реализовано"
                    observe_service.create_event(event_type.error(), {
                        "message": error_msg,
                        "service": "reference_service"
                    })
                    raise argument_exception(error_msg)

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

                # Логируем успешное изменение
                observe_service.create_event(event_type.info(), {
                    "message": f"Элемент справочника успешно изменен: {model_type}",
                    "service": "reference_service",
                    "details": {
                        "model_type": model_type,
                        "unique_code": params.id,
                        "old_name": old_model.name if hasattr(old_model, 'name') else None,
                        "new_name": model.name if hasattr(model, 'name') else None
                    }
                })
                
            except Exception as e:
                observe_service.create_event(event_type.error(), {
                    "message": f"Ошибка при изменении элемента справочника {model_type}: {str(e)}",
                    "service": "reference_service",
                    "details": {
                        "model_type": model_type,
                        "unique_code": params.id,
                        "error": str(e)
                    }
                })
                raise

        elif event == event_type.remove_reference():
            validator.validate(params, reference_dto)
            model_type = params.name

            # Логируем обработку удаления
            observe_service.create_event(event_type.debug(), {
                "message": f"Обработка удаления справочника: {model_type}",
                "service": "reference_service",
                "details": {
                    "model_type": model_type,
                    "unique_code": params.id
                }
            })

            model = None
            for item in self.__service.data.data.get(model_type, []):
                if item.unique_code == params.id:
                    model = item
                    break

            if not model:
                error_msg = f"Объект с кодом {params.id} не найден."
                observe_service.create_event(event_type.error(), {
                    "message": error_msg,
                    "service": "reference_service"
                })
                raise operation_exception(error_msg)

            try:
                check_dto = check_dependencies_dto().create({"model": model})
                observe_service.create_event(event_type.check_dependencies(), check_dto)
                
                self.__service.data.data[model_type].remove(model)
                # Логируем успешное удаление
                observe_service.create_event(event_type.info(), {
                    "message": f"Элемент справочника успешно удален: {model_type}",
                    "service": "reference_service",
                    "details": {
                        "model_type": model_type,
                        "unique_code": params.id,
                        "name": model.name if hasattr(model, 'name') else None
                    }
                })
                    
            except operation_exception as e:
                # Логируем отказ в удалении из-за зависимостей
                observe_service.create_event(event_type.warning(), {
                    "message": f"Отказ в удалении элемента справочника: {str(e)}",
                    "service": "reference_service",
                    "details": {
                        "model_type": model_type,
                        "unique_code": params.id,
                        "error": str(e)
                    }
                })
                raise
            except Exception as e:
                observe_service.create_event(event_type.error(), {
                    "message": f"Ошибка при удалении элемента справочника {model_type}: {str(e)}",
                    "service": "reference_service",
                    "details": {
                        "model_type": model_type,
                        "unique_code": params.id,
                        "error": str(e)
                    }
                })
                raise
