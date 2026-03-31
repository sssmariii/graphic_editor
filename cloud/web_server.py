from flask import Flask, send_from_directory, jsonify, request
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cloud.auth.auth import login, register
from cloud.cloud_saver import list_user_projects, load_project_from_cloud
from cloud.cloud_manager import delete_project_from_cloud

app = Flask(__name__, static_folder='../web')

# ========== СТРАНИЦЫ ==========

@app.route('/')
def index():
    """Главная страница — Мои проекты"""
    return send_from_directory('../web', 'projects.html')

# ========== API ДЛЯ ВЕБ-СТРАНИЦЫ ==========

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    result = login(data.get('email'), data.get('password'))
    return jsonify(result)

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    result = register(data.get('email'), data.get('password'))
    return jsonify(result)

@app.route('/api/projects', methods=['GET'])
def api_projects():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    result = list_user_projects(token)
    return jsonify(result)

@app.route('/api/projects/<project_id>', methods=['DELETE'])
def api_delete_project(project_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    result = delete_project_from_cloud(project_id, token)
    return jsonify(result)

if __name__ == '__main__':
    print("🚀 Сервер запущен: http://localhost:5000")
    print("📁 Открой в браузере: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)