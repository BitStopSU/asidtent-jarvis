core/server.py
"""
JARVIS - Главный сервер
Принимает команды и обрабатывает их через ИИ
"""
import os
import sys
import json
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify
from loguru import logger

# Загружаем конфиг
CONFIG_PATH = Path(__file__).parent.parent / "config.json"

def load_config():
    if not CONFIG_PATH.exists():
        logger.error("config.json не найден! Скопируй config.example.json → config.json")
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# Инициализация Flask
app = Flask(__name__)
config = None

@app.route('/')
def index():
    return jsonify({
        "name": "JARVIS",
        "version": "0.1.0",
        "status": "online"
    })

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        "status": "online",
        "time": datetime.now().isoformat()
    })

@app.route('/api/command', methods=['POST'])
def command():
    data = request.json
    cmd = data.get("command", "").lower()
    
    if not cmd:
        return jsonify({"response": "Пустая команда"})
    
    logger.info(f"Команда: {cmd}")
    
    # Простые команды (пока без ИИ)
    if "время" in cmd:
        return jsonify({"response": f"Сейчас {datetime.now().strftime('%H:%M')}"})
    elif "дата" in cmd:
        return jsonify({"response": f"Сегодня {datetime.now().strftime('%d.%m.%Y')}"})
    elif "привет" in cmd:
        return jsonify({"response": f"Привет, {config.get('user_name', 'Пользователь')}!"})
    elif "помощь" in cmd:
        return jsonify({"response": "Доступно: время, дата, привет"})
    else:
        return jsonify({"response": f"Команда не распознана: {cmd}"})

if __name__ == "__main__":
    logger.info("🚀 JARVIS запускается...")
    config = load_config()
    server_config = config.get("server", {})
    host = server_config.get("host", "0.0.0.0")
    port = server_config.get("port", 5001)
    logger.info(f"✅ Сервер на http://{host}:{port}")
    app.run(host=host, port=port)