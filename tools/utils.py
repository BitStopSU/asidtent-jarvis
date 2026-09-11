"""
JARVIS - Utilities
Утилиты: логирование, шифрование, помощники
"""
import os
import json
import logging
from datetime import datetime
from pathlib import Path


# ============ ЛОГИРОВАНИЕ ============

def setup_logger(name="jarvis", log_dir="logs"):
    """Настройка логгера"""
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Файл
    log_file = os.path.join(
        log_dir,
        f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    )
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)

    # Консоль
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


# ============ ШИФРОВАНИЕ ============

def encrypt_text(text, key):
    """Шифрование текста"""
    try:
        from cryptography.fernet import Fernet
        f = Fernet(key)
        return f.encrypt(text.encode()).decode()
    except Exception:
        return None


def decrypt_text(encrypted, key):
    """Расшифровка"""
    try:
        from cryptography.fernet import Fernet
        f = Fernet(key)
        return f.decrypt(encrypted.encode()).decode()
    except Exception:
        return None


def generate_key():
    """Генерация ключа шифрования"""
    try:
        from cryptography.fernet import Fernet
        return Fernet.generate_key().decode()
    except Exception:
        return None


def hash_password(password):
    """Хеширование пароля"""
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()


# ============ ФАЙЛЫ ============

def load_json(path, default=None):
    """Загрузка JSON"""
    if not os.path.exists(path):
        return default if default is not None else {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default if default is not None else {}


def save_json(path, data):
    """Сохранение JSON"""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def human_size(size):
    """Человекочитаемый размер"""
    for unit in ["Б", "КБ", "МБ", "ГБ", "ТБ"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} ПБ"


def ensure_dir(path):
    """Создать папку если нет"""
    os.makedirs(path, exist_ok=True)
    return path


# ============ ВРЕМЯ ============

def now_str():
    """Текущее время в формате строки"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def now_iso():
    """Текущее время в ISO"""
    return datetime.now().isoformat()


def format_time(dt=None):
    """Форматирование времени"""
    if not dt:
        dt = datetime.now()
    return dt.strftime("%H:%M")


def format_date(dt=None):
    """Форматирование даты"""
    if not dt:
        dt = datetime.now()

    months = [
        "января", "февраля", "марта", "апреля",
        "мая", "июня", "июля", "августа",
        "сентября", "октября", "ноября", "декабря"
    ]
    return f"{dt.day} {months[dt.month - 1]} {dt.year} года"


# ============ СЕТЬ ============

def check_internet():
    """Проверка интернета"""
    import socket
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except Exception:
        return False


def check_url(url, timeout=5):
    """Проверка доступности URL"""
    import requests
    try:
        resp = requests.get(url, timeout=timeout)
        return resp.status_code == 200
    except Exception:
        return False


# ============ СИСТЕМА ============

def get_system_info():
    """Информация о системе"""
    import platform
    import psutil

    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "processor": platform.processor(),
        "cpu_cores": psutil.cpu_count(logical=False),
        "cpu_threads": psutil.cpu_count(logical=True),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 1),
        "ram_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent
    }


def get_ip_address():
    """Локальный IP"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


# ============ ТЕКСТ ============

def truncate(text, length=100):
    """Обрезать текст"""
    if not text:
        return ""
    return text[:length] + "..." if len(text) > length else text


def clean_text(text):
    """Очистка текста"""
    if not text:
        return ""
    return " ".join(text.split()).strip()


def extract_numbers(text):
    """Извлечь числа из текста"""
    import re
    return [int(n) for n in re.findall(r'\d+', text)]


# ============ БЕЗОПАСНОСТЬ ============

def is_safe_path(path, base_dir):
    """Проверка что путь внутри базовой папки"""
    try:
        real_path = os.path.realpath(path)
        real_base = os.path.realpath(base_dir)
        return real_path.startswith(real_base)
    except Exception:
        return False


def sanitize_filename(filename):
    """Очистка имени файла"""
    import re
    # Только буквы, цифры, дефис, подчёркивание, точка
    filename = re.sub(r'[^\w\-.]', '_', filename)
    # Не начинается с точки
    filename = filename.lstrip(".")
    return filename or "file"