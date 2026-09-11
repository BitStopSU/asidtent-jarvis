"""
JARVIS - Raspberry Pi Client
Лёгкий сервер для Pi (24/7)
"""
from flask import Flask, request, jsonify
import requests
import subprocess
import socket
import json
import os
from datetime import datetime


app = Flask(__name__)

# Настройки
MAIN_PC_URL = "http://192.168.0.168:5001/api/command"
PI_LEARNING_FILE = "data/pi_learning.json"


def load_learning():
    """Загрузка статистики Pi"""
    if os.path.exists(PI_LEARNING_FILE):
        try:
            with open(PI_LEARNING_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    return {
        "unknown_commands": [],
        "stats": {"total": 0, "success": 0, "failed": 0}
    }


def save_learning(data):
    """Сохранение статистики"""
    try:
        os.makedirs("data", exist_ok=True)
        with open(PI_LEARNING_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def check_pc():
    """Проверка доступен ли ПК"""
    try:
        resp = requests.get(
            "http://192.168.0.168:5001/api/status",
            timeout=2
        )
        return resp.status_code == 200
    except Exception:
        return False


def wake_on_lan(mac="00-D8-61-37-14-80"):
    """Включить ПК по Wake-on-LAN"""
    try:
        mac = mac.replace("-", "").replace(":", "")
        magic = b"\xff" * 6 + bytes.fromhex(mac) * 16

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(magic, ("255.255.255.255", 9))
        sock.close()

        return "Сигнал отправлен. ПК включается..."
    except Exception as e:
        return f"Ошибка: {e}"


def get_weather():
    """Погода через Open-Meteo"""
    try:
        resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": 53.9,
                "longitude": 27.57,
                "current": "temperature_2m,weather_code"
            },
            timeout=5
        )
        if resp.status_code == 200:
            temp = resp.json()["current"]["temperature_2m"]
            return f"Температура в Минске: {temp}°C"
    except Exception:
        pass
    return "Не удалось получить погоду"


def get_exchange_rate():
    """Курс доллара"""
    try:
        resp = requests.get(
            "https://www.cbr-xml-daily.ru/daily_json.js",
            timeout=5
        )
        if resp.status_code == 200:
            rate = resp.json()["Valute"]["USD"]["Value"]
            return f"Курс доллара: {rate:.2f} ₽"
    except Exception:
        pass
    return "Не удалось получить курс"


def update_pi():
    """Обновить Pi с GitHub"""
    try:
        result = subprocess.run(
            ["git", "-C", "/home/bitstop/jarvis", "pull"],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            return "✅ Pi обновлён. Перезапустите: перезагрузи"
        return f"❌ Ошибка: {result.stderr[:200]}"
    except Exception as e:
        return f"❌ Ошибка: {e}"


def install_package(package):
    """Установить Python-пакет"""
    if not package:
        return "Пакет не указан"

    try:
        result = subprocess.run(
            ["pip3", "install", "--break-system-packages", package],
            capture_output=True,
            text=True,
            timeout=180
        )

        if result.returncode == 0:
            return f"✅ Установлено: {package}"
        return f"❌ Ошибка: {result.stderr[:200]}"
    except Exception as e:
        return f"❌ Ошибка: {e}"


def run_command(cmd):
    """Выполнить команду на Pi"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )

        output = result.stdout.strip() or result.stderr.strip()
        return output[:500] if output else "Выполнено"
    except Exception as e:
        return f"Ошибка: {e}"


def process_locally(cmd):
    """Обработка команды на Pi"""
    cmd_lower = cmd.lower()
    learning = load_learning()
    learning["stats"]["total"] += 1

    # Обновление
    if "обновись" in cmd_lower or "update" in cmd_lower:
        response = update_pi()

    # Установка
    elif "установи" in cmd_lower:
        package = cmd_lower.replace("установи", "").strip()
        response = install_package(package)

    # Wake-on-LAN
    elif "включи пк" in cmd_lower or "разбуди пк" in cmd_lower:
        response = wake_on_lan()

    # Перезагрузка Pi
    elif "перезагрузи" in cmd_lower:
        subprocess.run(["sudo", "reboot"])
        response = "Перезагружаю Pi"

    # Выключение Pi
    elif "выключи pi" in cmd_lower:
        subprocess.run(["sudo", "shutdown", "-h", "now"])
        response = "Выключаю Pi"

    # Время
    elif "время" in cmd_lower:
        response = f"Сейчас {datetime.now().strftime('%H:%M')}"

    # Дата
    elif "дата" in cmd_lower:
        response = f"Сегодня {datetime.now().strftime('%d.%m.%Y')}"

    # Статус
    elif "статус" in cmd_lower:
        response = "Raspberry Pi работает, ПК выключен"

    # Температура Pi
    elif "температура" in cmd_lower:
        try:
            with open("/sys/class/thermal/thermal_zone0/temp") as f:
                temp = int(f.read()) / 1000
            response = f"Температура Pi: {temp:.1f}°C"
        except Exception:
            response = "Не удалось получить температуру"

    # Погода
    elif "погода" in cmd_lower:
        response = get_weather()

    # Курс
    elif "курс" in cmd_lower:
        response = get_exchange_rate()

    # Привет
    elif "привет" in cmd_lower:
        response = "Привет! Работаю на Raspberry Pi."

    # Команда CMD
    elif "выполни" in cmd_lower:
        command = cmd_lower.replace("выполни", "").strip()
        response = run_command(command)

    # Помощь
    elif "помощь" in cmd_lower:
        response = (
            "Доступно: время, дата, статус, температура, "
            "погода, курс, включи пк, обновись, установи, "
            "выполни, перезагрузи"
        )

    else:
        response = "Команда не распознана. Скажите 'помощь'"
        learning["unknown_commands"].append(cmd)
        learning["stats"]["failed"] += 1

    learning["stats"]["success"] += 1
    save_learning(learning)
    return response


# ============ API ============

@app.route("/api/command", methods=["POST"])
def command():
    """Приём команды"""
    data = request.json
    cmd = data.get("command", "")

    # Если ПК доступен — отправляем туда
    if check_pc():
        try:
            resp = requests.post(
                MAIN_PC_URL,
                json={"command": cmd},
                timeout=10
            )
            return jsonify(resp.json())
        except Exception:
            pass

    # Иначе обрабатываем локально
    return jsonify({"response": process_locally(cmd)})


@app.route("/api/status", methods=["GET"])
def status():
    """Статус Pi"""
    return jsonify({
        "status": "online",
        "device": "Raspberry Pi",
        "time": datetime.now().isoformat()
    })


if __name__ == "__main__":
    print("🍓 Pi сервер запущен на порту 5001")
    app.run(host="0.0.0.0", port=5001)