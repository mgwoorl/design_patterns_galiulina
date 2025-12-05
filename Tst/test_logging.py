import unittest
import os
import tempfile
import json
from unittest.mock import patch

from Src.Core.logger_service import logger
from Src.Core.observe_service import observe_service
from Src.Core.event_type import event_type
from Src.Core.log_level import LogLevel

"""
Набор тестов для системы логирования
"""
class test_logging(unittest.TestCase):

    def test_notThrow_logger_creation(self):
        """
        Проверяет создание логгера без исключений
        """
        # Подготовка
        
        # Действие
        log_service = logger
        
        # Проверка
        assert log_service is not None

    def test_notThrow_logging_different_levels(self):
        """
        Проверяет логирование на разных уровнях
        """
        # Подготовка
        
        # Действие - тестируем через моки
        with patch.object(logger, '_write_log') as mock_write:
            logger.debug("Тестовое сообщение DEBUG", "test")
            logger.info("Тестовое сообщение INFO", "test")
            logger.warning("Тестовое сообщение WARNING", "test")
            logger.error("Тестовое сообщение ERROR", "test")

        # Проверка
        assert True  # Если не было исключений, тест пройден

    def test_log_level_from_string(self):
        """
        Проверяет преобразование строк в уровни логирования
        """
        # Подготовка
        
        # Действие
        debug_level = LogLevel.from_string("DEBUG")
        info_level = LogLevel.from_string("INFO")
        warning_level = LogLevel.from_string("WARNING")
        error_level = LogLevel.from_string("ERROR")
        default_level = LogLevel.from_string("UNKNOWN")
        
        # Проверка
        assert debug_level == LogLevel.DEBUG
        assert info_level == LogLevel.INFO
        assert warning_level == LogLevel.WARNING
        assert error_level == LogLevel.ERROR
        assert default_level == LogLevel.INFO  # По умолчанию INFO

    def test_log_level_includes(self):
        """
        Проверяет иерархию уровней логирования
        """
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

    def test_event_type_logging_events(self):
        """
        Проверяет наличие событий логирования в event_type
        """
        # Подготовка
        
        # Действие
        debug_event = event_type.debug()
        info_event = event_type.info()
        warning_event = event_type.warning()
        error_event = event_type.error()
        all_events = event_type.events()
        
        # Проверка
        assert debug_event == "debug"
        assert info_event == "info"
        assert warning_event == "warning"
        assert error_event == "error"
        assert "debug" in all_events
        assert "info" in all_events
        assert "warning"
