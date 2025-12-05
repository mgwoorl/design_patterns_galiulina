import os
from datetime import datetime
from Src.Core.log_handler import log_handler
from Src.Core.log_record import log_record
from Src.Core.log_level import LogLevel
from Src.Core.validator import validator, operation_exception

"""
Обработчик логов для записи в файл
"""
class file_log_handler(log_handler):
    __min_level: LogLevel
    __file_path: str
    __max_file_size: int = 10 * 1024 * 1024
    __backup_count: int = 5

    def __init__(self, file_path: str, min_level: LogLevel = LogLevel.DEBUG):
        validator.validate(file_path, str)
        validator.validate(min_level, LogLevel)

        self.__min_level = min_level
        self.__file_path = file_path

        # Создаем директорию если ее нет
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

    def handle(self, log_record: log_record):
        """
        Записать запись лога в файл

        Args:
            log_record (log_record): запись лога для записи
        """
        validator.validate(log_record, log_record)

        if not self.should_handle(log_record):
            return

        try:
            # Проверяем ротацию файлов
            self.__check_rotation()

            # Записываем лог
            with open(self.__file_path, 'a', encoding='utf-8') as f:
                f.write(log_record.to_string() + "\n")

        except Exception as e:
            raise operation_exception(f"Ошибка записи лога в файл: {str(e)}")

    def should_handle(self, log_record: log_record) -> bool:
        """
        Проверить, должен ли обработчик обработать данную запись

        Args:
            log_record (log_record): запись лога для проверки

        Returns:
            bool: True если уровень лога >= минимальному уровню
        """
        validator.validate(log_record, log_record)
        return self.__min_level.includes(log_record.level)

    def __check_rotation(self):
        """
        Проверить необходимость ротации лог-файлов
        """
        if not os.path.exists(self.__file_path):
            return

        file_size = os.path.getsize(self.__file_path)
        if file_size >= self.__max_file_size:
            self.__rotate_files()

    def __rotate_files(self):
        """
        Выполнить ротацию лог-файлов
        """
        # Удаляем самый старый backup
        oldest_backup = f"{self.__file_path}.{self.__backup_count}"
        if os.path.exists(oldest_backup):
            os.remove(oldest_backup)

        # Сдвигаем существующие backup
        for i in range(self.__backup_count - 1, 0, -1):
            old_name = f"{self.__file_path}.{i}"
            new_name = f"{self.__file_path}.{i + 1}"
            if os.path.exists(old_name):
                os.rename(old_name, new_name)

        # Переименовываем текущий файл в backup.1
        if os.path.exists(self.__file_path):
            os.rename(self.__file_path, f"{self.__file_path}.1")
