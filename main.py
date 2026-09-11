"""
JARVIS - Main Entry Point
Точка входа в приложение
"""
import os
import sys
import json
from pathlib import Path


# ============ КОНФИГУРАЦИЯ ============

CONFIG_PATH = "config.json"
DEFAULT_CONFIG = "config.example.json"


def load_config():
    """Загрузка конфигурации"""
    if not os.path.exists(CONFIG_PATH):
        print(f"⚠️  {CONFIG_PATH} не найден")
        print(f"📋 Копирую из {DEFAULT_CONFIG}...")

        if os.path.exists(DEFAULT_CONFIG):
            import shutil
            shutil.copy(DEFAULT_CONFIG, CONFIG_PATH)
            print(f"✅ Создан {CONFIG_PATH}")
            print("⚠️  Заполните ключи и перезапустите")
            sys.exit(0)
        else:
            print(f"❌ {DEFAULT_CONFIG} не найден")
            sys.exit(1)

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ============ ПРОВЕРКА ЗАВИСИМОСТЕЙ ============

def check_dependencies():
    """Проверка установленных пакетов"""
    required = [
        "flask",
        "requests",
        "loguru"
    ]

    missing = []
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        print(f"❌ Отсутствуют пакеты: {', '.join(missing)}")
        print(f"📦 Установите: pip install {' '.join(missing)}")
        sys.exit(1)

    print("✅ Все зависимости установлены")


# ============ ЗАПУСК МОДУЛЕЙ ============

def start_server(config):
    """Запуск главного сервера"""
    print("🚀 Запуск JARVIS сервера...")

    from core.server import app
    from core.nlp import NLPEngine
    from core.learning import LearningSystem

    # Инициализация
    nlp = NLPEngine()
    learning = LearningSystem()

    # Сервер запускается через app.run в core/server.py
    host = config.get("server", {}).get("host", "0.0.0.0")
    port = config.get("server", {}).get("port", 5001)

    print(f"✅ Сервер: http://{host}:{port}")

    app.run(host=host, port=port)


def start_discord(config):
    """Запуск Discord бота"""
    token = config.get("discord", {}).get("token", "")

    if not token or token == "ВСТАВЬ_ТОКЕН_DISCORD":
        print("⚠️  Discord токен не указан. Пропускаю.")
        return

    print("💬 Запуск Discord бота...")

    from clients.discord import DiscordClient

    server_url = f"http://localhost:{config.get('server', {}).get('port', 5001)}"
    bot = DiscordClient(token, server_url)
    bot.run()


def start_web(config):
    """Запуск веб-интерфейса"""
    enabled = config.get("features", {}).get("web_interface", True)

    if not enabled:
        print("⚠️  Веб-интерфейс отключён")
        return

    print("🌐 Запуск веб-интерфейса...")

    from clients.web import run
    run(port=3000)


# ============ МЕНЮ ЗАПУСКА ============

def show_menu():
    """Меню выбора режима"""
    print("""
╔══════════════════════════════════════╗
║         ⚡ JARVIS v0.1.0             ║
╠══════════════════════════════════════╣
║  Что запустить?                      ║
║                                      ║
║  1. Всё сразу (сервер + бот + веб)   ║
║  2. Только сервер                    ║
║  3. Только Discord бот               ║
║  4. Только веб-интерфейс             ║
║  5. Проверка системы                 ║
║  0. Выход                            ║
║                                      ║
╚══════════════════════════════════════╝
    """)

    choice = input("Выбор: ").strip()
    return choice


def run_all(config):
    """Запустить всё"""
    import threading

    # Сервер в основном потоке
    web_thread = threading.Thread(
        target=start_web,
        args=(config,),
        daemon=True
    )
    web_thread.start()

    discord_thread = threading.Thread(
        target=start_discord,
        args=(config,),
        daemon=True
    )
    discord_thread.start()

    # Сервер в конце (блокирующий)
    start_server(config)


def check_system(config):
    """Проверка системы"""
    print("\n📊 ПРОВЕРКА СИСТЕМЫ\n")

    # Python
    print(f"✅ Python: {sys.version.split()[0]}")

    # Система
    from tools.utils import get_system_info, get_ip_address
    info = get_system_info()

    print(f"✅ ОС: {info['os']}")
    print(f"✅ CPU: {info['cpu_cores']} ядер / {info['cpu_threads']} потоков")
    print(f"✅ RAM: {info['ram_total_gb']} ГБ (занято {info['ram_percent']}%)")
    print(f"✅ Диск: занято {info['disk_percent']}%")
    print(f"✅ IP: {get_ip_address()}")

    # Интернет
    from tools.utils import check_internet
    if check_internet():
        print("✅ Интернет: есть")
    else:
        print("❌ Интернет: нет")

    # Конфигурация
    print(f"\n⚙️  КОНФИГУРАЦИЯ:")
    print(f"   Имя: {config.get('user_name', 'Не указано')}")
    print(f"   Язык: {config.get('language', 'ru')}")
    print(f"   Порт: {config.get('server', {}).get('port', 5001)}")

    # ИИ-ключи
    print(f"\n🤖 ИИ-ПРОВАЙДЕРЫ:")
    ai = config.get("ai", {}).get("providers", {})

    for name, provider in ai.items():
        key = provider.get("api_key", "")
        status = "✅" if key and "ВСТАВЬ" not in key else "❌"
        print(f"   {status} {name.capitalize()}")

    # Аккаунты
    print(f"\n🔗 АККАУНТЫ:")
    print(f"   Google: {'✅' if config.get('google_tokens') else '❌'}")
    print(f"   GitHub: {'✅' if config.get('github', {}).get('token') else '❌'}")
    print(f"   Telegram: {'✅' if config.get('telegram', {}).get('bot_token') else '❌'}")
    print(f"   Discord: {'✅' if config.get('discord', {}).get('token') else '❌'}")

    print("\n" + "=" * 40)
    input("Нажмите Enter для продолжения...")


# ============ ГЛАВНАЯ ============

def main():
    """Точка входа"""
    print("""
    ⚡ JARVIS
    Персональный ИИ-ассистент
    """)

    # Проверка зависимостей
    check_dependencies()

    # Загрузка конфига
    config = load_config()
    print("✅ Конфигурация загружена\n")

    # Меню
    while True:
        choice = show_menu()

        if choice == "1":
            run_all(config)
            break
        elif choice == "2":
            start_server(config)
            break
        elif choice == "3":
            start_discord(config)
            break
        elif choice == "4":
            start_web(config)
            break
        elif choice == "5":
            check_system(config)
        elif choice == "0":
            print("👋 До свидания!")
            break
        else:
            print("❌ Неверный выбор")
            continue


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Прервано пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")