"""
Типы событий для системы наблюдателей
"""
class event_type:
    
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
    def update_dependencies() -> str:
        return "update_dependencies"
    
    @staticmethod
    def check_dependencies() -> str:
        return "check_dependencies"
    
    @staticmethod
    def info() -> str:
        return "info"
    
    @staticmethod
    def warning() -> str:
        return "warning"
    
    @staticmethod
    def error() -> str:
        return "error"
    
    @staticmethod
    def events() -> list:
        """
        Получить список всех событий
        """
        result = []
        methods = [method for method in dir(event_type) if
                    callable(getattr(event_type, method)) and not method.startswith('__') and method != "events"]
        for method in methods:
            key = getattr(event_type, method)()
            result.append(key)
        
        return result
