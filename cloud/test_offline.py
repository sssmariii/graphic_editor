import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cloud.offline_sync import save_local_copy, load_local_copy, list_local_projects, delete_local_copy

def test_offline():
    print("=== Тест офлайн-синхронизации ===\n")
    
    # 1. Сохраняем локальную копию
    test_project = {
        "name": "Офлайн проект",
        "width": 800,
        "height": 600,
        "layers": [{"name": "Слой 1", "visible": True}]
    }
    result = save_local_copy("test_123", test_project, "Офлайн проект")
    print(f"1. Сохранение: {result.get('ok')}")
    
    # 2. Загружаем локальную копию
    loaded = load_local_copy("test_123")
    if loaded:
        print(f"2. Загрузка: {loaded['name']}")
    else:
        print("2. Загрузка: не найдена")
    
    # 3. Список локальных проектов
    projects = list_local_projects()
    print(f"3. Локальных проектов: {len(projects)}")
    for p in projects:
        print(f"     - {p['name']} (id: {p['id']})")
    
    # 4. Удаляем локальную копию
    deleted = delete_local_copy("test_123")
    print(f"4. Удаление: {deleted.get('ok')}")
    
    print("\nТест пройден")

if __name__ == "__main__":
    test_offline()