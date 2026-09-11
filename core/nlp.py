"""
JARVIS - NLP Engine
Понимание намерений пользователя
"""
import re


class NLPEngine:
    """Понимает что хочет пользователь"""
    
    def __init__(self):
        # Все возможные намерения
        self.intents = {
            "greeting": [
                "привет", "здравствуй", "добрый день",
                "доброе утро", "добрый вечер", "доброй ночи",
                "хай", "hello", "hi"
            ],
            "time": [
                "время", "который час", "сколько времени",
                "текущее время"
            ],
            "date": [
                "дата", "какое число", "какой сегодня день",
                "сегодняшняя дата"
            ],
            "weather": [
                "погода", "температура на улице",
                "прогноз погоды", "какая погода"
            ],
            "exchange_rate": [
                "курс", "курс доллара", "курс евро",
                "курс валют", "сколько стоит доллар"
            ],
            "email": [
                "почта", "письма", "проверь почту",
                "новые письма", "gmail"
            ],
            "screenshot": [
                "скриншот", "скрин", "сделай снимок",
                "сфотографируй экран"
            ],
            "music": [
                "музык", "песн", "трек", "включи музыку",
                "поставь песню"
            ],
            "youtube": [
                "ютуб", "youtube", "видео",
                "включи видео"
            ],
            "browser": [
                "браузер", "интернет", "открой гугл",
                "открой хром", "chrome"
            ],
            "file_read": [
                "прочитай файл", "читай файл",
                "открой файл", "покажи файл"
            ],
            "file_create": [
                "создай файл", "создать файл",
                "новый файл"
            ],
            "file_write": [
                "запиши", "напиши в файл",
                "сохрани в файл"
            ],
            "file_list": [
                "покажи файлы", "список файлов",
                "какие файлы"
            ],
            "file_delete": [
                "удали файл", "удалить файл"
            ],
            "copy": [
                "копируй", "скопируй", "копировать"
            ],
            "paste": [
                "вставь", "вставить"
            ],
            "cut": [
                "вырежи", "вырезать"
            ],
            "click": [
                "кликни", "клик", "нажми мышью"
            ],
            "press": [
                "нажми", "нажать клавишу"
            ],
            "type": [
                "напиши", "печатай", "введи текст"
            ],
            "cmd": [
                "выполни", "запусти команду",
                "cmd", "консоль", "терминал"
            ],
            "code": [
                "напиши код", "сгенерируй код",
                "создай скрипт", "напиши функцию"
            ],
            "solve": [
                "реши задачу", "сделай сам",
                "автономно", "реши"
            ],
            "ai_change": [
                "смени ии", "выбери ии",
                "используй", "переключи"
            ],
            "help": [
                "помощь", "что ты умеешь",
                "команды", "help"
            ],
            "status": [
                "статус", "состояние",
                "как дела"
            ],
            "exit": [
                "выход", "пока", "отключись",
                "стоп", "выключись"
            ]
        }
    
    def analyze(self, command):
        """
        Определяет намерение команды
        
        Возвращает:
        ├── Тип намерения (greeting, time, ...)
        └── Или "unknown" если не понял
        """
        if not command:
            return "unknown"
        
        command_lower = command.lower().strip()
        
        # 1. Точное совпадение
        for intent, keywords in self.intents.items():
            if command_lower in keywords:
                return intent
        
        # 2. Начинается с ключевого слова
        for intent, keywords in self.intents.items():
            for keyword in keywords:
                if command_lower.startswith(keyword):
                    return intent
        
        # 3. Ключевое слово есть в тексте
        for intent, keywords in self.intents.items():
            for keyword in keywords:
                if keyword in command_lower:
                    return intent
        
        return "unknown"
    
    def extract_parameters(self, command, intent):
        """
        Извлекает параметры из команды
        
        Пример:
        "прочитай файл test.py"
        → {"filename": "test.py"}
        """
        params = {}
        command_lower = command.lower().strip()
        
        if intent == "file_read":
            params["filename"] = (
                command_lower
                .replace("прочитай файл", "")
                .replace("читай файл", "")
                .replace("открой файл", "")
                .replace("покажи файл", "")
                .strip()
            )
        
        elif intent == "file_create":
            params["filename"] = (
                command_lower
                .replace("создай файл", "")
                .replace("создать файл", "")
                .replace("новый файл", "")
                .strip()
            )
        
        elif intent == "file_delete":
            params["filename"] = (
                command_lower
                .replace("удали файл", "")
                .replace("удалить файл", "")
                .strip()
            )
        
        elif intent == "file_write":
            # "запиши привет мир" → text = "привет мир"
            parts = command_lower.split(" ", 1)
            if len(parts) > 1:
                params["text"] = parts[1].strip()
        
        elif intent == "music":
            # "включи музыку Imagine Dragons"
            params["query"] = (
                command_lower
                .replace("включи музыку", "")
                .replace("поставь песню", "")
                .replace("включи песню", "")
                .replace("включи трек", "")
                .strip()
            )
        
        elif intent == "youtube":
            params["query"] = (
                command_lower
                .replace("включи видео", "")
                .replace("ютуб", "")
                .replace("youtube", "")
                .strip()
            )
        
        elif intent == "code":
            params["task"] = (
                command_lower
                .replace("напиши код", "")
                .replace("сгенерируй код", "")
                .replace("создай скрипт", "")
                .replace("напиши функцию", "")
                .strip()
            )
        
        elif intent == "solve":
            params["task"] = (
                command_lower
                .replace("реши задачу", "")
                .replace("сделай сам", "")
                .replace("автономно", "")
                .replace("реши", "")
                .strip()
            )
        
        return params
    
    def validate(self, command, intent):
        """
        Проверяет правильность команды
        """
        # Слишком короткая
        if len(command) < 2:
            return False
        
        # Неизвестное намерение
        if intent == "unknown":
            return False
        
        return True
    
    def get_all_intents(self):
        """Возвращает список всех намерений"""
        return list(self.intents.keys())
    
    def get_examples(self, intent):
        """Возвращает примеры для намерения"""
        return self.intents.get(intent, [])