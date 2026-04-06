"""
Сервер для веб-страницы "Мои проекты" с Firebase Google OAuth.
"""

from flask import Flask, send_from_directory, jsonify, request, session, redirect, url_for
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cloud.auth.auth import login, register, google_auth
from cloud.cloud_saver import list_user_projects, load_project_from_cloud
from cloud.cloud_manager import delete_project_from_cloud

# Инициализация Firebase
import firebase_admin
from firebase_admin import credentials, auth

# Путь к файлу с ключами
cred_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "serviceAccountKey.json")
if os.path.exists(cred_path):
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    print("✅ Firebase инициализирован")
else:
    print(f"⚠️ Файл {cred_path} не найден. Google OAuth не будет работать.")

app = Flask(__name__, static_folder='../web')
app.secret_key = os.urandom(24)

# ========== API ДЛЯ ВЕБ-СТРАНИЦЫ ==========

@app.route('/')
def index():
    """Главная страница — Мои проекты"""
    return send_from_directory('../web', 'projects.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    result = login(data.get('email'), data.get('password'))
    if result.get("ok"):
        session['user_token'] = result.get("token")
    return jsonify(result)

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    result = register(data.get('email'), data.get('password'))
    return jsonify(result)

@app.route('/api/firebase-google-login', methods=['POST'])
def api_firebase_google_login():
    """Вход через Google с Firebase"""
    data = request.get_json()
    id_token = data.get('id_token')
    
    if not id_token:
        return jsonify({"ok": False, "error": "No id_token provided"})
    
    try:
        # Проверяем токен через Firebase Admin SDK
        decoded_token = auth.verify_id_token(id_token)
        email = decoded_token.get('email')
        name = decoded_token.get('name', '')
        
        # Аутентифицируем в нашей системе
        result = google_auth(email, name)
        
        if result.get("ok"):
            session['user_token'] = result.get("token")
            session['user_email'] = email
            session['user_name'] = name
            result["email"] = email
            result["name"] = name
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})

@app.route('/api/projects', methods=['GET'])
def api_projects():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        token = session.get('user_token')
    result = list_user_projects(token)
    return jsonify(result)

@app.route('/api/projects/<project_id>', methods=['DELETE'])
def api_delete_project(project_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        token = session.get('user_token')
    result = delete_project_from_cloud(project_id, token)
    return jsonify(result)

@app.route('/api/user', methods=['GET'])
def api_user():
    """Получить информацию о текущем пользователе"""
    if session.get('user_token'):
        return jsonify({
            "ok": True,
            "email": session.get('user_email'),
            "name": session.get('user_name')
        })
    return jsonify({"ok": False, "error": "Not logged in"})

@app.route('/logout')
def logout():
    """Выход из аккаунта"""
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    print("🚀 Сервер запущен: http://localhost:5000")
    print("📁 Открой в браузере: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)