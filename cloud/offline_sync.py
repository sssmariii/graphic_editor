import os
import json
from datetime import datetime

# Папка для локальных копий проектов
LOCAL_BACKUP_DIR = os.path.join(os.path.expanduser("~"), "GraphitiumLocal", "projects")

def _init_local():
    if not os.path.exists(LOCAL_BACKUP_DIR):
        os.makedirs(LOCAL_BACKUP_DIR)

def save_local_copy(project_id: str, project_data: dict, name: str = "Без названия"):
    """
    Сохранить локальную копию проекта.
    """
    _init_local()
    filepath = os.path.join(LOCAL_BACKUP_DIR, f"{project_id}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump({
            "project_id": project_id,
            "name": name,
            "data": project_data,
            "last_saved": datetime.now().isoformat()
        }, f, indent=2, ensure_ascii=False)
    return {"ok": True, "file": filepath}

def load_local_copy(project_id: str):
    """
    Загрузить локальную копию проекта.
    """
    filepath = os.path.join(LOCAL_BACKUP_DIR, f"{project_id}.json")
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def list_local_projects():
    """
    Получить список всех локальных проектов.
    """
    _init_local()
    projects = []
    for filename in os.listdir(LOCAL_BACKUP_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(LOCAL_BACKUP_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                projects.append({
                    "id": data.get("project_id"),
                    "name": data.get("name", "Без названия"),
                    "last_saved": data.get("last_saved", "")
                })
    return projects

def delete_local_copy(project_id: str):
    """
    Удалить локальную копию проекта.
    """
    filepath = os.path.join(LOCAL_BACKUP_DIR, f"{project_id}.json")
    if os.path.exists(filepath):
        os.remove(filepath)
        return {"ok": True}
    return {"ok": False, "error": "Файл не найден"}