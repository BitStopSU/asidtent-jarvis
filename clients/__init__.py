"""
JARVIS Clients
Все клиенты: Discord, Pi, Web
"""

from .discord import DiscordClient
from .pi import app as pi_app
from .web import app as web_app

__all__ = [
    "DiscordClient",
    "pi_app",
    "web_app",
]