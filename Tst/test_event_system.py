import unittest
from Src.Core.event_manager import event_manager
from Src.Core.event_types import event_types

class test_event_system(unittest.TestCase):

    # Проверить подписку на события
    def test_notThrow_event_subscription(self):
        # Подготовка
        event_called = False

        def test_handler():
            nonlocal event_called
            event_called = True

        # Действие
        event_manager.subscribe(event_types.DATA_EXPORT_NEEDED, test_handler)
        event_manager.notify(event_types.DATA_EXPORT_NEEDED)

        # Проверка
        assert event_called == True

        # Очистка
        event_manager.unsubscribe(event_types.DATA_EXPORT_NEEDED, test_handler)

    # Проверить отписку от событий
    def test_notThrow_event_unsubscription(self):
        # Подготовка
        event_called = False

        def test_handler():
            nonlocal event_called
            event_called = True

        event_manager.subscribe(event_types.DATA_EXPORT_NEEDED, test_handler)
        event_manager.unsubscribe(event_types.DATA_EXPORT_NEEDED, test_handler)

        # Действие
        event_manager.notify(event_types.DATA_EXPORT_NEEDED)

        # Проверка
        assert event_called == False

    # Проверить обработку исключений в обработчиках
    def test_notThrow_handler_exceptions(self):
        # Подготовка
        def failing_handler():
            raise Exception("Test exception")

        event_manager.subscribe(event_types.DATA_EXPORT_NEEDED, failing_handler)

        # Действие и проверка
        try:
            event_manager.notify(event_types.DATA_EXPORT_NEEDED)
            assert True
        except Exception:
            assert False

        # Очистка
        event_manager.unsubscribe(event_types.DATA_EXPORT_NEEDED, failing_handler)

if __name__ == '__main__':
    unittest.main()
