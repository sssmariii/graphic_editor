import json
import os
import sys
import uuid
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.editor_api import export_project_to_cloud, import_project_from_cloud
from cloud.version_history import save_version

CLOUD_PROJECTS_DIR = os.path.join(os.path.expanduser("~"), "GraphicEditorCloud", "projects")

def _init():
    if not os.path.exists(CLOUD_PROJECTS_DIR):
        os.makedirs(CLOUD_PROJECTS_DIR)

def save_project_to_cloud(project, token: str, name: str = "Без названия") -> dict:
    """
    Сохранить проект в облако, используя функцию Лизы export_project_to_cloud().
    
    Args:
        project: объект Project от Лизы (словарь) — не используется, т.к. export берёт из глобального состояния
        token: токен пользователя
        name: название проекта
    
    Returns:
        {"ok": True, "project_id": "...", "cloud_file": "..."}
    """
    _init()
    
    # 1. Вызываем функцию Лизы для экспорта в JSON с base64
    export_result = export_project_to_cloud()
    
    # Проверяем status (у Лизы используется "status", а не "ok")
    if export_result.get("status") != "ok":
        return {"ok": False, "error": export_result.get("error", "Ошибка экспорта проекта")}
    
    cloud_json = export_result["project_data"]
    cloud_json["name"] = name
    cloud_json["user_token"] = token
    cloud_json["saved_at"] = datetime.now().isoformat()
    
    # 2. Генерируем ID и сохраняем
    project_id = str(uuid.uuid4())[:8]
    cloud_json["project_id"] = project_id
    
    cloud_file = os.path.join(CLOUD_PROJECTS_DIR, f"{project_id}.json")
    with open(cloud_file, "w", encoding="utf-8") as f:
        json.dump(cloud_json, f, indent=2, ensure_ascii=False)
    
    # 3. Сохраняем версию в историю
    try:
        save_version(project_id, cloud_json, name)
    except Exception as e:
        print(f"Warning: Failed to save version history: {e}")
    
    return {"ok": True, "project_id": project_id, "cloud_file": cloud_file}

def load_project_from_cloud(project_id: str, token: str) -> dict:
    """
    Загрузить проект из облака, используя функцию Лизы import_project_from_cloud().
    
    Returns:
        {"ok": True, "project": {...}, "name": "..."}
    """
    _init()
    
    cloud_file = os.path.join(CLOUD_PROJECTS_DIR, f"{project_id}.json")
    if not os.path.exists(cloud_file):
        return {"ok": False, "error": "Проект не найден"}
    
    with open(cloud_file, "r", encoding="utf-8") as f:
        cloud_json = json.load(f)
    
    # Проверяем права доступа
    if cloud_json.get("user_token") != token:
        return {"ok": False, "error": "Нет доступа к проекту"}
    
    # Вызываем функцию Лизы для импорта
    import_result = import_project_from_cloud(cloud_json)
    
    # Проверяем status (у Лизы используется "status", а не "ok")
    if import_result.get("status") != "ok":
        return {"ok": False, "error": import_result.get("error", "Ошибка импорта проекта")}
    
    return {
        "ok": True,
        "project": cloud_json,
        "name": cloud_json.get("name", "Без названия")
    }

def list_user_projects(token: str) -> dict:
    """Получить список всех проектов пользователя"""
    _init()
    projects = []
    
    if not os.path.exists(CLOUD_PROJECTS_DIR):
        return {"ok": True, "projects": []}
    
    for filename in os.listdir(CLOUD_PROJECTS_DIR):
        filepath = os.path.join(CLOUD_PROJECTS_DIR, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("user_token") == token:
                    projects.append({
                        "id": data.get("project_id"),
                        "name": data.get("name", "Без названия"),
                        "saved_at": data.get("saved_at", "")
                    })
        except (json.JSONDecodeError, IOError):
            continue  # Пропускаем повреждённые файлы
    
    return {"ok": True, "projects": projects}