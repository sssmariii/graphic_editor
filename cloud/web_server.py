"""
Сервер для веб-страницы "Мои проекты" с AI генерацией и шарингом.
"""

from flask import Flask, send_from_directory, jsonify, request, session, redirect, url_for
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cloud.auth.auth import login, register
from cloud.cloud_saver import list_user_projects, load_project_from_cloud
from cloud.cloud_manager import delete_project_from_cloud

# ========== ИНИЦИАЛИЗАЦИЯ (Firebase отключён) ==========
# Google OAuth не используется в MVP, поэтому Firebase закомментирован
# import firebase_admin
# from firebase_admin import credentials, auth

# cred_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "serviceAccountKey.json")
# if os.path.exists(cred_path):
#     cred = credentials.Certificate(cred_path)
#     firebase_admin.initialize_app(cred)
#     print("✅ Firebase инициализирован")
# else:
#     print(f"⚠️ Файл {cred_path} не найден. Google OAuth не будет работать.")

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

# ========== Эндпоинт Google OAuth (отключён) ==========
# @app.route('/api/firebase-google-login', methods=['POST'])
# def api_firebase_google_login():
#     """Вход через Google с Firebase (отключено)"""
#     return jsonify({"ok": False, "error": "Google OAuth временно отключён"})

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
            "email": session.get('user_email', 'user@graphitium.com'),
            "name": session.get('user_name', 'Пользователь')
        })
    return jsonify({"ok": False, "error": "Not logged in"})

@app.route('/logout')
def logout():
    """Выход из аккаунта"""
    session.clear()
    return redirect('/')

# ========== AI ГЕНЕРАЦИЯ ==========

from cloud.ai_tools import generate_image

@app.route('/api/ai/generate', methods=['POST'])
def api_ai_generate():
    """Генерация изображения через AI"""
    data = request.get_json()
    prompt = data.get('prompt', '')
    style = data.get('style', 'photo')
    
    if not prompt:
        return jsonify({"ok": False, "error": "Не указан prompt"})
    
    result = generate_image(prompt, style)
    return jsonify(result)

# ========== ГЕНЕРАЦИЯ ФОНОВ ==========

from cloud.ai_tools import generate_solid_background

@app.route('/api/ai/background', methods=['POST'])
def api_ai_background():
    """Генерация однотонного фона"""
    data = request.get_json()
    color = data.get('color', '#85ADFF')
    width = data.get('width', 1024)
    height = data.get('height', 1024)
    
    if not color:
        return jsonify({"ok": False, "error": "Не указан цвет"})
    
    result = generate_solid_background(color, width, height)
    return jsonify(result)

# ========== ШАРИНГ (ОТКРЫТИЕ ПРОЕКТА ПО ССЫЛКЕ) ==========

from cloud.share import get_project_by_share_code

@app.route('/share/<share_code>')
def share_project(share_code):
    """Открыть проект по ссылке (просмотр в браузере)"""
    result = get_project_by_share_code(share_code)
    
    if not result.get("ok"):
        return f"""
        <html>
        <head><title>Graphitium - Ошибка</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px; background: #0a0a0a; color: #fff;">
            <h1>❌ Ошибка</h1>
            <p>{result.get('error', 'Ссылка недействительна')}</p>
            <a href="/" style="color: #85adff;">Вернуться на главную</a>
        </body>
        </html>
        """
    
    project = result.get("project", {})
    can_edit = result.get("can_edit", False)
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Graphitium - Просмотр проекта</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #0a0a0a; color: #fff; padding: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .project-info {{ background: #1a1a2e; padding: 20px; border-radius: 12px; margin-bottom: 20px; }}
            .layers {{ background: #1a1a2e; padding: 20px; border-radius: 12px; }}
            .layer {{ border-bottom: 1px solid #333; padding: 10px 0; }}
            .badge {{ background: #85adff; color: #000; padding: 4px 12px; border-radius: 20px; font-size: 12px; }}
            a {{ color: #85adff; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="project-info">
                <h1>📁 {project.get('name', 'Без названия')}</h1>
                <p>📐 Размер: {project.get('width', 800)} x {project.get('height', 600)}</p>
                <p>📄 Всего слоёв: {len(project.get('layers', []))}</p>
                {"<p>✏️ У вас есть права на редактирование. Откройте проект в приложении Graphitium для внесения изменений.</p>" if can_edit else ""}
            </div>
            <div class="layers">
                <h2>📋 Слои</h2>
                {''.join([f'<div class="layer"><strong>{layer.get("name", "Слой")}</strong> <span class="badge">{layer.get("blend_mode", "normal")}</span> | прозрачность: {layer.get("opacity", 100)}% | позиция: ({layer.get("x", 0)}, {layer.get("y", 0)})</div>' for layer in project.get('layers', [])])}
            </div>
            <p style="margin-top: 20px;"><a href="/">← Вернуться на главную</a></p>
        </div>
    </body>
    </html>
    """

# ========== ИСТОРИЯ ВЕРСИЙ ==========

from cloud.version_history import list_versions, load_version

@app.route('/api/projects/<project_id>/versions', methods=['GET'])
def api_project_versions(project_id):
    """Получить список версий проекта"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        token = session.get('user_token')
    
    if not token:
        return jsonify({"ok": False, "error": "Not authenticated"})
    
    # Проверяем доступ к проекту
    from cloud.cloud_saver import load_project_from_cloud
    project_check = load_project_from_cloud(project_id, token)
    if not project_check.get("ok"):
        return jsonify({"ok": False, "error": "Project not found or access denied"})
    
    result = list_versions(project_id)
    return jsonify(result)

@app.route('/api/projects/<project_id>/versions/<version_id>', methods=['POST'])
def api_restore_version(project_id, version_id):
    """Восстановить проект из версии"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        token = session.get('user_token')
    
    if not token:
        return jsonify({"ok": False, "error": "Not authenticated"})
    
    # Загружаем версию
    version_result = load_version(project_id, version_id)
    if not version_result.get("ok"):
        return jsonify({"ok": False, "error": "Version not found"})
    
    # Сохраняем как новый проект
    from cloud.cloud_saver import save_project_to_cloud
    project_data = version_result.get("project")
    name = version_result.get("version_name", "Restored version")
    
    result = save_project_to_cloud(project_data, token, f"{name} (restored)")
    return jsonify(result)

# ========== ЗАПУСК ==========

if __name__ == '__main__':
    print("🚀 Сервер запущен: http://localhost:5000")
    print("📁 Открой в браузере: http://localhost:5000")
    print("🎨 AI генерация доступна: POST /api/ai/generate")
    print("🔗 Шаринг доступен: GET /share/<code>")
    app.run(host='0.0.0.0', port=5000, debug=True)
