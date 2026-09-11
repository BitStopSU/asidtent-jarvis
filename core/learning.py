"""
JARVIS - Learning System
Самообучение на основе команд пользователя
"""
import os
import json
from datetime import datetime


class LearningSystem:
    """Система самообучения"""

    def __init__(self, db_path="data/learning.json"):
        self.db_path = db_path
        self.data = self._load()

    def _load(self):
        """Загрузка данных обучения"""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        # Начальные данные
        return {
            "unknown_commands": [],
            "learned_commands": {},
            "statistics": {
                "total_commands": 0,
                "successful": 0,
                "failed": 0,
                "started_at": datetime.now().isoformat()
            }
        }

    def _save(self):
        """Сохранение данных"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False

    # ============ НЕИЗВЕСТНЫЕ КОМАНДЫ ============

    def log_unknown_command(self, command):
        """Записать непонятую команду"""
        self.data["unknown_commands"].append({
            "command": command,
            "timestamp": datetime.now().isoformat(),
            "count": 1
        })

        # Ограничение: храним последние 1000
        if len(self.data["unknown_commands"]) > 1000:
            self.data["unknown_commands"] = self.data["unknown_commands"][-1000:]

        self.data["statistics"]["failed"] += 1
        self.data["statistics"]["total_commands"] += 1
        self._save()

    def get_unknown_commands(self, limit=50):
        """Получить список непонятых команд"""
        return self.data["unknown_commands"][-limit:]

    def get_top_unknown(self, limit=10):
        """Топ непонятых команд (по частоте)"""
        # Подсчёт частоты
        counter = {}
        for item in self.data["unknown_commands"]:
            cmd = item["command"]
            counter[cmd] = counter.get(cmd, 0) + 1

        # Сортировка
        sorted_cmds = sorted(
            counter.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            {"command": cmd, "count": count}
            for cmd, count in sorted_cmds[:limit]
        ]

    def clear_unknown_commands(self):
        """Очистить список непонятых"""
        count = len(self.data["unknown_commands"])
        self.data["unknown_commands"] = []
        self._save()
        return count

    # ============ ИЗУЧЕННЫЕ КОМАНДЫ ============

    def learn_command(self, user_command, action):
        """Обучить новой команде"""
        self.data["learned_commands"][user_command] = {
            "action": action,
            "learned_at": datetime.now().isoformat(),
            "uses": 0
        }
        self._save()
        return True

    def get_learned_command(self, user_command):
        """Получить действие для команды"""
        if user_command in self.data["learned_commands"]:
            cmd = self.data["learned_commands"][user_command]
            cmd["uses"] = cmd.get("uses", 0) + 1
            self._save()
            return cmd["action"]
        return None

    def get_all_learned(self):
        """Список всех изученных команд"""
        return self.data["learned_commands"]

    def forget_command(self, user_command):
        """Забыть команду"""
        if user_command in self.data["learned_commands"]:
            del self.data["learned_commands"][user_command]
            self._save()
            return True
        return False

    # ============ СТАТИСТИКА ============

    def log_success(self, command=None):
        """Записать успешную команду"""
        self.data["statistics"]["successful"] += 1
        self.data["statistics"]["total_commands"] += 1
        self._save()

    def get_statistics(self):
        """Получить статистику"""
        stats = self.data["statistics"].copy()

        # Добавляем дополнительно
        stats["unknown_count"] = len(self.data["unknown_commands"])
        stats["learned_count"] = len(self.data["learned_commands"])

        # Успешность
        total = stats.get("total_commands", 0)
        if total > 0:
            success_rate = stats["successful"] / total * 100
            stats["success_rate"] = round(success_rate, 1)
        else:
            stats["success_rate"] = 0

        return stats

    def reset_statistics(self):
        """Сбросить статистику"""
        self.data["statistics"] = {
            "total_commands": 0,
            "successful": 0,
            "failed": 0,
            "started_at": datetime.now().isoformat()
        }
        self._save()
        return True

    # ============ АНАЛИЗ ============

    def analyze_unknown(self):
        """Анализ непонятых команд"""
        top = self.get_top_unknown(20)

        if not top:
            return {
                "message": "Нет непонятых команд",
                "suggestions": []
            }

        # Группировка по ключевым словам
        suggestions = []
        for item in top:
            cmd = item["command"]
            count = item["count"]

            suggestions.append({
                "command": cmd,
                "times": count,
                "suggestion": f"Добавить команду '{cmd}' в NLP"
            })

        return {
            "message": f"Найдено {len(self.data['unknown_commands'])} непонятых команд",
            "top": top,
            "suggestions": suggestions
        }

    def export_data(self):
        """Экспорт всех данных"""
        return {
            "exported_at": datetime.now().isoformat(),
            "data": self.data
        }

    def import_data(self, imported):
        """Импорт данных"""
        if "data" in imported:
            self.data = imported["data"]
            self._save()
            return True
        return False