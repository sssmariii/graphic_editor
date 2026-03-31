"""
Облачный модуль для графического редактора Graphitium.

Использование:
    from cloud import register, login, save_project_to_cloud, load_project_from_cloud
"""

# Авторизация
from cloud.auth.auth import register, login, get_user

# Основные операции с проектами
from cloud.cloud_saver import (
    save_project_to_cloud,
    load_project_from_cloud,
    list_user_projects
)

# Управление проектами
from cloud.cloud_manager import (
    delete_project_from_cloud,
    rename_project,
    get_project_info
)

# Шаринг (ссылки для доступа)
from cloud.share import (
    create_share_link,
    get_project_by_share_code,
    revoke_share_link
)

# Экспортируем всё для удобного импорта
__all__ = [
    # Авторизация
    'register',
    'login',
    'get_user',
    
    # Основные операции
    'save_project_to_cloud',
    'load_project_from_cloud',
    'list_user_projects',
    
    # Управление
    'delete_project_from_cloud',
    'rename_project',
    'get_project_info',
    
    # Шаринг
    'create_share_link',
    'get_project_by_share_code',
    'revoke_share_link'
]