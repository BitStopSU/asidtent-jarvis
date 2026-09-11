"""
JARVIS - Google Integration
Gmail, Drive, Sheets, Docs
"""
import os
import json
import base64
import requests
from datetime import datetime


class GoogleIntegration:
    """Работа с Google сервисами"""

    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.tokens = {}
        self._load_tokens()

    def _load_tokens(self):
        """Загрузка токенов"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            self.tokens = config.get("google_tokens", {})
        except Exception:
            self.tokens = {}

    def _save_tokens(self):
        """Сохранение токенов"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            config["google_tokens"] = self.tokens

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения: {e}")

    def _get_access_token(self):
        """Получить access token"""
        return self.tokens.get("access_token", "")

    def is_authorized(self):
        """Проверка авторизации"""
        return bool(self._get_access_token())

    def get_user_info(self):
        """Информация о пользователе"""
        token = self._get_access_token()
        if not token:
            return None

        try:
            resp = requests.get(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    # ============ GMAIL ============

    def get_emails(self, limit=5):
        """Получить последние письма"""
        token = self._get_access_token()
        if not token:
            return []

        try:
            resp = requests.get(
                "https://gmail.googleapis.com/gmail/v1/users/me/messages",
                headers={"Authorization": f"Bearer {token}"},
                params={"maxResults": limit},
                timeout=10
            )

            if resp.status_code != 200:
                return []

            messages = resp.json().get("messages", [])
            result = []

            for msg in messages:
                msg_id = msg["id"]
                msg_resp = requests.get(
                    f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10
                )

                if msg_resp.status_code == 200:
                    data = msg_resp.json()
                    headers = data.get("payload", {}).get("headers", [])

                    subject = ""
                    sender = ""

                    for h in headers:
                        if h["name"] == "Subject":
                            subject = h["value"]
                        elif h["name"] == "From":
                            sender = h["value"]

                    result.append({
                        "id": msg_id,
                        "subject": subject,
                        "from": sender
                    })

            return result
        except Exception as e:
            print(f"Ошибка Gmail: {e}")
            return []

    def send_email(self, to, subject, body):
        """Отправить письмо"""
        token = self._get_access_token()
        if not token:
            return False

        try:
            message = (
                f"To: {to}\r\n"
                f"Subject: {subject}\r\n\r\n"
                f"{body}"
            )
            raw = base64.urlsafe_b64encode(message.encode()).decode()

            resp = requests.post(
                "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                json={"raw": raw},
                timeout=15
            )

            return resp.status_code == 200
        except Exception as e:
            print(f"Ошибка отправки: {e}")
            return False

    # ============ DRIVE ============

    def list_drive_files(self, limit=10):
        """Список файлов на Drive"""
        token = self._get_access_token()
        if not token:
            return []

        try:
            resp = requests.get(
                "https://www.googleapis.com/drive/v3/files",
                headers={"Authorization": f"Bearer {token}"},
                params={
                    "pageSize": limit,
                    "fields": "files(id,name,mimeType,size)"
                },
                timeout=10
            )

            if resp.status_code == 200:
                return resp.json().get("files", [])
        except Exception:
            pass
        return []

    def upload_to_drive(self, file_path):
        """Загрузить файл на Drive"""
        token = self._get_access_token()
        if not token:
            return None

        if not os.path.exists(file_path):
            return None

        try:
            metadata = {"name": os.path.basename(file_path)}

            with open(file_path, "rb") as f:
                files = {
                    "metadata": (
                        "metadata",
                        json.dumps(metadata),
                        "application/json"
                    ),
                    "file": f
                }

                resp = requests.post(
                    "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
                    headers={"Authorization": f"Bearer {token}"},
                    files=files,
                    timeout=60
                )

            if resp.status_code == 200:
                return resp.json().get("id")
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
        return None

    def download_from_drive(self, file_id, save_path):
        """Скачать файл с Drive"""
        token = self._get_access_token()
        if not token:
            return None

        try:
            resp = requests.get(
                f"https://www.googleapis.com/drive/v3/files/{file_id}",
                headers={"Authorization": f"Bearer {token}"},
                params={"alt": "media"},
                timeout=60
            )

            if resp.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(resp.content)
                return save_path
        except Exception as e:
            print(f"Ошибка скачивания: {e}")
        return None

    # ============ SHEETS ============

    def create_sheet(self, title):
        """Создать Google таблицу"""
        token = self._get_access_token()
        if not token:
            return None

        try:
            resp = requests.post(
                "https://sheets.googleapis.com/v4/spreadsheets",
                headers={"Authorization": f"Bearer {token}"},
                json={"properties": {"title": title}},
                timeout=15
            )

            if resp.status_code == 200:
                data = resp.json()
                return {
                    "id": data.get("spreadsheetId"),
                    "url": data.get("spreadsheetUrl")
                }
        except Exception as e:
            print(f"Ошибка создания таблицы: {e}")
        return None

    def write_to_sheet(self, sheet_id, range_name, data):
        """Записать данные в таблицу"""
        token = self._get_access_token()
        if not token:
            return False

        try:
            resp = requests.put(
                f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/{range_name}",
                headers={"Authorization": f"Bearer {token}"},
                params={"valueInputOption": "USER_ENTERED"},
                json={"values": data},
                timeout=15
            )

            return resp.status_code == 200
        except Exception:
            return False

    def read_sheet(self, sheet_id, range_name="A1:Z100"):
        """Прочитать таблицу"""
        token = self._get_access_token()
        if not token:
            return []

        try:
            resp = requests.get(
                f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/{range_name}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=15
            )

            if resp.status_code == 200:
                return resp.json().get("values", [])
        except Exception:
            pass
        return []

    # ============ DOCS ============

    def create_doc(self, title, content=""):
        """Создать Google документ"""
        token = self._get_access_token()
        if not token:
            return None

        try:
            resp = requests.post(
                "https://docs.googleapis.com/v1/documents",
                headers={"Authorization": f"Bearer {token}"},
                json={"title": title},
                timeout=15
            )

            if resp.status_code != 200:
                return None

            doc_id = resp.json().get("documentId")

            # Добавляем содержимое
            if content:
                requests.post(
                    f"https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate",
                    headers={"Authorization": f"Bearer {token}"},
                    json={
                        "requests": [{
                            "insertText": {
                                "location": {"index": 1},
                                "text": content
                            }
                        }]
                    },
                    timeout=15
                )

            return {
                "id": doc_id,
                "url": f"https://docs.google.com/document/d/{doc_id}"
            }
        except Exception as e:
            print(f"Ошибка создания документа: {e}")
        return None

    # ============ TOKEN MANAGEMENT ============

    def update_tokens(self, new_tokens):
        """Обновить токены"""
        self.tokens.update(new_tokens)
        self._save_tokens()

    def refresh_access_token(self, client_id, client_secret):
        """Обновить access token"""
        refresh = self.tokens.get("refresh_token")
        if not refresh:
            return False

        try:
            resp = requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "refresh_token": refresh,
                    "grant_type": "refresh_token"
                },
                timeout=15
            )

            if resp.status_code == 200:
                data = resp.json()
                self.tokens["access_token"] = data.get("access_token")
                self._save_tokens()
                return True
        except Exception:
            pass
        return False