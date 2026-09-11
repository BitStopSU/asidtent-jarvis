"""
JARVIS - Autonomous Agent
Автономное решение задач
"""
import os
import json
import subprocess
from datetime import datetime


class Autonomous:
    """Автономный агент с самопроверкой"""

    def __init__(self, ai_providers, max_iterations=5):
        self.ai = ai_providers
        self.max_iterations = max_iterations
        self.memory_file = "data/autonomous_memory.json"
        self.memory = self._load_memory()

    def _load_memory(self):
        """Загрузка памяти"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"tasks": []}

    def _save_memory(self):
        """Сохранение памяти"""
        try:
            os.makedirs("data", exist_ok=True)
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # ============ ПЛАНИРОВАНИЕ ============

    def plan(self, task):
        """Разбить задачу на шаги"""
        prompt = (
            "Разбей задачу на 3-5 конкретных шагов. "
            "Отвечай ТОЛЬКО списком, каждый шаг с новой строки, "
            "БЕЗ нумерации и дефисов.\n\n"
            "Задача: " + task
        )

        response = self.ai.ask_auto(prompt)

        if not response or response.strip().lower() == task.lower():
            return [task]

        steps = []
        for line in response.split("\n"):
            line = line.strip()
            # Убираем нумерацию
            line = line.lstrip("0123456789.-) ")
            if line and len(line) > 3 and line.lower() != task.lower():
                steps.append(line)

        return steps[:5] if steps else [task]

    # ============ САМОПРОВЕРКА ============

    def verify(self, answer):
        """Проверить ответ"""
        questions = [
            "Это правильно? Ответь ДА или НЕТ.",
            "Это безопасно? Ответь ДА или НЕТ.",
            "Есть ли ошибки? Ответь ДА или НЕТ."
        ]

        for q in questions:
            prompt = q + "\n\nЧто проверить:\n" + answer[:2000]
            result = self.ai.ask_auto(prompt)

            if result and "нет" in result.lower():
                return False, q

        return True, None

    def improve(self, answer, issue):
        """Улучшить ответ"""
        prompt = (
            "Улучши этот ответ с учётом проблемы.\n\n"
            "Проблема: " + issue + "\n\n"
            "Ответ:\n" + answer
        )
        return self.ai.ask_auto(prompt)

    # ============ ВЫПОЛНЕНИЕ ============

    def execute_step(self, step):
        """Выполнить один шаг"""
        # Установка пакета
        if "установи" in step.lower() or "install" in step.lower():
            package = (
                step.lower()
                .replace("установи", "")
                .replace("install", "")
                .strip()
            )
            return self._install_package(package)

        # Поиск в интернете
        if "найди" in step.lower() or "поиск" in step.lower():
            return "Поиск: " + step

        # Генерация кода
        return self.ai.ask_auto(step)

    def _install_package(self, package):
        """Установка Python пакета"""
        if not package:
            return "Пакет не указан"

        try:
            result = subprocess.run(
                ["pip", "install", package],
                capture_output=True, text=True, timeout=120
            )
            if result.returncode == 0:
                return f"✅ Установлено: {package}"
            return f"❌ Ошибка: {result.stderr[:200]}"
        except Exception as e:
            return f"❌ Ошибка: {e}"

    # ============ ГЛАВНЫЙ ЦИКЛ ============

    def solve(self, task):
        """Полное решение задачи с самопроверкой"""
        result = {
            "task": task,
            "steps": [],
            "iterations": 0,
            "final_answer": None,
            "thoughts": []
        }

        # 1. Планирование
        steps = self.plan(task)
        result["steps"] = steps
        result["thoughts"].append({
            "stage": "plan",
            "steps": steps
        })

        # 2. Выполнение шагов
        answers = []
        for step in steps:
            step_result = self.execute_step(step)
            answers.append({
                "step": step,
                "result": step_result
            })

        # 3. Сборка ответа
        answer = "\n".join(
            a["result"] for a in answers if a["result"]
        )

        # 4. Самопроверка (5 итераций)
        for i in range(self.max_iterations):
            result["iterations"] = i + 1

            is_ok, issue = self.verify(answer)
            result["thoughts"].append({
                "iteration": i + 1,
                "answer_preview": answer[:200],
                "is_ok": is_ok,
                "issue": issue
            })

            if is_ok:
                break

            answer = self.improve(answer, issue)

        result["final_answer"] = answer

        # 5. Сохранение в память
        self.memory["tasks"].append({
            "task": task,
            "steps": steps,
            "completed": True,
            "time": datetime.now().isoformat()
        })
        self._save_memory()

        return result

    def get_stats(self):
        """Статистика решённых задач"""
        return {
            "total": len(self.memory["tasks"]),
            "recent": self.memory["tasks"][-5:]
        }