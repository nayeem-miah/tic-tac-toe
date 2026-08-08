"""
test_player.py
--------------
Unit tests for game.player.Player.

Covers:
    - Construction and validation
    - Properties (name, symbol, rounds_won, double_turn_available)
    - Mutators (increment_rounds_won, use_double_turn, reset_for_new_match)
    - Guard conditions (empty name, invalid symbol, double-use of ability)
    - Helper methods (get_status_summary, __str__, __repr__)
"""

import unittest

from game.player import Player
from utils.constants import SYMBOL_X, SYMBOL_O


class TestPlayerConstruction(unittest.TestCase):
    """Tests for Player.__init__ and validation guards."""

    def test_valid_player_x(self) -> None:
        player = Player("Alice", SYMBOL_X)
        self.assertEqual(player.name, "Alice")
        self.assertEqual(player.symbol, SYMBOL_X)

    def test_valid_player_o(self) -> None:
        player = Player("Bob", SYMBOL_O)
        self.assertEqual(player.name, "Bob")
        self.assertEqual(player.symbol, SYMBOL_O)

    def test_name_is_stripped(self) -> None:
        """Leading/trailing whitespace in the name should be stripped."""
        player = Player("  Alice  ", SYMBOL_X)
        self.assertEqual(player.name, "Alice")

    def test_empty_name_raises(self) -> None:
        with self.assertRaises(ValueError):
            Player("", SYMBOL_X)

    def test_whitespace_only_name_raises(self) -> None:
        with self.assertRaises(ValueError):
            Player("   ", SYMBOL_X)

    def test_invalid_symbol_raises(self) -> None:
        with self.assertRaises(ValueError):
            Player("Alice", "Z")

    def test_lowercase_symbol_raises(self) -> None:
        with self.assertRaises(ValueError):
            Player("Alice", "x")

    def test_empty_symbol_raises(self) -> None:
        with self.assertRaises(ValueError):
            Player("Alice", "")


class TestPlayerInitialState(unittest.TestCase):
    """Tests for the default state of a newly created Player."""

    def setUp(self) -> None:
        self.player = Player("Alice", SYMBOL_X)

    def test_rounds_won_starts_at_zero(self) -> None:
        self.assertEqual(self.player.rounds_won, 0)

    def test_double_turn_is_available_initially(self) -> None:
        self.assertTrue(self.player.double_turn_available)


class TestPlayerIncrementRoundsWon(unittest.TestCase):
    """Tests for Player.increment_rounds_won()."""

    def setUp(self) -> None:
        self.player = Player("Alice", SYMBOL_X)

    def test_increment_once(self) -> None:
        self.player.increment_rounds_won()
        self.assertEqual(self.player.rounds_won, 1)

    def test_increment_multiple_times(self) -> None:
        self.player.increment_rounds_won()
        self.player.increment_rounds_won()
        self.assertEqual(self.player.rounds_won, 2)


class TestPlayerDoubleTurn(unittest.TestCase):
    """Tests for the Double Turn ability (use_double_turn, double_turn_available)."""

    def setUp(self) -> None:
        self.player = Player("Alice", SYMBOL_X)

    def test_use_double_turn_consumes_ability(self) -> None:
        self.player.use_double_turn()
        self.assertFalse(self.player.double_turn_available)

    def test_use_double_turn_twice_raises(self) -> None:
        self.player.use_double_turn()
        with self.assertRaises(ValueError):
            self.player.use_double_turn()

    def test_double_turn_available_before_use(self) -> None:
        self.assertTrue(self.player.double_turn_available)

    def test_double_turn_unavailable_after_use(self) -> None:
        self.player.use_double_turn()
        self.assertFalse(self.player.double_turn_available)


class TestPlayerResetForNewMatch(unittest.TestCase):
    """Tests for Player.reset_for_new_match()."""

    def setUp(self) -> None:
        self.player = Player("Alice", SYMBOL_X)

    def test_reset_clears_rounds_won(self) -> None:
        self.player.increment_rounds_won()
        self.player.increment_rounds_won()
        self.player.reset_for_new_match()
        self.assertEqual(self.player.rounds_won, 0)

    def test_reset_restores_double_turn(self) -> None:
        self.player.use_double_turn()
        self.player.reset_for_new_match()
        self.assertTrue(self.player.double_turn_available)

    def test_reset_does_not_change_name(self) -> None:
        self.player.reset_for_new_match()
        self.assertEqual(self.player.name, "Alice")

    def test_reset_does_not_change_symbol(self) -> None:
        self.player.reset_for_new_match()
        self.assertEqual(self.player.symbol, SYMBOL_X)

    def test_double_turn_usable_again_after_reset(self) -> None:
        self.player.use_double_turn()
        self.player.reset_for_new_match()
        # Must not raise
        self.player.use_double_turn()
        self.assertFalse(self.player.double_turn_available)


class TestPlayerHelpers(unittest.TestCase):
    """Tests for __str__, __repr__, and get_status_summary."""

    def setUp(self) -> None:
        self.player = Player("Alice", SYMBOL_X)

    def test_str_contains_name(self) -> None:
        self.assertIn("Alice", str(self.player))

    def test_str_contains_symbol(self) -> None:
        self.assertIn(SYMBOL_X, str(self.player))

    def test_repr_is_non_empty(self) -> None:
        self.assertTrue(len(repr(self.player)) > 0)

    def test_status_summary_contains_name(self) -> None:
        self.assertIn("Alice", self.player.get_status_summary())

    def test_status_summary_contains_symbol(self) -> None:
        self.assertIn(SYMBOL_X, self.player.get_status_summary())

    def test_status_summary_shows_available(self) -> None:
        self.assertIn("available", self.player.get_status_summary())

    def test_status_summary_shows_used(self) -> None:
        self.player.use_double_turn()
        self.assertIn("used", self.player.get_status_summary())


if __name__ == "__main__":
    unittest.main()
