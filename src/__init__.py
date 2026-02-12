__version__="0.1.0"

from .game import Game
from .patterns import Pattern, PatternType, create_pattern

__all__ = [
    "Game",
    "Pattern",
    "PatternType",
    "create_pattern"
]

