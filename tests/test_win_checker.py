"""
test_win_checker.py
-------------------
Unit tests for game.win_checker.WinChecker.

Covers:
    - No winner on a fresh / partially-filled board
    - All 5 rows (one test per row)
    - All 5 columns (one test per column)
    - Main diagonal (top-left → bottom-right)
    - Anti-diagonal (top-right → bottom-left)
    - Symbol specificity (O win is not a win for X and vice-versa)
    - Partial lines do NOT trigger a win
"""

import unittest

from game.board import Board
from game.win_checker import WinChecker
from utils.constants import SYMBOL_X, SYMBOL_O


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _mark_cells(board: Board, cells: list[int], symbol: str) -> None:
    """Mark multiple cells with *symbol* on *board*."""
    for cell in cells:
        board.update_cell(cell, symbol)


# ---------------------------------------------------------------------------
# Test classes
# ---------------------------------------------------------------------------

class TestWinCheckerNoWinner(unittest.TestCase):
    """WinChecker must return False when no winning line exists."""

    def setUp(self) -> None:
        self.board = Board()

    def test_fresh_board_x_no_win(self) -> None:
        self.assertFalse(WinChecker.check_winner(self.board, SYMBOL_X))

    def test_fresh_board_o_no_win(self) -> None:
        self.assertFalse(WinChecker.check_winner(self.board, SYMBOL_O))

    def test_four_in_a_row_is_not_a_win(self) -> None:
        """Four consecutive marks should NOT constitute a win."""
        _mark_cells(self.board, [1, 2, 3, 4], SYMBOL_X)
        self.assertFalse(WinChecker.check_winner(self.board, SYMBOL_X))

    def test_four_in_a_column_is_not_a_win(self) -> None:
        _mark_cells(self.board, [1, 6, 11, 16], SYMBOL_X)
        self.assertFalse(WinChecker.check_winner(self.board, SYMBOL_X))

    def test_mixed_row_is_not_a_win(self) -> None:
        """A row with both symbols must not trigger a win."""
        _mark_cells(self.board, [1, 2, 3, 4], SYMBOL_X)
        _mark_cells(self.board, [5], SYMBOL_O)
        self.assertFalse(WinChecker.check_winner(self.board, SYMBOL_X))
        self.assertFalse(WinChecker.check_winner(self.board, SYMBOL_O))


class TestWinCheckerRows(unittest.TestCase):
    """WinChecker must detect a complete row of 5 for either symbol."""

    def setUp(self) -> None:
        self.board = Board()

    def _row_cells(self, row_index: int) -> list[int]:
        """Return the five 1-based cell numbers for a given 0-indexed row."""
        start = row_index * 5 + 1
        return list(range(start, start + 5))

    def test_row_0_x_wins(self) -> None:
        _mark_cells(self.board, self._row_cells(0), SYMBOL_X)
        self.assertTrue(WinChecker.check_winner(self.board, SYMBOL_X))

    def test_row_1_x_wins(self) -> None:
        _mark_cells(self.board, self._row_cells(1), SYMBOL_X)
        self.assertTrue(WinChecker.check_winner(self.board, SYMBOL_X))

    def test_row_2_x_wins(self) -> None:
        _mark_cells(self.board, self._row_cells(2), SYMBOL_X)
        self.assertTrue(WinChecker.check_winner(self.board, SYMBOL_X))

    def test_row_3_x_wins(self) -> None:
        _mark_cells(self.board, self._row_cells(3), SYMBOL_X)
        self.assertTrue(WinChecker.check_winner(self.board, SYMBOL_X))

    def test_row_4_x_wins(self) -> None:
        _mark_cells(self.board, self._row_cells(4), SYMBOL_X)
        self.assertTrue(WinChecker.check_winner(self.board, SYMBOL_X))

    def test_row_0_o_wins(self) -> None:
        _mark_cells(self.board, self._row_cells(0), SYMBOL_O)
        self.assertTrue(WinChecker.check_winner(self.board, SYMBOL_O))

    def test_row_win_is_not_a_win_for_other_symbol(self) -> None:
        """A complete row for X must not report a win for O."""
        _mark_cells(self.board, self._row_cells(2), SYMBOL_X)
        self.assertFalse(WinChecker.check_winner(self.board, SYMBOL_O))


class TestWinCheckerColumns(unittest.TestCase):
    """WinChecker must detect a complete column of 5 for either symbol."""

    def setUp(self) -> None:
        self.board = Board()

    def _col_cells(self, col_index: int) -> list[int]:
        """Return the five 1-based cell numbers for a given 0-indexed column."""
        return [col_index + 1 + row * 5 for row in range(5)]

    def test_col_0_x_wins(self) -> None:
        _mark_cells(self.board, self._col_cells(0), SYMBOL_X)
        self.assertTrue(WinChecker.check_winner(self.board, SYMBOL_X))

    def test_col_1_x_wins(self) -> None:
        _mark_cells(self.board, self._col_cells(1), SYMBOL_X)
        self.assertTrue(WinChecker.check_winner(self.board, SYMBOL_X))

    def test_col_2_x_wins(self) -> None:
        _mark_cells(self.board, self._col_cells(2), SYMBOL_X)
        self.assertTrue(WinChecker.check_winner(self.board, SYMBOL_X))

    def test_col_3_x_wins(self) -> None:
        _mark_cells(self.board, self._col_cells(3), SYMBOL_X)
        self.assertTrue(WinChecker.check_winner(self.board, SYMBOL_X))

    def test_col_4_x_wins(self) -> None:
        _mark_cells(self.board, self._col_cells(4), SYMBOL_X)
        self.assertTrue(WinChecker.check_winner(self.board, SYMBOL_X))

    def test_col_0_o_wins(self) -> None:
        _mark_cells(self.board, self._col_cells(0), SYMBOL_O)
        self.assertTrue(WinChecker.check_winner(self.board, SYMBOL_O))

    def test_col_win_is_not_a_win_for_other_symbol(self) -> None:
        _mark_cells(self.board, self._col_cells(2), SYMBOL_X)
        self.assertFalse(WinChecker.check_winner(self.board, SYMBOL_O))


class TestWinCheckerDiagonals(unittest.TestCase):
    """WinChecker must detect both diagonals."""

    def setUp(self) -> None:
        self.board = Board()

    # Main diagonal: cells 1, 7, 13, 19, 25  (row=col)
    _MAIN_DIAGONAL = [1, 7, 13, 19, 25]
    # Anti-diagonal: cells 5, 9, 13, 17, 21  (row + col = 4)
    _ANTI_DIAGONAL = [5, 9, 13, 17, 21]

    def test_main_diagonal_x_wins(self) -> None:
        _mark_cells(self.board, self._MAIN_DIAGONAL, SYMBOL_X)
        self.assertTrue(WinChecker.check_winner(self.board, SYMBOL_X))

    def test_main_diagonal_o_wins(self) -> None:
        _mark_cells(self.board, self._MAIN_DIAGONAL, SYMBOL_O)
        self.assertTrue(WinChecker.check_winner(self.board, SYMBOL_O))

    def test_anti_diagonal_x_wins(self) -> None:
        _mark_cells(self.board, self._ANTI_DIAGONAL, SYMBOL_X)
        self.assertTrue(WinChecker.check_winner(self.board, SYMBOL_X))

    def test_anti_diagonal_o_wins(self) -> None:
        _mark_cells(self.board, self._ANTI_DIAGONAL, SYMBOL_O)
        self.assertTrue(WinChecker.check_winner(self.board, SYMBOL_O))

    def test_main_diagonal_x_is_not_win_for_o(self) -> None:
        _mark_cells(self.board, self._MAIN_DIAGONAL, SYMBOL_X)
        self.assertFalse(WinChecker.check_winner(self.board, SYMBOL_O))

    def test_partial_main_diagonal_no_win(self) -> None:
        _mark_cells(self.board, self._MAIN_DIAGONAL[:4], SYMBOL_X)
        self.assertFalse(WinChecker.check_winner(self.board, SYMBOL_X))

    def test_partial_anti_diagonal_no_win(self) -> None:
        _mark_cells(self.board, self._ANTI_DIAGONAL[:4], SYMBOL_O)
        self.assertFalse(WinChecker.check_winner(self.board, SYMBOL_O))


class TestWinCheckerIndividualMethods(unittest.TestCase):
    """Tests that target check_rows, check_columns, check_main_diagonal,
    and check_anti_diagonal directly (via the grid snapshot interface)."""

    def setUp(self) -> None:
        self.board = Board()

    def _grid(self) -> list[list[str]]:
        return self.board.get_grid()

    def test_check_rows_true_when_row_complete(self) -> None:
        _mark_cells(self.board, [1, 2, 3, 4, 5], SYMBOL_X)
        self.assertTrue(WinChecker.check_rows(self._grid(), SYMBOL_X))

    def test_check_rows_false_when_no_complete_row(self) -> None:
        _mark_cells(self.board, [1, 2, 3, 4], SYMBOL_X)
        self.assertFalse(WinChecker.check_rows(self._grid(), SYMBOL_X))

    def test_check_columns_true_when_column_complete(self) -> None:
        _mark_cells(self.board, [1, 6, 11, 16, 21], SYMBOL_X)
        self.assertTrue(WinChecker.check_columns(self._grid(), SYMBOL_X))

    def test_check_columns_false_when_no_complete_column(self) -> None:
        _mark_cells(self.board, [1, 6, 11, 16], SYMBOL_X)
        self.assertFalse(WinChecker.check_columns(self._grid(), SYMBOL_X))

    def test_check_main_diagonal_true(self) -> None:
        _mark_cells(self.board, [1, 7, 13, 19, 25], SYMBOL_X)
        self.assertTrue(WinChecker.check_main_diagonal(self._grid(), SYMBOL_X))

    def test_check_main_diagonal_false(self) -> None:
        _mark_cells(self.board, [1, 7, 13, 19], SYMBOL_X)
        self.assertFalse(WinChecker.check_main_diagonal(self._grid(), SYMBOL_X))

    def test_check_anti_diagonal_true(self) -> None:
        _mark_cells(self.board, [5, 9, 13, 17, 21], SYMBOL_X)
        self.assertTrue(WinChecker.check_anti_diagonal(self._grid(), SYMBOL_X))

    def test_check_anti_diagonal_false(self) -> None:
        _mark_cells(self.board, [5, 9, 13, 17], SYMBOL_X)
        self.assertFalse(WinChecker.check_anti_diagonal(self._grid(), SYMBOL_X))


if __name__ == "__main__":
    unittest.main()
