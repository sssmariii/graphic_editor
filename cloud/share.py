import json
import os
import uuid
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cloud.cloud_saver import CLOUD_PROJECTS_DIR, _init

# Папка для хранения ссылок
SHARE_LINKS_DIR = os.path.join(os.path.dirname(CLOUD_PROJECTS_DIR), "share_links")

def _init_share():
    if not os.path.exists(SHARE_LINKS_DIR):
        os.makedirs(SHARE_LINKS_DIR)

def create_share_link(project_id: str, token: str, can_edit: bool = False) -> dict:
    """
    Создать ссылку для доступа к проекту.
    
    Args:
        project_id: ID проекта
        token: токен владельца
        can_edit: может ли получатель редактировать
    
    Returns:
        {"ok": True, "link": "https://...", "code": "abc123"}
    """
    _init()
    _init_share()
    
    # Проверяем, что проект существует и принадлежит пользователю
    project_file = os.path.join(CLOUD_PROJECTS_DIR, f"{project_id}.json")
    if not os.path.exists(project_file):
        return {"ok": False, "error": "Проект не найден"}
    
    with open(project_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if data.get("user_token") != token:
        return {"ok": False, "error": "Нет прав на создание ссылки"}
    
    # Генерируем уникальный код
    share_code = str(uuid.uuid4())[:8]
    
    # Сохраняем ссылку
    link_data = {
        "project_id": project_id,
        "code": share_code,
        "can_edit": can_edit,
        "created_at": __import__('datetime').datetime.now().isoformat()
    }
    
    with open(os.path.join(SHARE_LINKS_DIR, f"{share_code}.json"), "w") as f:
        json.dump(link_data, f, indent=2)
    
    # Добавляем ссылку в проект
    if "share_links" not in data:
        data["share_links"] = []
    data["share_links"].append({"code": share_code, "can_edit": can_edit})
    
    with open(project_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return {
        "ok": True,
        "link": f"https://graphitium.com/share/{share_code}",
        "code": share_code
    }

def get_project_by_share_code(share_code: str) -> dict:
    """
    Открыть проект по ссылке.
    
    Returns:
        {"ok": True, "project": {...}, "can_edit": True/False}
    """
    _init_share()
    
    link_file = os.path.join(SHARE_LINKS_DIR, f"{share_code}.json")
    if not os.path.exists(link_file):
        return {"ok": False, "error": "Ссылка недействительна"}
    
    with open(link_file, "r") as f:
        link_data = json.load(f)
    
    project_id = link_data["project_id"]
    can_edit = link_data.get("can_edit", False)
    
    project_file = os.path.join(CLOUD_PROJECTS_DIR, f"{project_id}.json")
    if not os.path.exists(project_file):
        return {"ok": False, "error": "Проект не найден"}
    
    with open(project_file, "r") as f:
        project_data = json.load(f)
    
    # Убираем служебные поля
    project_data.pop("user_token", None)
    project_data.pop("share_links", None)
    
    return {"ok": True, "project": project_data, "can_edit": can_edit}

def list_share_links(project_id: str, token: str) -> dict:
    """Получить список всех ссылок на проект"""
    _init()
    
    project_file = os.path.join(CLOUD_PROJECTS_DIR, f"{project_id}.json")
    if not os.path.exists(project_file):
        return {"ok": False, "error": "Проект не найден"}
    
    with open(project_file, "r") as f:
        data = json.load(f)
    
    if data.get("user_token") != token:
        return {"ok": False, "error": "Нет прав"}
    
    links = data.get("share_links", [])
    return {"ok": True, "links": links}

def revoke_share_link(share_code: str, token: str) -> dict:
    """Отозвать ссылку (удалить)"""
    _init_share()
    
    link_file = os.path.join(SHARE_LINKS_DIR, f"{share_code}.json")
    if not os.path.exists(link_file):
        return {"ok": False, "error": "Ссылка не найдена"}
    
    with open(link_file, "r") as f:
        link_data = json.load(f)
    
    project_id = link_data["project_id"]
    
    # Проверяем права
    project_file = os.path.join(CLOUD_PROJECTS_DIR, f"{project_id}.json")
    with open(project_file, "r") as f:
        project_data = json.load(f)
    
    if project_data.get("user_token") != token:
        return {"ok": False, "error": "Нет прав"}
    
    # Удаляем ссылку
    os.remove(link_file)
    
    # Удаляем из проекта
    project_data["share_links"] = [l for l in project_data.get("share_links", []) if l.get("code") != share_code]
    with open(project_file, "w") as f:
        json.dump(project_data, f, indent=2)
    
    return {"ok": True, "code": share_code}