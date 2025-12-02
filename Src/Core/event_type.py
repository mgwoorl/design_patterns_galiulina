"""
Типы событий для системы наблюдателей
"""
class event_type:
    """
    Событие - смена даты блокировки
    """
    @staticmethod
    def change_block_period() -> str:
        return "change_block_period"

    """
    Событие - добавление reference
    """
    @staticmethod
    def add_reference() -> str:
        return "add_reference"

    """
    Событие - изменение reference
    """
    @staticmethod
    def change_reference() -> str:
        return "change_reference"

    """
    Событие - удаление reference
    """
    @staticmethod
    def remove_reference() -> str:
        return "remove_reference"

    """
    Событие - обновить зависимости от reference
    """
    @staticmethod
    def update_dependencies() -> str:
        return "update_dependencies"

    """
    Событие - проверить зависимости от reference
    """
    @staticmethod
    def check_dependencies() -> str:
        return "check_dependencies"

    """
    Событие - логгирование уровня INFO
    """
    @staticmethod
    def info() -> str:
        return "info"

    """
    Событие - логгирование уровня WARNING
    """
    @staticmethod
    def warning() -> str:
        return "warning"

    """
    Событие - логгирование уровня ERROR
    """
    @staticmethod
    def error() -> str:
        return "error"

    """
    Получить список всех событий
    """
    @staticmethod
    def events() -> list:
        result = []
        methods = [method for method in dir(event_type) if
                    callable(getattr(event_type, method)) and not method.startswith('__') and method != "events"]
        for method in methods:
            key = getattr(event_type, method)()
            result.append(key)

        return result
