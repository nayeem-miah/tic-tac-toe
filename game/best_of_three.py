"""
best_of_three.py
----------------
Responsibility:
    Tracks the score across up to three rounds and determines when
    the match is over.

    Owns:
        - Rounds played counter
        - Per-player round-win tallies
        - Match-over and match-winner logic
        - Human-readable score and result formatting

    Does NOT own:
        - Board state
        - Player input
        - Turn logic
        - Timer

    Display methods (display_round_result, display_score) print
    directly to the console so the module is fully self-contained
    and testable without wiring up a Display instance.
    When integrated into the full game the Match class will delegate
    output to the Display class instead.

    Follows Single Responsibility Principle (SRP).
"""

from typing import Optional
from utils.constants import ROUNDS_TO_WIN, MAX_ROUNDS, SYMBOL_X, SYMBOL_O


class BestOfThree:
    """
    Tracks and evaluates the Best-of-Three match score.

    A match ends as soon as one player wins ROUNDS_TO_WIN (2) rounds,
    or when MAX_ROUNDS (3) rounds have been completed, whichever comes
    first.

    Usage example::

        score = BestOfThree("Alice", "Bob")

        score.record_round_result(SYMBOL_X)   # Alice wins round 1
        score.display_round_result(1, SYMBOL_X)
        score.display_score()

        score.record_round_result(SYMBOL_O)   # Bob wins round 2
        score.display_round_result(2, SYMBOL_O)
        score.display_score()

        if not score.is_match_over():
            score.record_round_result(SYMBOL_X)   # Alice wins round 3

        winner = score.get_match_winner()   # SYMBOL_X
    """

    def __init__(self, name_x: str, name_o: str) -> None:
        """
        Initialise the scoreboard.

        Args:
            name_x: Display name of the player using symbol X.
            name_o: Display name of the player using symbol O.
        """
        self._name_x: str = name_x
        self._name_o: str = name_o

        self._wins: dict[str, int] = {SYMBOL_X: 0, SYMBOL_O: 0}
        self._draws: int = 0
        self._rounds_played: int = 0

    # ------------------------------------------------------------------
    # Score mutation
    # ------------------------------------------------------------------

    def record_round_result(self, winner_symbol: Optional[str]) -> None:
        """
        Register the outcome of one completed round.

        Args:
            winner_symbol: SYMBOL_X if X won, SYMBOL_O if O won,
                           or None if the round ended in a draw.

        Raises:
            ValueError: If the match is already over.
            ValueError: If winner_symbol is not SYMBOL_X, SYMBOL_O, or None.
        """
        if self.is_match_over():
            raise ValueError(
                "Cannot record a result — the match is already over."
            )

        if winner_symbol not in {SYMBOL_X, SYMBOL_O, None}:
            raise ValueError(
                f"winner_symbol must be '{SYMBOL_X}', '{SYMBOL_O}', or None. "
                f"Got: {winner_symbol!r}"
            )

        self._rounds_played += 1

        if winner_symbol is None:
            self._draws += 1
        else:
            self._wins[winner_symbol] += 1

    # ------------------------------------------------------------------
    # State queries
    # ------------------------------------------------------------------

    def is_match_over(self) -> bool:
        """
        Return True if the match should end.

        The match ends when:
            - Any player has reached ROUNDS_TO_WIN victories, OR
            - MAX_ROUNDS rounds have been played.

        Returns:
            True  if the match is finished.
            False if more rounds should be played.
        """
        if any(wins >= ROUNDS_TO_WIN for wins in self._wins.values()):
            return True

        if self._rounds_played >= MAX_ROUNDS:
            return True

        return False

    def get_match_winner(self) -> Optional[str]:
        """
        Return the symbol of the match winner, or None if there is no
        winner yet (or the match ended in a tie after all draws).

        Returns:
            SYMBOL_X if X reached ROUNDS_TO_WIN wins.
            SYMBOL_O if O reached ROUNDS_TO_WIN wins.
            None     if no player has enough round wins (all draws, or
                     match still in progress).
        """
        for symbol, wins in self._wins.items():
            if wins >= ROUNDS_TO_WIN:
                return symbol
        return None

    def get_player_name(self, symbol: str) -> str:
        """
        Return the display name associated with a symbol.

        Args:
            symbol: SYMBOL_X or SYMBOL_O.

        Returns:
            The player's name string.

        Raises:
            ValueError: If symbol is not SYMBOL_X or SYMBOL_O.
        """
        if symbol == SYMBOL_X:
            return self._name_x
        if symbol == SYMBOL_O:
            return self._name_o
        raise ValueError(f"Unknown symbol: {symbol!r}")

    def get_wins(self, symbol: str) -> int:
        """
        Return the number of round wins for the given symbol.

        Args:
            symbol: SYMBOL_X or SYMBOL_O.

        Returns:
            Integer win count (0–MAX_ROUNDS).

        Raises:
            ValueError: If symbol is not SYMBOL_X or SYMBOL_O.
        """
        if symbol not in self._wins:
            raise ValueError(f"Unknown symbol: {symbol!r}")
        return self._wins[symbol]

    @property
    def rounds_played(self) -> int:
        """Return the number of completed rounds."""
        return self._rounds_played

    @property
    def draws(self) -> int:
        """Return the number of rounds that ended in a draw."""
        return self._draws

    @property
    def rounds_remaining(self) -> int:
        """Return how many more rounds could still be played."""
        return max(0, MAX_ROUNDS - self._rounds_played)

    # ------------------------------------------------------------------
    # Formatted summaries (display helpers)
    # ------------------------------------------------------------------

    def get_score_line(self) -> str:
        """
        Return a compact one-line score string.

        Returns:
            E.g. "Alice [X]: 1  |  Bob [O]: 0  |  Draws: 1"
        """
        return (
            f"{self._name_x} [X]: {self._wins[SYMBOL_X]}  |  "
            f"{self._name_o} [O]: {self._wins[SYMBOL_O]}  |  "
            f"Draws: {self._draws}"
        )

    def get_round_result_line(
        self, round_number: int, winner_symbol: Optional[str]
    ) -> str:
        """
        Return a formatted round-result string.

        Args:
            round_number  : The round that just finished (1, 2, or 3).
            winner_symbol : SYMBOL_X, SYMBOL_O, or None for a draw.

        Returns:
            E.g. "Round 2 Result: Alice [X] wins!"
                 "Round 3 Result: Draw — no winner."
        """
        if winner_symbol is None:
            outcome = "Draw — no winner."
        else:
            name = self.get_player_name(winner_symbol)
            outcome = f"{name} [{winner_symbol}] wins!"

        return f"Round {round_number} Result: {outcome}"

    def get_match_result_line(self) -> str:
        """
        Return a formatted match-result string for the final summary.

        Returns:
            E.g. "Match over! Alice [X] wins the Best of Three!"
                 "Match over! No winner — all rounds ended in a draw."
        """
        winner = self.get_match_winner()
        if winner:
            name = self.get_player_name(winner)
            return f"Match over! {name} [{winner}] wins the Best of Three!"
        return "Match over! No winner — all rounds ended in a draw."

    # ------------------------------------------------------------------
    # Direct console display (standalone use / testing)
    # ------------------------------------------------------------------

    def display_round_result(
        self, round_number: int, winner_symbol: Optional[str]
    ) -> None:
        """
        Print the result of the most recently completed round.

        Args:
            round_number : The round that just finished (1–3).
            winner_symbol: SYMBOL_X, SYMBOL_O, or None for a draw.
        """
        border = "=" * 45
        print(f"\n{border}")
        print(self.get_round_result_line(round_number, winner_symbol).center(45))
        print(f"{border}\n")

    def display_score(self) -> None:
        """
        Print the current running score (rounds won per player).
        """
        border = "-" * 45
        print(border)
        print("  SCORE".center(45))
        print(f"  {self.get_score_line()}")
        print(
            f"  Rounds played: {self._rounds_played} / {MAX_ROUNDS}  |  "
            f"Rounds remaining: {self.rounds_remaining}"
        )
        print(f"{border}\n")

    def display_match_result(self) -> None:
        """
        Print the final match outcome (call once when is_match_over() is True).
        """
        border = "=" * 45
        print(f"\n{border}")
        print(self.get_match_result_line().center(45))
        print(f"{border}\n")

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"BestOfThree("
            f"X={self._wins[SYMBOL_X]}, "
            f"O={self._wins[SYMBOL_O]}, "
            f"draws={self._draws}, "
            f"rounds={self._rounds_played})"
        )
