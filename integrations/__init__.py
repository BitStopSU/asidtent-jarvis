"""
JARVIS Integrations
Внешние сервисы
"""

from .google import GoogleIntegration
from .github import GitHubIntegration
from .telegram import TelegramIntegration

__all__ = [
    "GoogleIntegration",
    "GitHubIntegration",
    "TelegramIntegration",
]