import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cloud.auth.auth import register, login
from cloud.cloud_saver import save_project_to_cloud, load_project_from_cloud, list_user_projects

def test_full():
    print("=== Полный тест облачного модуля ===\n")
    
    # 1. Загружаем тестовый проект (из cloud_export.json или test_project)
    cloud_export_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cloud_export.json")
    
    if os.path.exists(cloud_export_path):
        with open(cloud_export_path, "r", encoding="utf-8") as f:
            original_project = json.load(f)
        print(f"1. Исходный проект из cloud_export.json: {original_project['width']}x{original_project['height']}, {len(original_project['layers'])} слоёв")
    else:
        # Альтернатива: загружаем из test_project
        test_project_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_project", "project.json")
        with open(test_project_path, "r", encoding="utf-8") as f:
            original_project = json.load(f)
        print(f"1. Исходный проект из test_project: {original_project['width']}x{original_project['height']}, {len(original_project['layers'])} слоёв")
    
    # 2. Регистрация пользователя
    print("\n2. Регистрация...")
    reg = register("cloud@test.com", "123456")
    print(f"   {reg}")
    
    # 3. Вход
    print("\n3. Вход...")
    auth = login("cloud@test.com", "123456")
    print(f"   {auth}")
    
    if not auth["ok"]:
        print("Ошибка входа!")
        return
    
    token = auth["token"]
    
    # 4. Сохранение в облако
    print("\n4. Сохранение проекта в облако...")
    saved = save_project_to_cloud(original_project, token, "Мой облачный проект")
    print(f"   {saved}")
    
    # 5. Список проектов
    print("\n5. Список проектов...")
    projects = list_user_projects(token)
    print(f"   Проектов: {len(projects['projects'])}")
    for p in projects['projects']:
        print(f"     - {p['name']} (id: {p['id']})")
    
    # 6. Загрузка из облака
    if saved["ok"]:
        print("\n6. Загрузка проекта из облака...")
        loaded = load_project_from_cloud(saved["project_id"], token)
        if loaded["ok"]:
            print(f"   Загружен: {loaded['name']}")
            print(f"   Размер: {loaded['project'].get('width', '?')}x{loaded['project'].get('height', '?')}")
            print(f"   Слоёв: {len(loaded['project'].get('layers', []))}")
        else:
            print(f"   ❌ {loaded.get('error')}")
    
    print("\nТест пройден")

if __name__ == "__main__":
    test_full()