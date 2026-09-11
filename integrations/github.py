"""
JARVIS - GitHub Integration
Поиск, репозитории, файлы
"""
import os
import base64
import requests


class GitHubIntegration:
    """Работа с GitHub"""

    def __init__(self, token="", username=""):
        self.token = token
        self.username = username
        self.api = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"

    def set_token(self, token, username=""):
        """Установить токен"""
        self.token = token
        self.username = username
        if token:
            self.headers["Authorization"] = f"token {token}"

    def is_authorized(self):
        """Проверка авторизации"""
        return bool(self.token)

    # ============ ПОЛЬЗОВАТЕЛЬ ============

    def get_user(self):
        """Информация о пользователе"""
        if not self.token:
            return None

        try:
            resp = requests.get(
                f"{self.api}/user",
                headers=self.headers,
                timeout=10
            )
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    # ============ ПОИСК ============

    def search_repos(self, query, limit=5):
        """Поиск репозиториев"""
        try:
            resp = requests.get(
                f"{self.api}/search/repositories",
                headers=self.headers,
                params={"q": query, "per_page": limit},
                timeout=10
            )

            if resp.status_code == 200:
                items = resp.json().get("items", [])
                return [{
                    "name": item["full_name"],
                    "url": item["html_url"],
                    "clone_url": item["clone_url"],
                    "description": item.get("description", ""),
                    "stars": item["stargazers_count"],
                    "language": item.get("language", "")
                } for item in items]
        except Exception as e:
            print(f"Ошибка поиска: {e}")
        return []

    def search_code(self, query, limit=5):
        """Поиск кода"""
        if not self.token:
            return []

        try:
            resp = requests.get(
                f"{self.api}/search/code",
                headers=self.headers,
                params={"q": query, "per_page": limit},
                timeout=10
            )

            if resp.status_code == 200:
                items = resp.json().get("items", [])
                return [{
                    "repo": item["repository"]["full_name"],
                    "path": item["path"],
                    "url": item["html_url"]
                } for item in items]
        except Exception:
            pass
        return []

    # ============ РЕПОЗИТОРИИ ============

    def get_repo(self, owner, repo):
        """Информация о репозитории"""
        try:
            resp = requests.get(
                f"{self.api}/repos/{owner}/{repo}",
                headers=self.headers,
                timeout=10
            )
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def get_my_repos(self, limit=30):
        """Мои репозитории"""
        if not self.token:
            return []

        try:
            resp = requests.get(
                f"{self.api}/user/repos",
                headers=self.headers,
                params={"per_page": limit, "sort": "updated"},
                timeout=10
            )

            if resp.status_code == 200:
                return [{
                    "name": r["full_name"],
                    "url": r["html_url"],
                    "private": r["private"],
                    "updated": r["updated_at"]
                } for r in resp.json()]
        except Exception:
            pass
        return []

    def create_repo(self, name, description="", private=False):
        """Создать репозиторий"""
        if not self.token:
            return None

        try:
            resp = requests.post(
                f"{self.api}/user/repos",
                headers=self.headers,
                json={
                    "name": name,
                    "description": description,
                    "private": private,
                    "auto_init": True
                },
                timeout=15
            )

            if resp.status_code == 201:
                return resp.json()
        except Exception as e:
            print(f"Ошибка создания: {e}")
        return None

    def delete_repo(self, owner, repo):
        """Удалить репозиторий"""
        if not self.token:
            return False

        try:
            resp = requests.delete(
                f"{self.api}/repos/{owner}/{repo}",
                headers=self.headers,
                timeout=15
            )
            return resp.status_code == 204
        except Exception:
            return False

    # ============ ФАЙЛЫ ============

    def get_file(self, owner, repo, path, branch="main"):
        """Получить файл"""
        try:
            resp = requests.get(
                f"{self.api}/repos/{owner}/{repo}/contents/{path}",
                headers=self.headers,
                params={"ref": branch},
                timeout=10
            )

            if resp.status_code == 200:
                data = resp.json()
                content = base64.b64decode(data["content"]).decode("utf-8")
                return {
                    "content": content,
                    "sha": data["sha"],
                    "path": data["path"]
                }
        except Exception:
            pass
        return None

    def create_file(self, owner, repo, path, content, message="Create file", branch="main"):
        """Создать или обновить файл"""
        if not self.token:
            return False

        try:
            # Проверяем существует ли
            existing = self.get_file(owner, repo, path, branch)

            data = {
                "message": message,
                "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
                "branch": branch
            }

            if existing:
                data["sha"] = existing["sha"]

            resp = requests.put(
                f"{self.api}/repos/{owner}/{repo}/contents/{path}",
                headers=self.headers,
                json=data,
                timeout=15
            )

            return resp.status_code in [200, 201]
        except Exception as e:
            print(f"Ошибка создания файла: {e}")
        return False

    def delete_file(self, owner, repo, path, message="Delete file", branch="main"):
        """Удалить файл"""
        if not self.token:
            return False

        try:
            existing = self.get_file(owner, repo, path, branch)
            if not existing:
                return False

            resp = requests.delete(
                f"{self.api}/repos/{owner}/{repo}/contents/{path}",
                headers=self.headers,
                json={
                    "message": message,
                    "sha": existing["sha"],
                    "branch": branch
                },
                timeout=15
            )

            return resp.status_code == 200
        except Exception:
            return False

    def list_files(self, owner, repo, path="", branch="main"):
        """Список файлов в папке"""
        try:
            resp = requests.get(
                f"{self.api}/repos/{owner}/{repo}/contents/{path}",
                headers=self.headers,
                params={"ref": branch},
                timeout=10
            )

            if resp.status_code == 200:
                return [{
                    "name": item["name"],
                    "path": item["path"],
                    "type": item["type"],
                    "size": item.get("size", 0)
                } for item in resp.json()]
        except Exception:
            pass
        return []

    # ============ GIST ============

    def create_gist(self, description, content, filename="snippet.txt", public=False):
        """Создать Gist (сниппет)"""
        if not self.token:
            return None

        try:
            resp = requests.post(
                f"{self.api}/gists",
                headers=self.headers,
                json={
                    "description": description,
                    "public": public,
                    "files": {
                        filename: {"content": content}
                    }
                },
                timeout=15
            )

            if resp.status_code == 201:
                return resp.json()
        except Exception:
            pass
        return None

    # ============ CLONE ============

    def clone_repo(self, clone_url, target_dir):
        """Клонировать репозиторий"""
        try:
            if os.path.exists(target_dir):
                return target_dir

            result = subprocess.run(
                ["git", "clone", clone_url, target_dir],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                return target_dir
        except Exception as e:
            print(f"Ошибка клонирования: {e}")
        return None


import subprocess