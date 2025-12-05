import unittest
import os
import json
from datetime import datetime
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Src.Core.log_level import LogLevel
from Src.Core.log_record import log_record
from Src.Core.event_type import event_type

"""
Набор тестов для системы логирования
"""
class test_logging(unittest.TestCase):

    # Проверить преобразование строк в уровни логирования
    def test_log_level_from_string(self):
        # Подготовка
        
        # Действие
        debug_level = LogLevel.from_string("DEBUG")
        info_level = LogLevel.from_string("INFO")
        warning_level = LogLevel.from_string("WARNING")
        error_level = LogLevel.from_string("ERROR")
        default_level = LogLevel.from_string("UNKNOWN")
        
        # Проверки
        assert debug_level == LogLevel.DEBUG
        assert info_level == LogLevel.INFO
        assert warning_level == LogLevel.WARNING
        assert error_level == LogLevel.ERROR
        assert default_level == LogLevel.INFO

    # Проверить иерархию уровней логирования
    def test_log_level_includes(self):
        # Подготовка
        
        # Действие и проверки
        # DEBUG включает все уровни
        assert LogLevel.DEBUG.includes(LogLevel.DEBUG) == True
        assert LogLevel.DEBUG.includes(LogLevel.INFO) == True
        assert LogLevel.DEBUG.includes(LogLevel.WARNING) == True
        assert LogLevel.DEBUG.includes(LogLevel.ERROR) == True

        # INFO включает INFO, WARNING, ERROR
        assert LogLevel.INFO.includes(LogLevel.DEBUG) == False
        assert LogLevel.INFO.includes(LogLevel.INFO) == True
        assert LogLevel.INFO.includes(LogLevel.WARNING) == True
        assert LogLevel.INFO.includes(LogLevel.ERROR) == True

        # WARNING включает WARNING, ERROR
        assert LogLevel.WARNING.includes(LogLevel.DEBUG) == False
        assert LogLevel.WARNING.includes(LogLevel.INFO) == False
        assert LogLevel.WARNING.includes(LogLevel.WARNING) == True
        assert LogLevel.WARNING.includes(LogLevel.ERROR) == True

        # ERROR включает только ERROR
        assert LogLevel.ERROR.includes(LogLevel.DEBUG) == False
        assert LogLevel.ERROR.includes(LogLevel.INFO) == False
        assert LogLevel.ERROR.includes(LogLevel.WARNING) == False
        assert LogLevel.ERROR.includes(LogLevel.ERROR) == True

    # Проверить создание записи лога
    def test_log_record_creation(self):
        # Подготовка
        
        # Действие
        record = log_record(LogLevel.INFO, "Test message", "test_service")
        
        # Проверки
        assert record.level == LogLevel.INFO
        assert record.message == "Test message"
        assert record.service == "test_service"
        assert record.details == None

    # Проверить создание записи лога с деталями
    def test_log_record_with_details(self):
        # Подготовка
        details = {"user": "test", "action": "login"}
        
        # Действие
        record = log_record(LogLevel.ERROR, "Error message", "auth_service", details)
        
        # Проверки
        assert record.level == LogLevel.ERROR
        assert record.message == "Error message"
        assert record.service == "auth_service"
        assert record.details == details

    # Проверить преобразование записи лога в словарь
    def test_log_record_to_dict(self):
        # Подготовка
        details = {"param1": "value1", "param2": 123}
        
        # Действие
        record = log_record(LogLevel.WARNING, "Warning message", "test_service", details)
        record_dict = record.to_dict()
        
        # Проверки
        assert "timestamp" in record_dict
        assert record_dict["level"] == "WARNING"
        assert record_dict["service"] == "test_service"
        assert record_dict["message"] == "Warning message"
        assert record_dict["details"] == details

    # Проверить наличие событий логирования в event_type
    def test_event_type_logging_events(self):
        # Подготовка
        
        # Действие
        debug_event = event_type.debug()
        info_event = event_type.info()
        warning_event = event_type.warning()
        error_event = event_type.error()
        all_events = event_type.events()
        
        # Проверки
        assert debug_event == "debug"
        assert info_event == "info"
        assert warning_event == "warning"
        assert error_event == "error"
        assert "debug" in all_events
        assert "info" in all_events
        assert "warning" in all_events
        assert "error" in all_events

    # Проверить создание logger_service без исключений
    def test_logger_service_creation(self):
        # Подготовка
        import Src.Core.logger_service
        
        # Действие
        logger = Src.Core.logger_service.logger
        
        # Проверки
        assert logger is not None

    # Проверить что logger_service является синглтоном
    def test_logger_service_singleton(self):
        # Подготовка
        import Src.Core.logger_service
        
        # Действие
        logger1 = Src.Core.logger_service.logger
        logger2 = Src.Core.logger_service.logger
        
        # Проверки
        assert logger1 is logger2
        assert id(logger1) == id(logger2)

    # Проверить логирование без исключений
    def test_logger_logging(self):
        # Подготовка
        import Src.Core.logger_service
        logger = Src.Core.logger_service.logger
        
        # Действие
        logger.debug("Test debug message", "test")
        logger.info("Test info message", "test")
        logger.warning("Test warning message", "test")
        logger.error("Test error message", "test")
        
        # Проверки
        assert True  # Если не было исключений, тест пройден

    # Проверить логирование с деталями без исключений
    def test_logger_logging_with_details(self):
        # Подготовка
        import Src.Core.logger_service
        logger = Src.Core.logger_service.logger
        details = {"user_id": "123", "action": "create"}
        
        # Действие
        logger.info("User action performed", "user_service", details)
        
        # Проверки
        assert True  # Если не было исключений, тест пройден

    # Проверить обработку событий наблюдателем
    def test_logger_event_handling(self):
        # Подготовка
        import Src.Core.logger_service
        from Src.Core.observe_service import observe_service
        
        # Действие - создаем события
        observe_service.create_event(event_type.debug(), {
            "message": "Debug event test",
            "service": "test_service"
        })
        
        observe_service.create_event(event_type.info(), {
            "message": "Info event test",
            "service": "test_service"
        })
        
        # Проверки
        assert True  # Если не было исключений, тест пройден

    # Проверить работу метода to_string у log_record
    def test_log_record_to_string(self):
        # Подготовка
        details = {"user": "test", "action": "login"}
        
        # Действие
        record = log_record(LogLevel.INFO, "Test message", "auth_service", details)
        record_str = record.to_string()
        
        # Проверки
        assert "[INFO]" in record_str
        assert "auth_service" in record_str
        assert "Test message" in record_str

    # Проверить кастомный формат для to_string
    def test_log_record_custom_format(self):
        # Подготовка
        custom_format = "{level} - {service} - {message}"
        custom_date_format = "%d/%m/%Y"
        
        # Действие
        record = log_record(LogLevel.ERROR, "Critical error", "system", {"code": "500"})
        record_str = record.to_string(custom_format, custom_date_format)
        
        # Проверки
        assert "ERROR - system - Critical error" in record_str
        assert record.timestamp.strftime(custom_date_format) in record_str

if __name__ == '__main__':
    unittest.main()
