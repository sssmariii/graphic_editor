import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Папка для облачных проектов (локально)
CLOUD_PROJECTS_DIR = os.path.join(os.path.expanduser("~"), "GraphicEditorCloud", "projects")

def _init():
    if not os.path.exists(CLOUD_PROJECTS_DIR):
        os.makedirs(CLOUD_PROJECTS_DIR)

def save_project_to_cloud(project, token: str, name: str = "Без названия") -> dict:
    """
    Сохранить проект в облако.
    
    Args:
        project: объект Project от Лизы (словарь)
        token: токен пользователя
        name: название проекта
    
    Returns:
        {"ok": True, "project_id": "...", "cloud_file": "..."}
    """
    _init()
    
    # 1. Конвертируем проект в JSON с base64
    # Пока просто копируем данные
    cloud_json = project.copy() if isinstance(project, dict) else {}
    cloud_json["name"] = name
    cloud_json["user_token"] = token
    cloud_json["saved_at"] = datetime.now().isoformat()
    
    # 2. Сохраняем в файл (имитация облака)
    import uuid
    project_id = str(uuid.uuid4())[:8]
    cloud_json["project_id"] = project_id
    
    cloud_file = os.path.join(CLOUD_PROJECTS_DIR, f"{project_id}.json")
    with open(cloud_file, "w", encoding="utf-8") as f:
        json.dump(cloud_json, f, indent=2, ensure_ascii=False)
    
    return {"ok": True, "project_id": project_id, "cloud_file": cloud_file}

def load_project_from_cloud(project_id: str, token: str) -> dict:
    """
    Загрузить проект из облака.
    
    Returns:
        {"ok": True, "project": проект_для_ядра, "name": "..."}
    """
    cloud_file = os.path.join(CLOUD_PROJECTS_DIR, f"{project_id}.json")
    
    if not os.path.exists(cloud_file):
        return {"ok": False, "error": "Проект не найден"}
    
    with open(cloud_file, "r", encoding="utf-8") as f:
        cloud_json = json.load(f)
    
    # Проверяем права
    if cloud_json.get("user_token") != token:
        return {"ok": False, "error": "Нет доступа к проекту"}
    
    # Убираем служебные поля
    project = cloud_json.copy()
    project.pop("user_token", None)
    project.pop("saved_at", None)
    project.pop("project_id", None)
    
    name = cloud_json.get("name", "Без названия")
    
    return {"ok": True, "project": project, "name": name}

def list_user_projects(token: str) -> dict:
    """Список проектов пользователя"""
    _init()
    projects = []
    
    if os.path.exists(CLOUD_PROJECTS_DIR):
        for filename in os.listdir(CLOUD_PROJECTS_DIR):
            filepath = os.path.join(CLOUD_PROJECTS_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("user_token") == token:
                    projects.append({
                        "id": data.get("project_id"),
                        "name": data.get("name", "Без названия"),
                        "saved_at": data.get("saved_at", "")
                    })
    
    return {"ok": True, "projects": projects}