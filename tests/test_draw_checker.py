"""
test_draw_checker.py
--------------------
Unit tests for game.draw_checker.DrawChecker.

Draw board layout used across tests:

    Row 0: X X O O X   (cells  1  2  3  4  5)
    Row 1: O O X X O   (cells  6  7  8  9 10)
    Row 2: X X O O X   (cells 11 12 13 14 15)
    Row 3: O O X X O   (cells 16 17 18 19 20)
    Row 4: X X O O X   (cells 21 22 23 24 25)

Verified properties:
    - All 25 cells occupied              → board is full
    - No row is uniform                  → no row winner
    - No column is uniform               → no column winner
    - Main diagonal (1,7,13,19,25) = X,X,O,X,X  → not uniform
    - Anti-diagonal (5,9,13,17,21) = X,X,O,O,X  → not uniform
    - Neither WinChecker.check_winner(X) nor (O) returns True

Covers:
    - is_board_full on fresh / partially filled / fully filled boards
    - is_draw on a genuine draw board
    - is_draw returns False when a winner exists
    - is_draw returns False when the board is not yet full
    - count_empty_cells counts correctly at each stage
"""

import unittest

from game.board import Board
from game.draw_checker import DrawChecker
from utils.constants import SYMBOL_X, SYMBOL_O


# ---------------------------------------------------------------------------
# Constants describing the draw board
# ---------------------------------------------------------------------------

_X_CELLS = [1, 2, 5, 8, 9, 11, 12, 15, 18, 19, 21, 22, 25]
_O_CELLS = [3, 4, 6, 7, 10, 13, 14, 16, 17, 20, 23, 24]


def _build_draw_board() -> Board:
    """Return a Board in the verified-draw state (full, no winner)."""
    board = Board()
    for cell in _X_CELLS:
        board.update_cell(cell, SYMBOL_X)
    for cell in _O_CELLS:
        board.update_cell(cell, SYMBOL_O)
    return board


def _build_x_row_win_board() -> Board:
    """Return a Board where X has won the first row (cells 1–5)."""
    board = Board()
    for cell in [1, 2, 3, 4, 5]:
        board.update_cell(cell, SYMBOL_X)
    return board


# ---------------------------------------------------------------------------
# Test classes
# ---------------------------------------------------------------------------

class TestIsBoardFull(unittest.TestCase):
    """Tests for DrawChecker.is_board_full()."""

    def test_fresh_board_is_not_full(self) -> None:
        self.assertFalse(DrawChecker.is_board_full(Board()))

    def test_partially_filled_board_is_not_full(self) -> None:
        board = Board()
        board.update_cell(1, SYMBOL_X)
        board.update_cell(13, SYMBOL_O)
        self.assertFalse(DrawChecker.is_board_full(board))

    def test_24_cells_filled_is_not_full(self) -> None:
        """One empty cell left must still report not full."""
        board = _build_draw_board()
        # Remove the last X cell to leave one empty slot
        board.reset_board()
        for cell in _X_CELLS[:-1]:        # all X cells except the last
            board.update_cell(cell, SYMBOL_X)
        for cell in _O_CELLS:
            board.update_cell(cell, SYMBOL_O)
        self.assertFalse(DrawChecker.is_board_full(board))

    def test_fully_marked_board_is_full(self) -> None:
        self.assertTrue(DrawChecker.is_board_full(_build_draw_board()))

    def test_all_x_board_is_full(self) -> None:
        board = Board()
        for cell in range(1, 26):
            board.update_cell(cell, SYMBOL_X)
        self.assertTrue(DrawChecker.is_board_full(board))


class TestCountEmptyCells(unittest.TestCase):
    """Tests for DrawChecker.count_empty_cells()."""

    def test_fresh_board_has_25_empty(self) -> None:
        self.assertEqual(DrawChecker.count_empty_cells(Board()), 25)

    def test_one_marked_cell(self) -> None:
        board = Board()
        board.update_cell(1, SYMBOL_X)
        self.assertEqual(DrawChecker.count_empty_cells(board), 24)

    def test_all_marked_cells(self) -> None:
        self.assertEqual(DrawChecker.count_empty_cells(_build_draw_board()), 0)

    def test_count_decrements_with_each_mark(self) -> None:
        board = Board()
        for i, cell in enumerate(range(1, 6), start=1):
            board.update_cell(cell, SYMBOL_X)
            self.assertEqual(DrawChecker.count_empty_cells(board), 25 - i)


class TestIsDraw(unittest.TestCase):
    """Tests for DrawChecker.is_draw()."""

    def test_fresh_board_is_not_draw(self) -> None:
        self.assertFalse(DrawChecker.is_draw(Board()))

    def test_partially_filled_no_winner_is_not_draw(self) -> None:
        board = Board()
        board.update_cell(1, SYMBOL_X)
        board.update_cell(7, SYMBOL_O)
        self.assertFalse(DrawChecker.is_draw(board))

    def test_full_board_no_winner_is_draw(self) -> None:
        """The verified draw board must report True."""
        self.assertTrue(DrawChecker.is_draw(_build_draw_board()))

    def test_full_board_with_row_winner_is_not_draw(self) -> None:
        """A full board where X won should not report a draw."""
        # Fill the rest of the board after an X row win
        board = _build_x_row_win_board()
        # Mark remaining cells alternating O and X (rows 1–4)
        symbol_cycle = [SYMBOL_O, SYMBOL_X]
        toggle = 0
        for cell in range(6, 26):
            board.update_cell(cell, symbol_cycle[toggle % 2])
            toggle += 1
        # Board is full — but X already won row 0
        self.assertFalse(DrawChecker.is_draw(board))

    def test_full_board_x_wins_row_0_not_draw(self) -> None:
        """Sanity: confirm X's row win is detected, ruling out a draw."""
        board = Board()
        for cell in [1, 2, 3, 4, 5]:
            board.update_cell(cell, SYMBOL_X)
        # Not full yet — clearly not a draw
        self.assertFalse(DrawChecker.is_draw(board))

    def test_draw_board_x_no_winner(self) -> None:
        """The draw board must yield no X win (pre-condition for is_draw)."""
        from game.win_checker import WinChecker
        board = _build_draw_board()
        self.assertFalse(WinChecker.check_winner(board, SYMBOL_X))

    def test_draw_board_o_no_winner(self) -> None:
        """The draw board must yield no O win (pre-condition for is_draw)."""
        from game.win_checker import WinChecker
        board = _build_draw_board()
        self.assertFalse(WinChecker.check_winner(board, SYMBOL_O))

    def test_draw_board_is_full(self) -> None:
        """Pre-condition: the draw board must be full."""
        self.assertTrue(DrawChecker.is_board_full(_build_draw_board()))


if __name__ == "__main__":
    unittest.main()
