"""
timer.py
--------
Responsibility:
    Provides a reusable, thread-safe countdown timer and a helper for
    reading player input within a fixed time window.

    Two public classes:

    MoveTimer
        A self-contained countdown timer backed by threading.Event
        and threading.Timer.  It knows nothing about the game; it
        only tracks whether a given number of seconds has elapsed.

    TimedInputReader
        Reads one line from stdin in a background thread and returns
        it within the time limit, or returns None on timeout.
        Uses a queue.Queue for safe cross-thread communication.

    Neither class prints messages, modifies the board, or drives
    game flow.  They are fully reusable outside this project.

    Follows Single Responsibility Principle (SRP).
    Thread-safety is achieved via threading.Event and queue.Queue
    (no manual locks needed).
"""

import threading
import queue
import time
from typing import Optional
from utils.constants import MOVE_TIME_LIMIT


# ---------------------------------------------------------------------------
# MoveTimer
# ---------------------------------------------------------------------------

class MoveTimer:
    """
    Thread-safe countdown timer for a single timed event window.

    Lifecycle::

        timer = MoveTimer(time_limit=15)
        timer.start()
        # ... player types their move ...
        if timer.is_expired():
            # turn was lost
        else:
            timer.stop()   # cancel before expiry

    The same instance can be reused across turns by calling reset()
    between uses.

    Attributes (private):
        _time_limit  : Total seconds for the countdown.
        _start_time  : Monotonic timestamp of when start() was called.
        _expired_flag: threading.Event set when the countdown fires.
        _timer_thread: Internal threading.Timer instance.
    """

    def __init__(self, time_limit: int = MOVE_TIME_LIMIT) -> None:
        """
        Initialise the timer.

        Args:
            time_limit: Number of seconds to count down. Defaults to
                        MOVE_TIME_LIMIT (15 seconds).
        """
        self._time_limit: int = time_limit
        self._start_time: Optional[float] = None
        self._expired_flag: threading.Event = threading.Event()
        self._timer_thread: Optional[threading.Timer] = None

    # ------------------------------------------------------------------
    # Control
    # ------------------------------------------------------------------

    def start(self) -> None:
        """
        Begin the countdown in a background thread.

        The internal threading.Timer will call _on_timeout() after
        _time_limit seconds, setting the expired flag.

        If start() is called while a countdown is already running,
        the existing timer is cancelled first and a fresh one starts.
        """
        self._cancel_timer()
        self._expired_flag.clear()
        self._start_time = time.monotonic()

        self._timer_thread = threading.Timer(
            interval=self._time_limit,
            function=self._on_timeout,
        )
        self._timer_thread.daemon = True   # won't block program exit
        self._timer_thread.start()

    def stop(self) -> None:
        """
        Cancel the running countdown (call this when a valid move arrives
        before the time limit is reached).

        Safe to call even if the timer has already expired or was never
        started — no exception will be raised.
        """
        self._cancel_timer()

    def reset(self) -> None:
        """
        Stop any running countdown and clear the expired flag.

        Use this to prepare the timer for a completely fresh turn
        without creating a new instance.
        """
        self._cancel_timer()
        self._expired_flag.clear()
        self._start_time = None

    # ------------------------------------------------------------------
    # State queries
    # ------------------------------------------------------------------

    def is_expired(self) -> bool:
        """
        Return True if the countdown ran to zero before stop() was called.

        Thread-safe: reads a threading.Event flag.

        Returns:
            True  — the player ran out of time.
            False — time is still remaining, or the timer was stopped.
        """
        return self._expired_flag.is_set()

    def remaining_seconds(self) -> float:
        """
        Return an approximate number of seconds still available.

        Calculated from the monotonic clock so it is unaffected by
        system clock adjustments.

        Returns:
            Seconds remaining as a float, clamped to a minimum of 0.0.
            Returns the full time_limit if the timer has not been started.
        """
        if self._start_time is None:
            return float(self._time_limit)

        elapsed = time.monotonic() - self._start_time
        remaining = self._time_limit - elapsed
        return max(0.0, remaining)

    @property
    def time_limit(self) -> int:
        """Return the configured time limit in seconds."""
        return self._time_limit

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _on_timeout(self) -> None:
        """
        Callback invoked by the background threading.Timer on expiry.

        Sets the expired flag so any thread polling is_expired() will
        see the change immediately.
        """
        self._expired_flag.set()

    def _cancel_timer(self) -> None:
        """Cancel the internal threading.Timer if one is running."""
        if self._timer_thread is not None:
            self._timer_thread.cancel()
            self._timer_thread = None

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"MoveTimer(time_limit={self._time_limit}, "
            f"expired={self.is_expired()}, "
            f"remaining={self.remaining_seconds():.1f}s)"
        )


# ---------------------------------------------------------------------------
# TimedInputReader
# ---------------------------------------------------------------------------

class TimedInputReader:
    """
    Reads one line from stdin within a time limit.

    Python's built-in input() blocks the calling thread indefinitely,
    so we push it into a daemon thread and communicate the result via
    a queue.Queue.  The main thread then waits on the queue with a
    timeout matching the timer's remaining seconds.

    This approach is cross-platform (works on Windows where select()
    does not support stdin).

    Usage::

        reader = TimedInputReader(time_limit=15)
        raw = reader.read_input(prompt="Enter cell (1-25): ")
        if raw is None:
            # player timed out
        else:
            # raw is the string the player typed

    Attributes (private):
        _time_limit: Seconds to wait for input before returning None.
        _result_queue: Thread-safe queue for the input string.
    """

    def __init__(self, time_limit: int = MOVE_TIME_LIMIT) -> None:
        """
        Initialise the reader.

        Args:
            time_limit: Seconds to wait for input before timing out.
        """
        self._time_limit: int = time_limit
        self._result_queue: queue.Queue[Optional[str]] = queue.Queue(maxsize=1)

    def read_input(self, prompt: str = "") -> Optional[str]:
        """
        Display prompt, then wait up to time_limit seconds for the
        player to type and press Enter.

        The stdin read happens in a background daemon thread.  The main
        thread blocks on queue.get(timeout=...) and returns as soon as
        either the player submits input or the time runs out.

        Args:
            prompt: Text to display before waiting for input.

        Returns:
            The stripped string the player entered, or None on timeout.
        """
        # Drain any leftover items from a previous use
        while not self._result_queue.empty():
            try:
                self._result_queue.get_nowait()
            except queue.Empty:
                break

        # Launch the blocking input() in a daemon thread
        reader_thread = threading.Thread(
            target=self._read_from_stdin,
            args=(prompt,),
            daemon=True,   # will not prevent program exit
        )
        reader_thread.start()

        # Wait on the queue for at most time_limit seconds
        try:
            raw: Optional[str] = self._result_queue.get(timeout=self._time_limit)
            return raw
        except queue.Empty:
            # Player did not submit input in time
            return None

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _read_from_stdin(self, prompt: str) -> None:
        """
        Target function for the background reader thread.

        Calls input() with the given prompt and places the result in
        the queue.  If an EOFError occurs (e.g. stdin is closed), None
        is placed in the queue so the caller handles it gracefully.

        Args:
            prompt: The prompt string to pass to input().
        """
        try:
            user_input: str = input(prompt)
            self._result_queue.put(user_input)
        except EOFError:
            # stdin was closed (piped input, redirected file, etc.)
            self._result_queue.put(None)
        except Exception:  # noqa: BLE001
            # Any unexpected I/O or OS error in the background thread —
            # treat as no input so the main thread times out gracefully.
            self._result_queue.put(None)

    def __repr__(self) -> str:
        return f"TimedInputReader(time_limit={self._time_limit})"
