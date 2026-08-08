"""
test_board.py
-------------
Unit tests for game.board.Board.

Covers:
    - Board initialisation
    - Cell access (get_cell, is_cell_empty)
    - Cell mutation (update_cell)
    - Board lifecycle (reset_board)
    - Grid snapshot (get_grid immutability)
    - Guard conditions (ValueError on out-of-range / occupied cells)
"""

import unittest

from game.board import Board
from utils.constants import BOARD_SIZE, TOTAL_CELLS


class TestBoardInitialisation(unittest.TestCase):
    """Tests for a freshly created Board."""

    def setUp(self) -> None:
        self.board = Board()

    def test_grid_is_five_by_five(self) -> None:
        """The internal grid must be exactly BOARD_SIZE × BOARD_SIZE."""
        grid = self.board.get_grid()
        self.assertEqual(len(grid), BOARD_SIZE)
        for row in grid:
            self.assertEqual(len(row), BOARD_SIZE)

    def test_all_cells_contain_their_number(self) -> None:
        """Each cell on a fresh board holds its own 1-based number as a string."""
        for cell_number in range(1, TOTAL_CELLS + 1):
            self.assertEqual(self.board.get_cell(cell_number), str(cell_number))

    def test_all_cells_are_empty(self) -> None:
        """Every cell reports empty on a fresh board."""
        for cell_number in range(1, TOTAL_CELLS + 1):
            self.assertTrue(
                self.board.is_cell_empty(cell_number),
                msg=f"Cell {cell_number} should be empty on a fresh board",
            )


class TestBoardGetCell(unittest.TestCase):
    """Tests for Board.get_cell()."""

    def setUp(self) -> None:
        self.board = Board()

    def test_get_first_cell(self) -> None:
        self.assertEqual(self.board.get_cell(1), "1")

    def test_get_last_cell(self) -> None:
        self.assertEqual(self.board.get_cell(25), "25")

    def test_get_middle_cell(self) -> None:
        self.assertEqual(self.board.get_cell(13), "13")

    def test_get_cell_below_range_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.board.get_cell(0)

    def test_get_cell_above_range_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.board.get_cell(26)

    def test_get_cell_negative_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.board.get_cell(-1)

    def test_get_cell_float_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.board.get_cell(3.5)  # type: ignore[arg-type]


class TestBoardUpdateCell(unittest.TestCase):
    """Tests for Board.update_cell()."""

    def setUp(self) -> None:
        self.board = Board()

    def test_mark_cell_with_x(self) -> None:
        self.board.update_cell(1, "X")
        self.assertEqual(self.board.get_cell(1), "X")

    def test_mark_cell_with_o(self) -> None:
        self.board.update_cell(25, "O")
        self.assertEqual(self.board.get_cell(25), "O")

    def test_mark_cell_makes_it_occupied(self) -> None:
        self.board.update_cell(13, "X")
        self.assertFalse(self.board.is_cell_empty(13))

    def test_mark_occupied_cell_raises(self) -> None:
        self.board.update_cell(7, "X")
        with self.assertRaises(ValueError):
            self.board.update_cell(7, "O")

    def test_mark_out_of_range_raises_low(self) -> None:
        with self.assertRaises(ValueError):
            self.board.update_cell(0, "X")

    def test_mark_out_of_range_raises_high(self) -> None:
        with self.assertRaises(ValueError):
            self.board.update_cell(26, "X")

    def test_mark_multiple_cells_independently(self) -> None:
        self.board.update_cell(1, "X")
        self.board.update_cell(2, "O")
        self.assertEqual(self.board.get_cell(1), "X")
        self.assertEqual(self.board.get_cell(2), "O")
        self.assertEqual(self.board.get_cell(3), "3")  # untouched


class TestBoardIsCellEmpty(unittest.TestCase):
    """Tests for Board.is_cell_empty()."""

    def setUp(self) -> None:
        self.board = Board()

    def test_empty_before_mark(self) -> None:
        self.assertTrue(self.board.is_cell_empty(5))

    def test_not_empty_after_mark(self) -> None:
        self.board.update_cell(5, "X")
        self.assertFalse(self.board.is_cell_empty(5))

    def test_neighbours_unaffected(self) -> None:
        self.board.update_cell(5, "X")
        self.assertTrue(self.board.is_cell_empty(4))
        self.assertTrue(self.board.is_cell_empty(6))

    def test_out_of_range_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.board.is_cell_empty(0)


class TestBoardResetBoard(unittest.TestCase):
    """Tests for Board.reset_board()."""

    def setUp(self) -> None:
        self.board = Board()

    def test_reset_clears_marked_cells(self) -> None:
        self.board.update_cell(1, "X")
        self.board.update_cell(13, "O")
        self.board.reset_board()
        self.assertEqual(self.board.get_cell(1), "1")
        self.assertEqual(self.board.get_cell(13), "13")

    def test_reset_restores_all_cells(self) -> None:
        for n in range(1, TOTAL_CELLS + 1):
            self.board.update_cell(n, "X")
        self.board.reset_board()
        for n in range(1, TOTAL_CELLS + 1):
            self.assertTrue(
                self.board.is_cell_empty(n),
                msg=f"Cell {n} should be empty after reset",
            )

    def test_reset_allows_re_marking(self) -> None:
        self.board.update_cell(5, "X")
        self.board.reset_board()
        # Should not raise after reset
        self.board.update_cell(5, "O")
        self.assertEqual(self.board.get_cell(5), "O")


class TestBoardGetGrid(unittest.TestCase):
    """Tests for Board.get_grid() immutability."""

    def setUp(self) -> None:
        self.board = Board()

    def test_get_grid_returns_correct_shape(self) -> None:
        grid = self.board.get_grid()
        self.assertEqual(len(grid), BOARD_SIZE)
        self.assertEqual(len(grid[0]), BOARD_SIZE)

    def test_get_grid_is_a_copy(self) -> None:
        """Mutating the returned grid must not affect the board's internal state."""
        grid = self.board.get_grid()
        grid[0][0] = "TAMPERED"
        self.assertEqual(self.board.get_cell(1), "1")

    def test_get_grid_reflects_marks(self) -> None:
        self.board.update_cell(1, "X")
        grid = self.board.get_grid()
        self.assertEqual(grid[0][0], "X")


class TestBoardCellLayout(unittest.TestCase):
    """Tests that the 1-based numbering maps to the correct (row, col) positions."""

    def setUp(self) -> None:
        self.board = Board()

    def _mark_and_get(self, cell_number: int) -> tuple[int, int]:
        """Mark a cell and find its (row, col) in the grid."""
        self.board.update_cell(cell_number, "X")
        grid = self.board.get_grid()
        for r, row in enumerate(grid):
            for c, val in enumerate(row):
                if val == "X":
                    return r, c
        raise AssertionError(f"Cell {cell_number} not found in grid")

    def test_cell_1_is_top_left(self) -> None:
        self.assertEqual(self._mark_and_get(1), (0, 0))

    def test_cell_5_is_top_right(self) -> None:
        self.board.reset_board()
        self.assertEqual(self._mark_and_get(5), (0, 4))

    def test_cell_13_is_center(self) -> None:
        self.board.reset_board()
        self.assertEqual(self._mark_and_get(13), (2, 2))

    def test_cell_21_is_bottom_left(self) -> None:
        self.board.reset_board()
        self.assertEqual(self._mark_and_get(21), (4, 0))

    def test_cell_25_is_bottom_right(self) -> None:
        self.board.reset_board()
        self.assertEqual(self._mark_and_get(25), (4, 4))


if __name__ == "__main__":
    unittest.main()
