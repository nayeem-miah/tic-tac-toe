"""
test_double_turn.py
-------------------
Unit tests for game.double_turn.DoubleTurnManager and DoubleTurnResult.

Covers:
    - is_activation_request: keyword matching (case, whitespace, non-match)
    - can_activate: eligibility based on player state
    - try_activate: full activation path (not keyword / eligible / already used)
    - Player state after activation (double_turn_available becomes False)
    - DoubleTurnResult fields (activated, is_keyword, message)
    - Message content for rejection (already used) and success
"""

import unittest

from game.double_turn import DoubleTurnManager, DoubleTurnResult
from game.player import Player
from utils.constants import SYMBOL_X, SYMBOL_O


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _fresh_player(name: str = "Alice", symbol: str = SYMBOL_X) -> Player:
    """Return a Player with the Double Turn still available."""
    return Player(name, symbol)


def _used_player(name: str = "Bob", symbol: str = SYMBOL_O) -> Player:
    """Return a Player who has already consumed their Double Turn."""
    player = Player(name, symbol)
    player.use_double_turn()
    return player


# ---------------------------------------------------------------------------
# Test classes
# ---------------------------------------------------------------------------

class TestIsActivationRequest(unittest.TestCase):
    """DoubleTurnManager.is_activation_request() must match keyword flexibly."""

    def test_exact_lowercase(self) -> None:
        self.assertTrue(DoubleTurnManager.is_activation_request("double"))

    def test_all_uppercase(self) -> None:
        self.assertTrue(DoubleTurnManager.is_activation_request("DOUBLE"))

    def test_title_case(self) -> None:
        self.assertTrue(DoubleTurnManager.is_activation_request("Double"))

    def test_mixed_case(self) -> None:
        self.assertTrue(DoubleTurnManager.is_activation_request("dOuBlE"))

    def test_leading_whitespace(self) -> None:
        self.assertTrue(DoubleTurnManager.is_activation_request("  double"))

    def test_trailing_whitespace(self) -> None:
        self.assertTrue(DoubleTurnManager.is_activation_request("double  "))

    def test_surrounding_whitespace(self) -> None:
        self.assertTrue(DoubleTurnManager.is_activation_request("  double  "))

    def test_cell_number_is_not_keyword(self) -> None:
        self.assertFalse(DoubleTurnManager.is_activation_request("13"))

    def test_empty_string_is_not_keyword(self) -> None:
        self.assertFalse(DoubleTurnManager.is_activation_request(""))

    def test_partial_keyword_is_not_keyword(self) -> None:
        self.assertFalse(DoubleTurnManager.is_activation_request("doub"))

    def test_whitespace_only_is_not_keyword(self) -> None:
        self.assertFalse(DoubleTurnManager.is_activation_request("   "))

    def test_keyword_with_extra_chars_is_not_keyword(self) -> None:
        self.assertFalse(DoubleTurnManager.is_activation_request("double!"))


class TestCanActivate(unittest.TestCase):
    """DoubleTurnManager.can_activate() reflects player eligibility."""

    def test_eligible_player_can_activate(self) -> None:
        self.assertTrue(DoubleTurnManager.can_activate(_fresh_player()))

    def test_player_who_used_ability_cannot_activate(self) -> None:
        self.assertFalse(DoubleTurnManager.can_activate(_used_player()))


class TestTryActivateNotKeyword(unittest.TestCase):
    """try_activate with non-keyword input must return a non-keyword result."""

    def test_cell_number_input_not_keyword(self) -> None:
        result = DoubleTurnManager.try_activate("13", _fresh_player())
        self.assertFalse(result.is_keyword)
        self.assertFalse(result.activated)
        self.assertEqual(result.message, "")

    def test_empty_input_not_keyword(self) -> None:
        result = DoubleTurnManager.try_activate("", _fresh_player())
        self.assertFalse(result.is_keyword)
        self.assertFalse(result.activated)

    def test_bool_of_non_keyword_result_is_false(self) -> None:
        result = DoubleTurnManager.try_activate("5", _fresh_player())
        self.assertFalse(bool(result))


class TestTryActivateEligible(unittest.TestCase):
    """try_activate with keyword + eligible player must activate successfully."""

    def setUp(self) -> None:
        self.player = _fresh_player()
        self.result = DoubleTurnManager.try_activate("double", self.player)

    def test_activated_is_true(self) -> None:
        self.assertTrue(self.result.activated)

    def test_is_keyword_is_true(self) -> None:
        self.assertTrue(self.result.is_keyword)

    def test_message_is_non_empty(self) -> None:
        self.assertTrue(len(self.result.message) > 0)

    def test_message_contains_player_name(self) -> None:
        self.assertIn(self.player.name, self.result.message)

    def test_player_double_turn_consumed(self) -> None:
        self.assertFalse(self.player.double_turn_available)

    def test_bool_of_successful_result_is_true(self) -> None:
        self.assertTrue(bool(self.result))


class TestTryActivateAlreadyUsed(unittest.TestCase):
    """try_activate with keyword + player who already used ability must fail."""

    def setUp(self) -> None:
        self.player = _used_player("Bob", SYMBOL_O)
        self.result = DoubleTurnManager.try_activate("double", self.player)

    def test_activated_is_false(self) -> None:
        self.assertFalse(self.result.activated)

    def test_is_keyword_is_true(self) -> None:
        """Even a rejected request was the keyword."""
        self.assertTrue(self.result.is_keyword)

    def test_message_explains_rejection(self) -> None:
        """Rejection message must mention the player's name or symbol."""
        self.assertTrue(
            self.player.name in self.result.message
            or self.player.symbol in self.result.message
        )

    def test_bool_of_failed_result_is_false(self) -> None:
        self.assertFalse(bool(self.result))


class TestTryActivateCaseInsensitive(unittest.TestCase):
    """try_activate must accept keyword in any case."""

    def test_uppercase_keyword_activates(self) -> None:
        player = _fresh_player()
        result = DoubleTurnManager.try_activate("DOUBLE", player)
        self.assertTrue(result.activated)

    def test_mixed_case_keyword_activates(self) -> None:
        player = _fresh_player()
        result = DoubleTurnManager.try_activate("DoUbLe", player)
        self.assertTrue(result.activated)


class TestDoubleTurnResultDataclass(unittest.TestCase):
    """DoubleTurnResult is frozen and truth-tests via .activated."""

    def test_result_is_immutable(self) -> None:
        result = DoubleTurnResult(activated=True, message="ok", is_keyword=True)
        with self.assertRaises((AttributeError, TypeError)):
            result.activated = False  # type: ignore[misc]

    def test_bool_true_when_activated(self) -> None:
        result = DoubleTurnResult(activated=True, message="", is_keyword=True)
        self.assertTrue(bool(result))

    def test_bool_false_when_not_activated(self) -> None:
        result = DoubleTurnResult(activated=False, message="", is_keyword=False)
        self.assertFalse(bool(result))


if __name__ == "__main__":
    unittest.main()
