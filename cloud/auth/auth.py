import hashlib
import json
import os
import uuid
from datetime import datetime

# Папка для хранения пользователей (локально, пока нет Firebase)
USERS_DIR = os.path.join(os.path.expanduser("~"), "GraphicEditorCloud", "users")

def _init():
    """Создать папку для пользователей"""
    if not os.path.exists(USERS_DIR):
        os.makedirs(USERS_DIR)

def _hash_password(password: str) -> str:
    """Хеширование пароля"""
    return hashlib.sha256(password.encode()).hexdigest()

def register(email: str, password: str) -> dict:
    """
    Регистрация нового пользователя.
    
    Args:
        email: Email пользователя
        password: Пароль (будет захэширован)
    
    Returns:
        {"ok": True, "user_id": "...", "token": "..."}
        или {"ok": False, "error": "..."}
    """
    _init()
    
    # Проверяем, не существует ли уже такой email
    if os.path.exists(USERS_DIR):
        for filename in os.listdir(USERS_DIR):
            with open(os.path.join(USERS_DIR, filename)) as f:
                user = json.load(f)
                if user["email"] == email:
                    return {"ok": False, "error": "Пользователь с таким email уже существует"}
    
    # Создаём нового пользователя
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "email": email,
        "password_hash": _hash_password(password),
        "created_at": datetime.now().isoformat()
    }
    
    with open(os.path.join(USERS_DIR, f"{user_id}.json"), "w") as f:
        json.dump(user, f, indent=2)
    
    return {"ok": True, "user_id": user_id, "token": user_id}

def login(email: str, password: str) -> dict:
    """
    Вход пользователя.
    
    Returns:
        {"ok": True, "user_id": "...", "token": "..."}
        или {"ok": False, "error": "..."}
    """
    _init()
    
    password_hash = _hash_password(password)
    
    if os.path.exists(USERS_DIR):
        for filename in os.listdir(USERS_DIR):
            with open(os.path.join(USERS_DIR, filename)) as f:
                user = json.load(f)
                if user["email"] == email and user["password_hash"] == password_hash:
                    return {"ok": True, "user_id": user["id"], "token": user["id"]}
    
    return {"ok": False, "error": "Неверный email или пароль"}

def get_user(token: str) -> dict:
    """Получить информацию о пользователе по токену"""
    _init()
    user_path = os.path.join(USERS_DIR, f"{token}.json")
    if not os.path.exists(user_path):
        return {"ok": False, "error": "Неверный токен"}
    
    with open(user_path) as f:
        user = json.load(f)
    
    return {"ok": True, "user": {"id": user["id"], "email": user["email"]}}