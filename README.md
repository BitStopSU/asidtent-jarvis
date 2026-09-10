# asidtent-jarvis
Personal AI assistant with web interface, multi-AI support, and integrations
# ⚡ JARVIS — Персональный ИИ-ассистент

> Умный ассистент с веб-интерфейсом, поддержкой нескольких ИИ и интеграциями с сервисами.

## 🎯 Возможности

- 🤖 **Мульти-ИИ**: OpenRouter, DeepSeek, Gemini, Groq, Mistral
- 💬 **Чат** через веб-сайт и Discord
- 📁 **Работа с файлами**: загрузка, чтение, скачивание, OCR
- 📊 **Google**: Gmail, Drive, Sheets, Docs
- 💻 **GitHub**: поиск, клонирование, установка
- 📱 **Telegram**: уведомления и команды
- 🎵 **Медиа**: VK, Yandex, YouTube
- 🎮 **Игры**: Steam, Dota 2
- 🏠 **Умный дом**: Yandex Smart Home
- 🧠 **Автономность**: самообучение и генерация кода

## 📦 Установка

```bash
git clone https://github.com/BitStopSU/asidtent-jarvis.git
cd asidtent-jarvis
pip install -r requirements.txt
cp config.example.json config.json
# Вставь ключи в config.json
python core/server.py