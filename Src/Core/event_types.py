"""
Типы событий для системы справочников
"""
class event_types:
    # События удаления
    BEFORE_DELETE_NOMENCLATURE = "before_delete_nomenclature"
    BEFORE_DELETE_GROUP = "before_delete_group" 
    BEFORE_DELETE_RANGE = "before_delete_range"
    BEFORE_DELETE_STORAGE = "before_delete_storage"
    
    # События обновления
    AFTER_UPDATE_NOMENCLATURE = "after_update_nomenclature"
    AFTER_UPDATE_GROUP = "after_update_group"
    AFTER_UPDATE_RANGE = "after_update_range" 
    AFTER_UPDATE_STORAGE = "after_update_storage"
    
    # События создания
    AFTER_CREATE_NOMENCLATURE = "after_create_nomenclature"
    AFTER_CREATE_GROUP = "after_create_group"
    AFTER_CREATE_RANGE = "after_create_range"
    AFTER_CREATE_STORAGE = "after_create_storage"
    
    # Системные события
    SETTINGS_CHANGED = "settings_changed"
    DATA_EXPORT_NEEDED = "data_export_needed"
