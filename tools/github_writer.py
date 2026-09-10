"""
JARVIS - GitHub Writer
Позволяет JARVIS создавать и изменять файлы на GitHub
"""
import base64
import requests
from loguru import logger

class GitHubWriter:
    def __init__(self, token, username, repo):
        self.token = token
        self.username = username
        self.repo = repo
        self.api = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def get_file(self, path, branch="main"):
        """Получает содержимое файла"""
        url = f"{self.api}/repos/{self.username}/{self.repo}/contents/{path}"
        resp = requests.get(url, headers=self.headers, params={"ref": branch})
        if resp.status_code == 200:
            data = resp.json()
            content = base64.b64decode(data["content"]).decode("utf-8")
            return {"content": content, "sha": data["sha"]}
        return None

    def create_file(self, path, content, message="Create file", branch="main"):
        """Создаёт новый файл"""
        url = f"{self.api}/repos/{self.username}/{self.repo}/contents/{path}"
        
        # Проверяем, существует ли файл
        existing = self.get_file(path, branch)
        
        data = {
            "message": message,
            "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
            "branch": branch
        }
        
        # Если файл существует — добавляем sha для обновления
        if existing:
            data["sha"] = existing["sha"]
            logger.info(f"Обновляю файл: {path}")
        else:
            logger.info(f"Создаю файл: {path}")
        
        resp = requests.put(url, headers=self.headers, json=data)
        
        if resp.status_code in [200, 201]:
            logger.success(f"✅ {path} готов")
            return True
        else:
            logger.error(f"❌ Ошибка {path}: {resp.text[:200]}")
            return False

    def delete_file(self, path, message="Delete file", branch="main"):
        """Удаляет файл"""
        existing = self.get_file(path, branch)
        if not existing:
            return False
        
        url = f"{self.api}/repos/{self.username}/{self.repo}/contents/{path}"
        data = {
            "message": message,
            "sha": existing["sha"],
            "branch": branch
        }
        
        resp = requests.delete(url, headers=self.headers, json=data)
        return resp.status_code == 200

    def create_branch(self, branch_name, from_branch="main"):
        """Создаёт новую ветку"""
        # Получаем sha последнего коммита
        url = f"{self.api}/repos/{self.username}/{self.repo}/git/refs/heads/{from_branch}"
        resp = requests.get(url, headers=self.headers)
        
        if resp.status_code != 200:
            logger.error(f"Не удалось получить ветку {from_branch}")
            return False
        
        sha = resp.json()["object"]["sha"]
        
        # Создаём новую ветку
        url = f"{self.api}/repos/{self.username}/{self.repo}/git/refs"
        data = {
            "ref": f"refs/heads/{branch_name}",
            "sha": sha
        }
        
        resp = requests.post(url, headers=self.headers, json=data)
        
        if resp.status_code == 201:
            logger.success(f"✅ Ветка {branch_name} создана")
            return True
        elif resp.status_code == 422:
            logger.info(f"Ветка {branch_name} уже существует")
            return True
        else:
            logger.error(f"❌ Ошибка: {resp.text[:200]}")
            return False

    def create_many_files(self, files_dict, message="Add files", branch="main"):
        """Создаёт сразу много файлов
        
        files_dict = {
            "path/to/file.py": "содержимое",
            "path/to/other.py": "содержимое"
        }
        """
        results = []
        for path, content in files_dict.items():
            success = self.create_file(path, content, message, branch)
            results.append({"path": path, "success": success})
        return results

    def list_files(self, path="", branch="main"):
        """Список файлов в папке"""
        url = f"{self.api}/repos/{self.username}/{self.repo}/contents/{path}"
        resp = requests.get(url, headers=self.headers, params={"ref": branch})
        
        if resp.status_code == 200:
            return [item["name"] for item in resp.json()]
        return []