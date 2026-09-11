"""
JARVIS - AI Providers
Все ИИ-провайдеры в одном месте
"""
import requests


class AIProviders:
    """Работа со всеми ИИ через один интерфейс"""

    def __init__(self):
        self.providers = {
            "openrouter": {
                "url": "https://openrouter.ai/api/v1/chat/completions",
                "model": "openrouter/auto",
                "key": "",
                "type": "openai"
            },
            "deepseek": {
                "url": "https://api.deepseek.com/v1/chat/completions",
                "model": "deepseek-chat",
                "key": "",
                "type": "openai"
            },
            "gemini": {
                "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
                "model": "gemini-2.0-flash",
                "key": "",
                "type": "gemini"
            },
            "groq": {
                "url": "https://api.groq.com/openai/v1/chat/completions",
                "model": "llama3-8b-8192",
                "key": "",
                "type": "openai"
            },
            "mistral": {
                "url": "https://api.mistral.ai/v1/chat/completions",
                "model": "mistral-small-latest",
                "key": "",
                "type": "openai"
            },
            "openai": {
                "url": "https://api.openai.com/v1/chat/completions",
                "model": "gpt-4o-mini",
                "key": "",
                "type": "openai"
            },
            "claude": {
                "url": "https://api.anthropic.com/v1/messages",
                "model": "claude-3-haiku-20240307",
                "key": "",
                "type": "claude"
            }
        }
        self.current_provider = "openrouter"

    def set_keys(self, keys):
        """Установить API ключи"""
        for provider, key in keys.items():
            if provider in self.providers:
                self.providers[provider]["key"] = key

    def set_provider(self, provider):
        """Выбрать активный провайдер"""
        if provider in self.providers:
            self.current_provider = provider
            return True
        return False

    def ask(self, question, provider=None):
        """Запрос к ИИ"""
        provider = provider or self.current_provider

        if provider not in self.providers:
            return None

        p = self.providers[provider]

        if not p["key"]:
            return None

        try:
            if p["type"] == "gemini":
                return self._ask_gemini(question, p)
            elif p["type"] == "claude":
                return self._ask_claude(question, p)
            else:
                return self._ask_openai(question, p)

        except Exception as e:
            print(f"Ошибка {provider}: {e}")
            return None

    def ask_auto(self, question):
        """Пробует всех провайдеров по очереди"""
        # Сначала текущий
        answer = self.ask(question)
        if answer:
            return answer

        # Потом остальные
        for provider in self.providers:
            if provider != self.current_provider:
                answer = self.ask(question, provider)
                if answer:
                    return answer

        return "Все ИИ недоступны"

    def _ask_openai(self, question, p):
        """OpenAI-совместимый запрос"""
        headers = {
            "Authorization": f"Bearer {p['key']}",
            "Content-Type": "application/json"
        }
        data = {
            "model": p["model"],
            "messages": [{"role": "user", "content": question}]
        }
        resp = requests.post(p["url"], headers=headers, json=data, timeout=60)

        if resp.status_code == 200:
            result = resp.json()
            if "choices" in result:
                return result["choices"][0]["message"]["content"].strip()
        return None

    def _ask_gemini(self, question, p):
        """Google Gemini"""
        url = f"{p['url']}?key={p['key']}"
        data = {
            "contents": [{"parts": [{"text": question}]}]
        }
        resp = requests.post(url, json=data, timeout=60)

        if resp.status_code == 200:
            result = resp.json()
            if "candidates" in result:
                return result["candidates"][0]["content"]["parts"][0]["text"].strip()
        return None

    def _ask_claude(self, question, p):
        """Anthropic Claude"""
        headers = {
            "x-api-key": p["key"],
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        data = {
            "model": p["model"],
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": question}]
        }
        resp = requests.post(p["url"], headers=headers, json=data, timeout=60)

        if resp.status_code == 200:
            result = resp.json()
            if "content" in result:
                return result["content"][0]["text"].strip()
        return None

    def get_available(self):
        """Список доступных провайдеров (с ключами)"""
        return [
            name for name, p in self.providers.items()
            if p["key"]
        ]

    def get_all(self):
        """Список всех провайдеров"""
        return list(self.providers.keys())