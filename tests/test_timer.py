"""
test_timer.py
-------------
Unit tests for game.timer.MoveTimer and game.timer.TimedInputReader.

MoveTimer tests use a very short time limit (0.1 s) so the suite runs fast.

Covers (MoveTimer):
    - Not expired before timeout
    - Expiry after time limit elapses
    - stop() prevents expiry
    - reset() clears expired state
    - remaining_seconds() decrements and never goes below zero

Covers (TimedInputReader):
    - Returns None when stdin produces no input within the time limit
    - Returns the typed string when input arrives in time
      (simulated via unittest.mock.patch on builtins.input)
"""

import time
import unittest
from unittest.mock import patch

from game.timer import MoveTimer, TimedInputReader


# ---------------------------------------------------------------------------
# MoveTimer tests
# ---------------------------------------------------------------------------

class TestMoveTimerNotStarted(unittest.TestCase):
    """MoveTimer before start() is called."""

    def test_not_expired_before_start(self) -> None:
        timer = MoveTimer(time_limit=1)
        self.assertFalse(timer.is_expired())

    def test_remaining_seconds_before_start(self) -> None:
        timer = MoveTimer(time_limit=5)
        self.assertEqual(timer.remaining_seconds(), 5)


class TestMoveTimerExpiry(unittest.TestCase):
    """MoveTimer expiry behaviour."""

    _LIMIT = 0.15       # 150 ms — just long enough to be reliable on CI
    _WAIT  = 0.30       # wait twice the limit to guarantee expiry

    def test_expires_after_time_limit(self) -> None:
        timer = MoveTimer(time_limit=self._LIMIT)
        timer.start()
        time.sleep(self._WAIT)
        self.assertTrue(timer.is_expired())

    def test_not_expired_before_time_limit(self) -> None:
        timer = MoveTimer(time_limit=5)
        timer.start()
        # Immediate check — nowhere near expiry
        self.assertFalse(timer.is_expired())
        timer.stop()

    def test_stop_prevents_expiry(self) -> None:
        timer = MoveTimer(time_limit=self._LIMIT)
        timer.start()
        timer.stop()
        time.sleep(self._WAIT)
        # Timer was stopped before the limit — must not be expired
        self.assertFalse(timer.is_expired())


class TestMoveTimerReset(unittest.TestCase):
    """MoveTimer.reset() restores the timer to its initial state."""

    _LIMIT = 0.15
    _WAIT  = 0.30

    def test_reset_clears_expired_flag(self) -> None:
        timer = MoveTimer(time_limit=self._LIMIT)
        timer.start()
        time.sleep(self._WAIT)
        self.assertTrue(timer.is_expired())   # expired before reset

        timer.reset()
        self.assertFalse(timer.is_expired())  # cleared after reset

    def test_reset_restores_remaining_seconds(self) -> None:
        timer = MoveTimer(time_limit=3)
        timer.start()
        timer.stop()
        timer.reset()
        self.assertEqual(timer.remaining_seconds(), 3)

    def test_timer_usable_after_reset(self) -> None:
        """A reset timer can be started again and expire normally."""
        timer = MoveTimer(time_limit=self._LIMIT)
        timer.start()
        time.sleep(self._WAIT)
        timer.reset()
        timer.start()
        time.sleep(self._WAIT)
        self.assertTrue(timer.is_expired())


class TestMoveTimerRemainingSeconds(unittest.TestCase):
    """MoveTimer.remaining_seconds() boundary checks."""

    def test_remaining_never_goes_negative(self) -> None:
        """Remaining seconds must clamp at 0, never go below."""
        timer = MoveTimer(time_limit=0.05)
        timer.start()
        time.sleep(0.20)         # well past the limit
        self.assertGreaterEqual(timer.remaining_seconds(), 0)
        timer.stop()

    def test_remaining_is_full_before_start(self) -> None:
        timer = MoveTimer(time_limit=10)
        self.assertEqual(timer.remaining_seconds(), 10)


# ---------------------------------------------------------------------------
# TimedInputReader tests
# ---------------------------------------------------------------------------

class TestTimedInputReaderTimeout(unittest.TestCase):
    """TimedInputReader must return None when no input arrives in time."""

    def test_returns_none_on_timeout(self) -> None:
        """With a 0.1 s limit and no stdin input, result must be None."""
        reader = TimedInputReader(time_limit=0.1)
        result = reader.read_input(prompt="")
        self.assertIsNone(result)


class TestTimedInputReaderWithMockedStdin(unittest.TestCase):
    """TimedInputReader must return the input string when input() fires in time.

    We patch builtins.input to return immediately with a preset value.
    The background thread picks up the mock and places the value in the queue
    before the main thread times out.
    """

    def test_returns_input_string_when_available(self) -> None:
        expected = "13"
        with patch("builtins.input", return_value=expected):
            reader = TimedInputReader(time_limit=2)
            result = reader.read_input(prompt="")
        self.assertEqual(result, expected)

    def test_returns_stripped_input_as_typed(self) -> None:
        """TimedInputReader should return the raw string exactly as input() gave it."""
        expected = "  7  "
        with patch("builtins.input", return_value=expected):
            reader = TimedInputReader(time_limit=2)
            result = reader.read_input(prompt="")
        # The reader does NOT strip — stripping is InputValidator's job.
        self.assertEqual(result, expected)

    def test_empty_string_input_is_returned(self) -> None:
        """An empty Enter press is valid input (an empty string, not None)."""
        with patch("builtins.input", return_value=""):
            reader = TimedInputReader(time_limit=2)
            result = reader.read_input(prompt="")
        self.assertEqual(result, "")

    def test_double_keyword_is_returned(self) -> None:
        with patch("builtins.input", return_value="double"):
            reader = TimedInputReader(time_limit=2)
            result = reader.read_input(prompt="")
        self.assertEqual(result, "double")


class TestTimedInputReaderRepr(unittest.TestCase):
    def test_repr_contains_time_limit(self) -> None:
        reader = TimedInputReader(time_limit=15)
        self.assertIn("15", repr(reader))


if __name__ == "__main__":
    unittest.main()
