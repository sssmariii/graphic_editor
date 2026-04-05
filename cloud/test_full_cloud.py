import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cloud.auth.auth import register, login
from cloud.cloud_saver import save_project_to_cloud, load_project_from_cloud, list_user_projects
from api.editor_api import (
    export_project_to_cloud, 
    import_project_from_cloud,
    create_project,
    add_layer,
    get_layers
)

def test_full():
    print("=== Полный тест облачного модуля (с функциями Лизы) ===\n")
    
    # 1. Создаём активный проект через API Лизы
    print("1. Создание активного проекта...")
    result = create_project(800, 600)
    if result.get("status") == "ok":
        print(f"   ✅ Проект создан: {result['width']}x{result['height']}")
    else:
        print(f"   ❌ {result.get('error')}")
        return
    
    # 2. Добавляем тестовый слой
    print("\n2. Добавление тестового слоя...")
    layer_result = add_layer("Фоновый слой")
    if layer_result.get("status") == "ok":
        print(f"   ✅ Слой добавлен (index: {layer_result['layer_index']})")
    else:
        print(f"   ⚠️ {layer_result.get('error')}")
    
    # 3. Проверяем, что функции Лизы работают с активным проектом
    print("\n3. Проверка export_project_to_cloud()...")
    export_result = export_project_to_cloud()
    if export_result.get("status") == "ok":
        print(f"   ✅ export_project_to_cloud() работает")
        project_data = export_result["project_data"]
        print(f"   Размер: {project_data['width']}x{project_data['height']}")
        print(f"   Слоёв: {len(project_data['layers'])}")
        for i, layer in enumerate(project_data['layers']):
            has_image = "✅" if layer.get("image_base64") else "❌"
            print(f"     Слой {i+1}: {layer['name']} (base64: {has_image})")
    else:
        print(f"   ❌ {export_result.get('error')}")
        return
    
    # 4. Регистрация и вход
    print("\n4. Регистрация...")
    reg_result = register("sync@test.com", "123456")
    if reg_result.get("ok"):
        print(f"   ✅ Регистрация успешна")
    else:
        print(f"   ⚠️ {reg_result.get('error')}")
    
    auth = login("sync@test.com", "123456")
    if not auth.get("ok"):
        print(f"   ❌ Ошибка входа: {auth.get('error')}")
        return
    
    token = auth["token"]
    print(f"   Токен: {token[:20]}...")
    
    # 5. Сохранение проекта в облако
    print("\n5. Сохранение проекта в облако...")
    saved = save_project_to_cloud(project_data, token, "Мой облачный проект")
    print(f"   {saved}")
    
    if not saved.get("ok"):
        print(f"   ❌ Не удалось сохранить проект: {saved.get('error')}")
        return
    
    # 6. Список проектов
    print("\n6. Список проектов...")
    projects = list_user_projects(token)
    print(f"   Проектов: {len(projects.get('projects', []))}")
    for p in projects.get('projects', []):
        print(f"     - {p['name']} (id: {p['id']})")
    
    # 7. Загрузка проекта
    print("\n7. Загрузка проекта из облака...")
    loaded = load_project_from_cloud(saved["project_id"], token)
    if loaded.get("ok"):
        print(f"   ✅ Загружен: {loaded['name']}")
        project = loaded.get("project", {})
        print(f"   Размер: {project.get('width', '?')}x{project.get('height', '?')}")
        print(f"   Слоёв: {len(project.get('layers', []))}")
    else:
        print(f"   ❌ {loaded.get('error')}")
    
    print("\n=== Тест пройден ===")

if __name__ == "__main__":
    test_full()