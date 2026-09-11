"""
JARVIS - Telegram Integration
Уведомления, файлы, облако
"""
import os
import requests


class TelegramIntegration:
    """Работа с Telegram"""

    def __init__(self, bot_token="", chat_id=""):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api = f"https://api.telegram.org/bot{bot_token}"

    def set_bot(self, bot_token, chat_id=""):
        """Установить бота"""
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api = f"https://api.telegram.org/bot{bot_token}"

    def is_authorized(self):
        """Проверка"""
        return bool(self.bot_token)

    # ============ СООБЩЕНИЯ ============

    def send_message(self, text, chat_id=None):
        """Отправить сообщение"""
        if not self.bot_token:
            return False

        chat = chat_id or self.chat_id
        if not chat:
            return False

        try:
            resp = requests.post(
                f"{self.api}/sendMessage",
                json={
                    "chat_id": chat,
                    "text": text,
                    "parse_mode": "HTML"
                },
                timeout=10
            )
            return resp.status_code == 200
        except Exception as e:
            print(f"Ошибка Telegram: {e}")
            return False

    def send_notification(self, title, message):
        """Красивое уведомление"""
        text = f"<b>{title}</b>\n\n{message}"
        return self.send_message(text)

    # ============ ФАЙЛЫ ============

    def send_document(self, file_path, caption="", chat_id=None):
        """Отправить файл"""
        if not self.bot_token:
            return None

        chat = chat_id or self.chat_id
        if not chat or not os.path.exists(file_path):
            return None

        # Проверка размера (Bot API: до 50 МБ)
        size = os.path.getsize(file_path)
        if size > 50 * 1024 * 1024:
            return {"error": "Файл больше 50 МБ"}

        try:
            with open(file_path, "rb") as f:
                resp = requests.post(
                    f"{self.api}/sendDocument",
                    data={
                        "chat_id": chat,
                        "caption": caption
                    },
                    files={"document": f},
                    timeout=120
                )

            if resp.status_code == 200:
                result = resp.json()
                return {
                    "file_id": result["result"]["document"]["file_id"],
                    "name": os.path.basename(file_path),
                    "size": size
                }
        except Exception as e:
            print(f"Ошибка отправки файла: {e}")
        return None

    def send_photo(self, photo_path, caption="", chat_id=None):
        """Отправить фото"""
        if not self.bot_token:
            return None

        chat = chat_id or self.chat_id
        if not chat or not os.path.exists(photo_path):
            return None

        try:
            with open(photo_path, "rb") as f:
                resp = requests.post(
                    f"{self.api}/sendPhoto",
                    data={"chat_id": chat, "caption": caption},
                    files={"photo": f},
                    timeout=60
                )

            if resp.status_code == 200:
                return resp.json()["result"]["photo"][-1]["file_id"]
        except Exception as e:
            print(f"Ошибка фото: {e}")
        return None

    def get_file(self, file_id):
        """Получить путь к файлу"""
        if not self.bot_token:
            return None

        try:
            resp = requests.get(
                f"{self.api}/getFile",
                params={"file_id": file_id},
                timeout=10
            )

            if resp.status_code == 200:
                return resp.json()["result"]["file_path"]
        except Exception:
            pass
        return None

    def download_file(self, file_id, save_path):
        """Скачать файл"""
        if not self.bot_token:
            return None

        file_path = self.get_file(file_id)
        if not file_path:
            return None

        try:
            url = f"https://api.telegram.org/file/bot{self.bot_token}/{file_path}"
            resp = requests.get(url, timeout=120)

            if resp.status_code == 200:
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                with open(save_path, "wb") as f:
                    f.write(resp.content)
                return save_path
        except Exception as e:
            print(f"Ошибка скачивания: {e}")
        return None

    # ============ ПОЛУЧЕНИЕ ОБНОВЛЕНИЙ ============

    def get_updates(self, offset=0):
        """Получить обновления (команды от юзера)"""
        if not self.bot_token:
            return []

        try:
            resp = requests.get(
                f"{self.api}/getUpdates",
                params={"offset": offset, "timeout": 5},
                timeout=10
            )

            if resp.status_code == 200:
                return resp.json().get("result", [])
        except Exception:
            pass
        return []

    def get_me(self):
        """Информация о боте"""
        if not self.bot_token:
            return None

        try:
            resp = requests.get(f"{self.api}/getMe", timeout=10)
            if resp.status_code == 200:
                return resp.json()["result"]
        except Exception:
            pass
        return None

    # ============ ОБЛАКО ============

    def upload_to_cloud(self, file_path, category="files"):
        """Загрузить файл как в облако"""
        caption = f"[{category}] {os.path.basename(file_path)}"
        return self.send_document(file_path, caption)

    def download_from_cloud(self, file_id, save_path):
        """Скачать из облака"""
        return self.download_file(file_id, save_path)