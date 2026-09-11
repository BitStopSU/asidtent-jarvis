"""
JARVIS Core
Главные модули системы
"""

from .server import app
from .nlp import NLPEngine
from .learning import LearningSystem

__version__ = "0.1.0"

__all__ = [
    "app",
    "NLPEngine",
    "LearningSystem",
]