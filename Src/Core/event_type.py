"""
Типы событий для системы справочников
"""
class event_type:
    
    # События удаления
    @staticmethod
    def before_delete_nomenclature() -> str:
        return "before_delete_nomenclature"
    
    @staticmethod
    def before_delete_group() -> str:
        return "before_delete_group"
    
    @staticmethod
    def before_delete_range() -> str:
        return "before_delete_range"
    
    @staticmethod
    def before_delete_storage() -> str:
        return "before_delete_storage"
    
    # События обновления
    @staticmethod
    def after_update_nomenclature() -> str:
        return "after_update_nomenclature"
    
    @staticmethod
    def after_update_group() -> str:
        return "after_update_group"
    
    @staticmethod
    def after_update_range() -> str:
        return "after_update_range"
    
    @staticmethod
    def after_update_storage() -> str:
        return "after_update_storage"
    
    # События создания
    @staticmethod
    def after_create_nomenclature() -> str:
        return "after_create_nomenclature"
    
    @staticmethod
    def after_create_group() -> str:
        return "after_create_group"
    
    @staticmethod
    def after_create_range() -> str:
        return "after_create_range"
    
    @staticmethod
    def after_create_storage() -> str:
        return "after_create_storage"
    
    # Системные события
    @staticmethod
    def settings_changed() -> str:
        return "settings_changed"
    
    @staticmethod
    def data_export_needed() -> str:
        return "data_export_needed"
    
    # События зависимостей
    @staticmethod
    def check_dependencies() -> str:
        return "check_dependencies"
    
    @staticmethod
    def update_dependencies() -> str:
        return "update_dependencies"
    
    @staticmethod
    def change_block_period() -> str:
        return "change_block_period"
    
    @staticmethod
    def add_reference() -> str:
        return "add_reference"
    
    @staticmethod
    def change_reference() -> str:
        return "change_reference"
    
    @staticmethod
    def remove_reference() -> str:
        return "remove_reference"
    
    @staticmethod
    def events() -> list:
        """Получить список всех событий"""
        result = []
        methods = [method for method in dir(event_type) if 
                  callable(getattr(event_type, method)) and not method.startswith('__') and method != "events"]
        for method in methods:
            key = getattr(event_type, method)()
            result.append(key)
        return result
