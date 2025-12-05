"""
Сервис логирования
"""
from Src.Core.log_record import log_record
from Src.Core.log_level import LogLevel
from Src.Core.abstract_subscriber import abstract_subscriber
from Src.Core.validator import validator
from Src.Core.observe_service import observe_service
from Src.Core.event_type import event_type
from Src.settings_manager import settings_manager

class logger_service(abstract_subscriber):
    __min_level: LogLevel = LogLevel.DEBUG
    __log_to_console: bool = True
    __log_to_file: bool = False
    __file_path: str = "app.log"
    
    def __init__(self):
        # Загружаем настройки из settings.json
        self.__load_settings()
        observe_service.add(self)
    
    def __load_settings(self):
        """
        Загрузить настройки логирования из settings.json
        """
        try:
            # Пытаемся загрузить настройки логирования если они есть
            import json
            import os
            
            if os.path.exists("settings.json"):
                with open("settings.json", 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                    if "logging" in settings:
                        logging_settings = settings["logging"]
                        
                        # Минимальный уровень
                        if "min_level" in logging_settings:
                            self.__min_level = LogLevel.from_string(logging_settings["min_level"])
                        
                        # Куда выводить
                        if "output" in logging_settings:
                            output = logging_settings["output"].lower()
                            if output == "console":
                                self.__log_to_console = True
                                self.__log_to_file = False
                            elif output == "file":
                                self.__log_to_console = False
                                self.__log_to_file = True
                            elif output == "both":
                                self.__log_to_console = True
                                self.__log_to_file = True
                        
                        # Файл для логирования
                        if "log_file" in logging_settings:
                            self.__file_path = logging_settings["log_file"]
                            
                # Логируем успешную загрузку настроек
                self.__write_log(log_record(
                    LogLevel.INFO,
                    "Настройки логирования загружены",
                    "logger_service",
                    {
                        "min_level": self.__min_level.value,
                        "output": "console" if self.__log_to_console and not self.__log_to_file else 
                                 "file" if not self.__log_to_console and self.__log_to_file else 
                                 "both",
                        "log_file": self.__file_path if self.__log_to_file else None
                    }
                ))
                
        except Exception as e:
            # Используем значения по умолчанию при ошибке
            self.__write_log(log_record(
                LogLevel.WARNING,
                f"Ошибка загрузки настроек логирования: {str(e)}. Используются значения по умолчанию",
                "logger_service"
            ))
    
    def __should_log(self, level: LogLevel) -> bool:
        """
        Проверить, нужно ли логировать на данном уровне
        
        Args:
            level (LogLevel): уровень логирования для проверки
            
        Returns:
            bool: True если нужно логировать
        """
        levels_order = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR]
        current_index = levels_order.index(level)
        min_index = levels_order.index(self.__min_level)
        return current_index >= min_index
    
    def __write_log(self, record: log_record):
        """
        Записать лог в соответствии с настройками
        
        Args:
            record (log_record): запись лога для записи
        """
        if not self.__should_log(record.level):
            return
            
        log_str = record.to_string() + "\n"
        
        # Вывод в консоль
        if self.__log_to_console:
            print(log_str)
        
        # Запись в файл
        if self.__log_to_file:
            try:
                # Создаем директорию если ее нет
                import os
                directory = os.path.dirname(self.__file_path)
                if directory and not os.path.exists(directory):
                    os.makedirs(directory)
                    
                with open(self.__file_path, 'a', encoding='utf-8') as f:
                    f.write(log_str)
            except Exception as e:
                # Если не удалось записать в файл, выводим в консоль
                if not self.__log_to_console:
                    print(f"{record.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\t[ERROR] [logger_service] Ошибка записи в файл: {str(e)}")
    
    def log(self, level: LogLevel, message: str, service: str, details: dict = None):
        """
        Создать запись лога
        
        Args:
            level (LogLevel): уровень логирования
            message (str): сообщение лога
            service (str): сервис-источник
            details (dict): дополнительные детали
        """
        record = log_record(level, message, service, details)
        self.__write_log(record)
    
    def handle(self, event: str, params):
        """
        Обработка событий логирования
        
        Args:
            event (str): тип события
            params: параметры события
        """
        super().handle(event, params)
        
        if event == event_type.debug():
            if isinstance(params, dict):
                self.log(LogLevel.DEBUG, params.get("message", ""), params.get("service", "unknown"), params.get("details"))
            else:
                self.log(LogLevel.DEBUG, str(params), "unknown")
        elif event == event_type.info():
            if isinstance(params, dict):
                self.log(LogLevel.INFO, params.get("message", ""), params.get("service", "unknown"), params.get("details"))
            else:
                self.log(LogLevel.INFO, str(params), "unknown")
        elif event == event_type.warning():
            if isinstance(params, dict):
                self.log(LogLevel.WARNING, params.get("message", ""), params.get("service", "unknown"), params.get("details"))
            else:
                self.log(LogLevel.WARNING, str(params), "unknown")
        elif event == event_type.error():
            if isinstance(params, dict):
                self.log(LogLevel.ERROR, params.get("message", ""), params.get("service", "unknown"), params.get("details"))
            else:
                self.log(LogLevel.ERROR, str(params), "unknown")

# Глобальный экземпляр логгера
logger = logger_service()
