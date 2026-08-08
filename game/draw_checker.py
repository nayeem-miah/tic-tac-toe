"""
draw_checker.py
---------------
Responsibility:
    Determines whether a round has ended in a draw.

    A draw requires BOTH conditions to be true simultaneously:
        1. Every cell on the board is occupied (no moves remain).
        2. Neither player has achieved a winning line.

    Condition 1 is checked internally via is_board_full().
    Condition 2 is delegated to WinChecker so win logic is never
    duplicated.

    Returns True / False only.
    Prints nothing.
    Modifies nothing.
    Holds no instance state — all methods are static.

    Follows Single Responsibility Principle (SRP).
"""

from utils.constants import SYMBOL_X, SYMBOL_O
from game.win_checker import WinChecker


class DrawChecker:
    """
    Stateless draw-condition evaluator for the 5x5 Tic-Tac-Toe board.

    Usage example::

        if DrawChecker.is_draw(board):
            # handle draw — no winner, board is full

    The board argument only needs to expose:
        get_grid() -> list[list[str]]
    """

    # ------------------------------------------------------------------
    # Primary (composite) check
    # ------------------------------------------------------------------

    @staticmethod
    def is_draw(board) -> bool:
        """
        Return True if and only if the board is completely full AND
        neither player has a winning line.

        Short-circuits on a win: if either symbol has already won,
        the round is NOT a draw even though the board may be full.

        Args:
            board: A Board instance exposing get_grid().

        Returns:
            True  — all cells occupied and no winner exists.
            False — at least one cell is still empty, OR a winner exists.

        Logic::

            is_draw = is_board_full(board)
                      AND NOT check_winner(board, "X")
                      AND NOT check_winner(board, "O")
        """
        if not DrawChecker.is_board_full(board):
            return False

        # Board is full — check that no symbol has a winning line.
        no_winner = (
            not WinChecker.check_winner(board, SYMBOL_X)
            and not WinChecker.check_winner(board, SYMBOL_O)
        )
        return no_winner

    # ------------------------------------------------------------------
    # Individual condition checks
    # ------------------------------------------------------------------

    @staticmethod
    def is_board_full(board) -> bool:
        """
        Return True if every cell on the board has been occupied by a
        player symbol (i.e. no cell still holds its own number string).

        Detection strategy:
            On creation, each cell stores its own 1-based number as a
            string (e.g. "1", "7", "25").  Once a player marks a cell
            the string becomes "X" or "O".  Therefore a cell is empty
            if and only if its content is a numeric string.

            If ANY cell in the flattened grid is numeric, the board
            still has free space → return False.

        Args:
            board: A Board instance exposing get_grid().

        Returns:
            True  if no cell contains a numeric string (board is full).
            False if at least one cell is still unoccupied.

        Examples::

            # Fresh board — 25 empty cells
            is_board_full(board)  →  False

            # All 25 cells marked — none numeric
            is_board_full(board)  →  True
        """
        grid = board.get_grid()
        return not any(cell.isdigit() for row in grid for cell in row)

    @staticmethod
    def count_empty_cells(board) -> int:
        """
        Return the number of cells that are still unoccupied.

        Useful for the game loop when deciding whether to continue
        or stop checking for draws after each move.

        Args:
            board: A Board instance exposing get_grid().

        Returns:
            Integer count of empty (numeric) cells remaining (0–25).
        """
        grid = board.get_grid()
        return sum(
            1
            for row in grid
            for cell in row
            if cell.isdigit()
        )
