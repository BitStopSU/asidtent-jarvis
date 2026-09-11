"""
JARVIS - AI Router
Умный выбор ИИ под задачу
"""


class AIRouter:
    """Выбирает лучший ИИ для каждой задачи"""

    def __init__(self):
        # Какой ИИ для какой задачи
        self.task_map = {
            "code": "deepseek",
            "debug": "deepseek",
            "math": "deepseek",
            "translation": "gemini",
            "creative": "mistral",
            "analysis": "gemini",
            "chat": "groq",
            "fast": "groq",
            "long": "claude",
            "general": "openrouter"
        }

        # Ключевые слова для определения задачи
        self.keywords = {
            "code": [
                "код", "code", "функция", "скрипт", "программа",
                "python", "javascript", "java", "c++", "html", "css",
                "напиши класс", "напиши функцию", "создай скрипт"
            ],
            "debug": [
                "ошибка", "error", "баг", "bug", "не работает",
                "исправь", "fix", "почему не", "сломалось"
            ],
            "math": [
                "посчитай", "реши", "уравнение", "формула",
                "математик", "вычисли", "сколько будет"
            ],
            "translation": [
                "переведи", "translate", "перевод",
                "на английский", "на русский"
            ],
            "creative": [
                "напиши", "придумай", "расскажи", "история",
                "стих", "поэма", "сказка", "сценарий"
            ],
            "analysis": [
                "проанализируй", "анализ", "сравни", "оцени",
                "статистика", "данные"
            ],
            "fast": [
                "быстро", "срочно", "скорее"
            ],
            "long": [
                "подробно", "большой", "длинный", "статья"
            ]
        }

    def detect_task(self, question):
        """Определить тип задачи"""
        if not question:
            return "general"

        q = question.lower()

        # Проверка ключевых слов
        for task, words in self.keywords.items():
            for word in words:
                if word in q:
                    return task

        return "general"

    def route(self, question):
        """Выбрать провайдера для задачи"""
        task = self.detect_task(question)
        provider = self.task_map.get(task, "openrouter")

        return {
            "task": task,
            "provider": provider
        }

    def ask(self, question, ai_providers):
        """Запрос с авто-выбором ИИ"""
        route = self.route(question)
        provider = route["provider"]

        # Пробуем выбранного
        answer = ai_providers.ask(question, provider)

        # Если не сработал — всех по очереди
        if not answer:
            answer = ai_providers.ask_auto(question)

        return {
            "answer": answer,
            "task": route["task"],
            "provider": provider
        }