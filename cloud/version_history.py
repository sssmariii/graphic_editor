import os
import json
import shutil
from datetime import datetime

# Папка для хранения версий
VERSIONS_DIR = os.path.join(os.path.expanduser("~"), "GraphitiumVersions")

def _init_versions():
    if not os.path.exists(VERSIONS_DIR):
        os.makedirs(VERSIONS_DIR)

def save_version(project_id: str, project_data: dict, version_name: str = None) -> dict:
    """
    Сохранить новую версию проекта.
    
    Args:
        project_id: ID проекта
        project_data: данные проекта
        version_name: название версии (если не указано - авто)
    
    Returns:
        {"ok": True, "version_id": "...", "version_name": "..."}
    """
    _init_versions()
    
    # Создаём папку для проекта, если её нет
    project_versions_dir = os.path.join(VERSIONS_DIR, project_id)
    if not os.path.exists(project_versions_dir):
        os.makedirs(project_versions_dir)
    
    # Генерируем название версии
    if not version_name:
        version_name = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Создаём версию
    version_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    version_data = {
        "version_id": version_id,
        "project_id": project_id,
        "name": version_name,
        "created_at": datetime.now().isoformat(),
        "data": project_data
    }
    
    # Сохраняем версию
    version_file = os.path.join(project_versions_dir, f"{version_id}.json")
    with open(version_file, "w", encoding="utf-8") as f:
        json.dump(version_data, f, indent=2, ensure_ascii=False)
    
    # Ограничиваем количество версий (оставляем последние 10)
    _limit_versions(project_id, 10)
    
    return {"ok": True, "version_id": version_id, "version_name": version_name}

def _limit_versions(project_id: str, max_versions: int = 10):
    """Оставить только последние max_versions версий"""
    project_versions_dir = os.path.join(VERSIONS_DIR, project_id)
    if not os.path.exists(project_versions_dir):
        return
    
    # Получаем все версии, сортируем по дате
    versions = []
    for filename in os.listdir(project_versions_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(project_versions_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                versions.append({
                    "file": filepath,
                    "version_id": data.get("version_id"),
                    "created_at": data.get("created_at", "")
                })
    
    # Сортируем по дате (новые сначала)
    versions.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Удаляем старые
    for old_version in versions[max_versions:]:
        os.remove(old_version["file"])

def load_version(project_id: str, version_id: str) -> dict:
    """
    Загрузить конкретную версию проекта.
    
    Returns:
        {"ok": True, "version": {...}, "name": "..."}
    """
    version_file = os.path.join(VERSIONS_DIR, project_id, f"{version_id}.json")
    if not os.path.exists(version_file):
        return {"ok": False, "error": "Версия не найдена"}
    
    with open(version_file, "r", encoding="utf-8") as f:
        version_data = json.load(f)
    
    return {
        "ok": True,
        "project": version_data.get("data"),
        "version_name": version_data.get("name"),
        "created_at": version_data.get("created_at")
    }

def list_versions(project_id: str) -> dict:
    """
    Получить список всех версий проекта.
    
    Returns:
        {"ok": True, "versions": [{"id": "...", "name": "...", "created_at": "..."}]}
    """
    project_versions_dir = os.path.join(VERSIONS_DIR, project_id)
    if not os.path.exists(project_versions_dir):
        return {"ok": True, "versions": []}
    
    versions = []
    for filename in os.listdir(project_versions_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(project_versions_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                versions.append({
                    "id": data.get("version_id"),
                    "name": data.get("name"),
                    "created_at": data.get("created_at")
                })
    
    # Сортируем по дате (новые сначала)
    versions.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {"ok": True, "versions": versions}

def delete_version(project_id: str, version_id: str) -> dict:
    """
    Удалить конкретную версию.
    """
    version_file = os.path.join(VERSIONS_DIR, project_id, f"{version_id}.json")
    if not os.path.exists(version_file):
        return {"ok": False, "error": "Версия не найдена"}
    
    os.remove(version_file)
    return {"ok": True}

def delete_all_versions(project_id: str) -> dict:
    """
    Удалить все версии проекта.
    """
    project_versions_dir = os.path.join(VERSIONS_DIR, project_id)
    if os.path.exists(project_versions_dir):
        shutil.rmtree(project_versions_dir)
    return {"ok": True}