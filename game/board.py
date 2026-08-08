"""
board.py
--------
Responsibility:
    Manages the 5x5 game grid.

    Owns only board-specific state and behaviour:
        - the internal grid data structure
        - marking a cell
        - validating whether a cell is available
        - resetting itself for a new round
        - displaying itself to the console

    Contains NO player logic, NO timing logic, NO winner detection.
    Winner detection is a separate concern (Step 5).
"""

from utils.constants import BOARD_SIZE, TOTAL_CELLS


class Board:
    """
    Represents and manages the 5x5 Tic-Tac-Toe grid.

    Cells are addressed externally by a 1-based cell number (1-25).
    Internally the grid is stored as a 2-D list of strings.

    Layout example (fresh board):

         1  |  2  |  3  |  4  |  5
        ---------------------------------
         6  |  7  |  8  |  9  | 10
        ---------------------------------
        11  | 12  | 13  | 14  | 15
        ---------------------------------
        16  | 17  | 18  | 19  | 20
        ---------------------------------
        21  | 22  | 23  | 24  | 25
    """

    # Precomputed separator line shared by display and __str__.
    _ROW_SEP: str = "-" * (BOARD_SIZE * 6 - 1)

    def __init__(self) -> None:
        """Initialise a fresh, empty 5x5 board."""
        self._grid: list[list[str]] = []
        self.create_board()

    # ------------------------------------------------------------------
    # Board lifecycle
    # ------------------------------------------------------------------

    def create_board(self) -> None:
        """
        Build the internal 5x5 grid.

        Each cell is initialised to its 1-based cell number as a string
        (e.g. "1", "2", ... "25"), so an unoccupied cell displays its
        own number rather than a generic placeholder.
        """
        self._grid = [
            [str(row * BOARD_SIZE + col + 1) for col in range(BOARD_SIZE)]
            for row in range(BOARD_SIZE)
        ]

    def reset_board(self) -> None:
        """
        Clear the board back to its initial state.

        Equivalent to creating a brand-new board; used between rounds.
        """
        self.create_board()

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def display_board(self) -> None:
        """
        Print the current state of the board to the console.

        Each cell is right-justified to width 3 so single- and
        double-digit numbers align neatly with player symbols.

        Example output (partially played):

             1  |  2  |  X  |  4  |  5
            ---------------------------------
             O  |  7  |  8  |  9  | 10
            ---------------------------------
            11  | 12  | 13  | 14  | 15
            ---------------------------------
            16  | 17  | 18  | 19  | 20
            ---------------------------------
            21  | 22  | 23  | 24  | 25
        """
        for row_index, row in enumerate(self._grid):
            print(self._format_row(row))
            if row_index < BOARD_SIZE - 1:
                print(self._ROW_SEP)

    # ------------------------------------------------------------------
    # Cell access
    # ------------------------------------------------------------------

    def get_cell(self, cell_number: int) -> str:
        """
        Return the current content of a cell.

        Args:
            cell_number: 1-based cell number (1-25).

        Returns:
            The occupying player symbol (e.g. "X", "O"), or the cell's
            own number string (e.g. "7") if the cell is still empty.

        Raises:
            ValueError: If cell_number is outside [1, 25].
        """
        self._validate_cell_number(cell_number)
        row, col = self._cell_to_row_col(cell_number)
        return self._grid[row][col]

    def is_cell_empty(self, cell_number: int) -> bool:
        """
        Return True if the cell has not yet been marked by a player.

        A cell is considered empty when its content equals its own
        cell-number string (as set by create_board).

        Args:
            cell_number: 1-based cell number (1-25).

        Returns:
            True if unoccupied, False if occupied.

        Raises:
            ValueError: If cell_number is outside [1, 25].
        """
        self._validate_cell_number(cell_number)
        return self.get_cell(cell_number) == str(cell_number)

    def update_cell(self, cell_number: int, symbol: str) -> None:
        """
        Place a player's symbol on the specified cell.

        Args:
            cell_number: 1-based cell number (1-25).
            symbol     : The player's symbol ("X" or "O").

        Raises:
            ValueError: If cell_number is outside [1, 25].
            ValueError: If the cell is already occupied.
        """
        self._validate_cell_number(cell_number)

        if not self.is_cell_empty(cell_number):
            raise ValueError(
                f"Cell {cell_number} is already occupied by "
                f"'{self.get_cell(cell_number)}'."
            )

        row, col = self._cell_to_row_col(cell_number)
        self._grid[row][col] = symbol

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _cell_to_row_col(self, cell_number: int) -> tuple[int, int]:
        """
        Convert a 1-based cell number to a (row, col) index pair.

        Args:
            cell_number: 1-based cell number (1-25).

        Returns:
            A (row, col) tuple, both 0-indexed.
        """
        zero_based = cell_number - 1
        row = zero_based // BOARD_SIZE
        col = zero_based % BOARD_SIZE
        return row, col

    def _validate_cell_number(self, cell_number: int) -> None:
        """
        Raise ValueError if cell_number is not in the valid range [1, 25].

        Args:
            cell_number: The number to validate.

        Raises:
            ValueError: If out of range.
        """
        if not isinstance(cell_number, int) or not (1 <= cell_number <= TOTAL_CELLS):
            raise ValueError(
                f"Cell number must be an integer between 1 and {TOTAL_CELLS}, "
                f"got {cell_number!r}."
            )

    @staticmethod
    def _format_row(row: list[str]) -> str:
        """Return a display-ready string for one grid row."""
        return " | ".join(cell.rjust(3) for cell in row)

    # ------------------------------------------------------------------
    # Read-only grid access (for use by other modules, e.g. win checker)
    # ------------------------------------------------------------------

    def get_grid(self) -> list[list[str]]:
        """
        Return a shallow copy of the internal 2-D grid.

        Callers receive a copy so they cannot accidentally mutate the
        board's internal state.

        Returns:
            A 5x5 list-of-lists containing each cell's current string value.
        """
        return [row[:] for row in self._grid]

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """Return a plain-text snapshot of the board (for debugging)."""
        rows: list[str] = []
        for row_index, row in enumerate(self._grid):
            rows.append(self._format_row(row))
            if row_index < BOARD_SIZE - 1:
                rows.append(self._ROW_SEP)
        return "\n".join(rows)

    def __repr__(self) -> str:
        return f"Board(grid={self._grid!r})"
