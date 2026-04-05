import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cloud.cloud_saver import CLOUD_PROJECTS_DIR, _init

def delete_project_from_cloud(project_id: str, token: str) -> dict:
    """Удалить проект из облака"""
    _init()
    
    project_file = os.path.join(CLOUD_PROJECTS_DIR, f"{project_id}.json")
    
    if not os.path.exists(project_file):
        return {"ok": False, "error": "Проект не найден"}
    
    with open(project_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if data.get("user_token") != token:
        return {"ok": False, "error": "Нет прав на удаление"}
    
    os.remove(project_file)
    return {"ok": True, "project_id": project_id}

def rename_project(project_id: str, token: str, new_name: str) -> dict:
    """Переименовать проект"""
    _init()
    
    project_file = os.path.join(CLOUD_PROJECTS_DIR, f"{project_id}.json")
    
    if not os.path.exists(project_file):
        return {"ok": False, "error": "Проект не найден"}
    
    with open(project_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if data.get("user_token") != token:
        return {"ok": False, "error": "Нет прав"}
    
    data["name"] = new_name
    
    with open(project_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return {"ok": True, "project_id": project_id, "new_name": new_name}

def get_project_info(project_id: str, token: str) -> dict:
    """Получить информацию о проекте без загрузки всего проекта"""
    _init()
    
    project_file = os.path.join(CLOUD_PROJECTS_DIR, f"{project_id}.json")
    
    if not os.path.exists(project_file):
        return {"ok": False, "error": "Проект не найден"}
    
    with open(project_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if data.get("user_token") != token:
        return {"ok": False, "error": "Нет доступа"}
    
    info = {
        "name": data.get("name", "Без названия"),
        "saved_at": data.get("saved_at", ""),
        "layers_count": len(data.get("layers", [])),
        "width": data.get("width", 0),
        "height": data.get("height", 0)
    }
    
    return {"ok": True, "info": info}