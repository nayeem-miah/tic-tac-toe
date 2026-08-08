"""
win_checker.py
--------------
Responsibility:
    Determines whether a given player symbol has achieved a winning
    line on the board.

    Four independent detection methods, each checking one direction:
        - check_rows()          → any complete row of 5
        - check_columns()       → any complete column of 5
        - check_main_diagonal() → top-left → bottom-right diagonal
        - check_anti_diagonal() → top-right → bottom-left diagonal

    One composite method ties them together:
        - check_winner()        → True if ANY of the four checks pass

    Returns True / False only.
    Prints nothing.
    Modifies nothing.
    Depends only on the grid snapshot (list[list[str]]) that Board
    already exposes via get_grid(), so WinChecker never mutates
    the Board's internal state.

    All methods are static — WinChecker carries no instance state.
    Follows Single Responsibility Principle (SRP).
"""

from utils.constants import BOARD_SIZE


class WinChecker:
    """
    Stateless win-condition evaluator for the 5x5 Tic-Tac-Toe board.

    Usage example::

        checker = WinChecker()          # or use WinChecker.check_winner(...)
        if checker.check_winner(board, "X"):
            # handle X winning

    All public methods accept a ``board`` object that exposes
    ``get_grid() -> list[list[str]]``, keeping the checker decoupled
    from Board's internals.
    """

    # ------------------------------------------------------------------
    # Composite check (primary public interface)
    # ------------------------------------------------------------------

    @staticmethod
    def check_winner(board, symbol: str) -> bool:
        """
        Return True if ``symbol`` has achieved a winning line anywhere
        on the board.

        Runs all four directional checks and short-circuits on the
        first success found.

        Args:
            board : A Board instance exposing get_grid().
            symbol: The player symbol to test ("X" or "O").

        Returns:
            True  if the symbol has five in a row/column/diagonal.
            False otherwise.
        """
        grid = board.get_grid()

        return (
            WinChecker.check_rows(grid, symbol)
            or WinChecker.check_columns(grid, symbol)
            or WinChecker.check_main_diagonal(grid, symbol)
            or WinChecker.check_anti_diagonal(grid, symbol)
        )

    # ------------------------------------------------------------------
    # Individual directional checks
    # ------------------------------------------------------------------

    @staticmethod
    def check_rows(grid: list[list[str]], symbol: str) -> bool:
        """
        Return True if ``symbol`` occupies all WIN_LENGTH cells in any
        single row.

        On a 5x5 board with WIN_LENGTH = 5, this means every cell in
        the row must belong to the same player.

        Args:
            grid  : A 2-D list snapshot of the board (5 rows × 5 cols).
            symbol: The player symbol to test.

        Returns:
            True if at least one complete row belongs to symbol.
            False otherwise.

        Example (symbol = "X"):
            Row → ["X", "X", "X", "X", "X"]  →  True
            Row → ["X", "X", "O", "X", "X"]  →  False
        """
        for row in grid:
            if all(cell == symbol for cell in row):
                return True
        return False

    @staticmethod
    def check_columns(grid: list[list[str]], symbol: str) -> bool:
        """
        Return True if ``symbol`` occupies all WIN_LENGTH cells in any
        single column.

        Iterates column-by-column; for each column index checks every
        row at that index.

        Args:
            grid  : A 2-D list snapshot of the board.
            symbol: The player symbol to test.

        Returns:
            True if at least one complete column belongs to symbol.
            False otherwise.

        Example (symbol = "O", column index 2):
            grid[0][2] = "O"
            grid[1][2] = "O"
            grid[2][2] = "O"
            grid[3][2] = "O"
            grid[4][2] = "O"  →  True
        """
        for col in range(BOARD_SIZE):
            if all(grid[row][col] == symbol for row in range(BOARD_SIZE)):
                return True
        return False

    @staticmethod
    def check_main_diagonal(grid: list[list[str]], symbol: str) -> bool:
        """
        Return True if ``symbol`` occupies all cells on the main
        diagonal (top-left → bottom-right).

        On a 5x5 board the main diagonal cells are:
            (0,0), (1,1), (2,2), (3,3), (4,4)

        Because WIN_LENGTH equals BOARD_SIZE, only this single diagonal
        (not shorter sub-diagonals) can constitute a win.

        Args:
            grid  : A 2-D list snapshot of the board.
            symbol: The player symbol to test.

        Returns:
            True if the entire main diagonal belongs to symbol.
            False otherwise.

        Example (symbol = "X"):
            grid[0][0] = grid[1][1] = grid[2][2] = grid[3][3] = grid[4][4] = "X"
            →  True
        """
        return all(grid[i][i] == symbol for i in range(BOARD_SIZE))

    @staticmethod
    def check_anti_diagonal(grid: list[list[str]], symbol: str) -> bool:
        """
        Return True if ``symbol`` occupies all cells on the anti-
        diagonal (top-right → bottom-left).

        On a 5x5 board the anti-diagonal cells are:
            (0,4), (1,3), (2,2), (3,1), (4,0)

        General formula for row i:
            column index = (BOARD_SIZE - 1) - i

        Args:
            grid  : A 2-D list snapshot of the board.
            symbol: The player symbol to test.

        Returns:
            True if the entire anti-diagonal belongs to symbol.
            False otherwise.

        Example (symbol = "O"):
            grid[0][4] = grid[1][3] = grid[2][2] = grid[3][1] = grid[4][0] = "O"
            →  True
        """
        last = BOARD_SIZE - 1
        return all(grid[i][last - i] == symbol for i in range(BOARD_SIZE))
