"""
constants.py
------------
Responsibility:
    Stores all game-wide constants in one place.
    No logic. No classes. Pure configuration values.

    Having a single source of truth for constants makes it trivial
    to translate magic numbers when porting to C / C++.
"""

# Board dimensions
BOARD_SIZE: int = 5           # 5×5 grid
TOTAL_CELLS: int = BOARD_SIZE * BOARD_SIZE  # 25 cells numbered 1-25
WIN_LENGTH: int = 5           # consecutive marks needed to win

# Timing
MOVE_TIME_LIMIT: int = 15     # seconds per move

# Player symbols
SYMBOL_X: str = "X"
SYMBOL_O: str = "O"

# Special-ability limits
MAX_DOUBLE_TURNS: int = 1     # each player may use Double Turn once per match

# Best-of-Three
ROUNDS_TO_WIN: int = 2        # rounds needed to win the match
MAX_ROUNDS: int = 3           # maximum rounds in a match

# Display
EMPTY_CELL: str = "."         # visual placeholder for an unoccupied cell
