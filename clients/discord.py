"""
JARVIS - Discord Client
Discord бот с командами и панелью
"""
import discord
from discord.ext import commands
import requests


class DiscordClient:
    """Discord бот JARVIS"""

    def __init__(self, token, server_url="http://localhost:5001"):
        self.token = token
        self.server_url = server_url
        self.bot = commands.Bot(
            command_prefix="!",
            intents=discord.Intents.all()
        )
        self._setup_events()

    def _setup_events(self):
        """Настройка событий и команд"""

        @self.bot.event
        async def on_ready():
            print(f"✅ Бот {self.bot.user} запущен")
            try:
                synced = await self.bot.tree.sync()
                print(f"✅ Синхронизировано: {len(synced)}")
            except Exception as e:
                print(f"Ошибка синхронизации: {e}")

        # ============ СЛЭШ-КОМАНДЫ ============

        @self.bot.tree.command(name="jarvis", description="Команда JARVIS")
        async def jarvis(interaction: discord.Interaction, command: str):
            await interaction.response.defer()
            answer = self._send_to_server(command)
            await interaction.followup.send(f"🤖 {answer}")

        @self.bot.tree.command(name="status", description="Статус серверов")
        async def status(interaction: discord.Interaction):
            await interaction.response.defer()
            try:
                resp = requests.get(
                    f"{self.server_url}/api/status",
                    timeout=5
                )
                if resp.status_code == 200:
                    await interaction.followup.send("✅ JARVIS онлайн")
                else:
                    await interaction.followup.send("⚠️ Проблемы с сервером")
            except Exception:
                await interaction.followup.send("❌ Сервер офлайн")

        @self.bot.tree.command(name="help", description="Все команды")
        async def help_cmd(interaction: discord.Interaction):
            text = (
                "**🤖 Команды JARVIS:**\n\n"
                "`/jarvis привет` — поздороваться\n"
                "`/jarvis время` — текущее время\n"
                "`/jarvis дата` — дата\n"
                "`/jarvis погода` — погода\n"
                "`/jarvis курс` — курс валют\n"
                "`/jarvis почта` — проверить почту\n"
                "`/jarvis скриншот` — скриншот\n"
                "`/jarvis файлы` — список файлов\n"
                "`/jarvis статус` — статус\n\n"
                "`/status` — статус сервера\n"
                "`/help` — эта справка"
            )
            await interaction.response.send_message(text)

        @self.bot.tree.command(name="ai", description="Выбрать ИИ")
        async def ai(interaction: discord.Interaction):
            select = discord.ui.Select(
                placeholder="Выбери ИИ...",
                options=[
                    discord.SelectOption(label="OpenRouter", value="openrouter"),
                    discord.SelectOption(label="DeepSeek", value="deepseek"),
                    discord.SelectOption(label="Gemini", value="gemini"),
                    discord.SelectOption(label="Groq", value="groq"),
                    discord.SelectOption(label="Mistral", value="mistral"),
                ]
            )

            async def callback(inter):
                self._send_to_server(f"смени ии {select.values[0]}")
                await inter.response.send_message(
                    f"✅ ИИ: {select.values[0]}"
                )

            select.callback = callback
            view = discord.ui.View()
            view.add_item(select)
            await interaction.response.send_message("Выбери ИИ:", view=view)

        # ============ КОМАНДЫ С ПРЕФИКСОМ ============

        @self.bot.command(name="jarvis")
        async def jarvis_prefix(ctx, *, command):
            answer = self._send_to_server(command)
            await ctx.send(f"🤖 {answer}")

        @self.bot.command(name="ping")
        async def ping(ctx):
            await ctx.send(f"🏓 Понг! {round(self.bot.latency * 1000)}мс")

    def _send_to_server(self, command):
        """Отправить команду на сервер"""
        try:
            resp = requests.post(
                f"{self.server_url}/api/command",
                json={"command": command},
                timeout=30
            )
            if resp.status_code == 200:
                return resp.json().get("response", "Ошибка")
            return f"Ошибка сервера: {resp.status_code}"
        except Exception as e:
            return f"Сервер недоступен: {e}"

    def run(self):
        """Запуск бота"""
        if not self.token:
            print("❌ Токен Discord не указан")
            return
        self.bot.run(self.token)