import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cloud.auth.auth import register, login
from cloud.cloud_saver import save_project_to_cloud, list_user_projects
from cloud.cloud_manager import delete_project_from_cloud, rename_project, get_project_info

def test_manager():
    print("Тест управления проектами\n")
    
    # 1. Регистрация и вход
    register("manager@test.com", "123456")
    auth = login("manager@test.com", "123456")
    token = auth["token"]
    print(f"1. Токен: {token[:20]}...")
    
    # 2. Создаём тестовый проект
    test_project = {
        "name": "Тестовый проект",
        "width": 800,
        "height": 600,
        "layers": [{"name": "Слой 1", "visible": True}]
    }
    
    saved = save_project_to_cloud(test_project, token, "Проект для теста")
    project_id = saved["project_id"]
    print(f"2. Создан проект: {project_id}")
    
    # 3. Получить информацию о проекте
    info = get_project_info(project_id, token)
    print(f"3. Информация: {info.get('info', {}).get('name')}")
    
    # 4. Переименовать проект
    renamed = rename_project(project_id, token, "Новое название")
    print(f"4. Переименование: {renamed.get('ok')}")
    
    # 5. Список проектов
    projects = list_user_projects(token)
    print(f"5. Проектов в списке: {len(projects.get('projects', []))}")
    for p in projects.get('projects', []):
        print(f"     - {p['name']} ({p['id']})")
    
    # 6. Удалить проект
    deleted = delete_project_from_cloud(project_id, token)
    print(f"6. Удаление: {deleted.get('ok')}")
    
    # 7. Проверить, что проект удалён
    projects_after = list_user_projects(token)
    print(f"7. Проектов после удаления: {len(projects_after.get('projects', []))}")
    
    print("\nТест управления проектами пройден")

if __name__ == "__main__":
    test_manager()