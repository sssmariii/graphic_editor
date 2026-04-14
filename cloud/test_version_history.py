import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cloud.version_history import save_version, load_version, list_versions, delete_version, delete_all_versions

def test_version_history():
    print("=== Тест истории версий ===\n")
    
    project_id = "test_project_versions"
    
    # 1. Создаём несколько версий
    print("1. Сохранение версий...")
    v1 = save_version(project_id, {"name": "Версия 1", "data": "content1"}, "Первая версия")
    print(f"   Версия 1: {v1.get('version_name')}")
    
    v2 = save_version(project_id, {"name": "Версия 2", "data": "content2"}, "Вторая версия")
    print(f"   Версия 2: {v2.get('version_name')}")
    
    v3 = save_version(project_id, {"name": "Версия 3", "data": "content3"}, "Третья версия")
    print(f"   Версия 3: {v3.get('version_name')}")
    
    # 2. Список версий
    print("\n2. Список версий:")
    versions = list_versions(project_id)
    for v in versions.get("versions", []):
        print(f"     - {v['name']} (id: {v['id']})")
    
    # 3. Загрузка версии
    if versions.get("versions"):
        version_id = versions["versions"][0]["id"]
        print(f"\n3. Загрузка версии {version_id}...")
        loaded = load_version(project_id, version_id)
        if loaded.get("ok"):
            print(f"   Загружено: {loaded.get('version_name')}")
    
    # 4. Удаление одной версии
    if versions.get("versions") and len(versions["versions"]) > 1:
        to_delete = versions["versions"][-1]["id"]
        print(f"\n4. Удаление версии {to_delete}...")
        deleted = delete_version(project_id, to_delete)
        print(f"   Результат: {deleted.get('ok')}")
    
    # 5. Список после удаления
    print("\n5. Список версий после удаления:")
    versions_after = list_versions(project_id)
    for v in versions_after.get("versions", []):
        print(f"     - {v['name']} (id: {v['id']})")
    
    # 6. Очистка всех версий
    print("\n6. Очистка всех версий...")
    delete_all_versions(project_id)
    versions_final = list_versions(project_id)
    print(f"   Версий осталось: {len(versions_final.get('versions', []))}")
    
    print("\n=== Тест пройден ===")

if __name__ == "__main__":
    test_version_history()