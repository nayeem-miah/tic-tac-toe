"""
player.py
---------
Responsibility:
    Represents a single human player.
    Owns only player-specific state and behaviour:
        - name and symbol (X or O)
        - rounds won across the current match
        - the single-use Double Turn ability flag

    Contains NO board logic, NO timing logic, NO display logic,
    NO input logic, NO win-detection logic.
    Follows Single Responsibility Principle (SRP).
"""

from utils.constants import SYMBOL_X, SYMBOL_O


class Player:
    """
    Encapsulates a player's identity and per-match state.

    A Player instance survives the full Best-of-Three match; only the
    board is reset between rounds.  Per-match state (rounds won,
    Double Turn used) is reset explicitly via reset_for_new_match().

    Attributes (private, accessed via properties):
        _name              : Human-readable player name.
        _symbol            : Board token, "X" or "O".
        _rounds_won        : Number of rounds won in the current match.
        _double_turn_used  : Whether the Double Turn ability has been consumed.
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(self, name: str, symbol: str) -> None:
        """
        Initialise a player.

        Args:
            name  : Human-readable player name (e.g. "Alice").
            symbol: Board token — must be SYMBOL_X ("X") or SYMBOL_O ("O").

        Raises:
            ValueError: If name is empty or symbol is not "X" / "O".
        """
        self._validate_name(name)
        self._validate_symbol(symbol)

        self._name: str = name.strip()
        self._symbol: str = symbol
        self._rounds_won: int = 0
        self._double_turn_used: bool = False

    # ------------------------------------------------------------------
    # Properties (read-only public interface)
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        """Return the player's display name."""
        return self._name

    @property
    def symbol(self) -> str:
        """Return the player's board token ("X" or "O")."""
        return self._symbol

    @property
    def rounds_won(self) -> int:
        """Return how many rounds this player has won in the current match."""
        return self._rounds_won

    @property
    def double_turn_available(self) -> bool:
        """
        Return True if the player has NOT yet used their Double Turn.

        Each player may activate Double Turn exactly once per match
        (controlled by MAX_DOUBLE_TURNS = 1).
        """
        return not self._double_turn_used

    # ------------------------------------------------------------------
    # Mutators (state changes with guard conditions)
    # ------------------------------------------------------------------

    def increment_rounds_won(self) -> None:
        """
        Credit this player with one round victory.

        Called by Match after a GameRound ends with this player as winner.
        """
        self._rounds_won += 1

    def use_double_turn(self) -> None:
        """
        Consume the Double Turn ability.

        Marks the ability as used so it cannot be activated again
        within the same match.

        Raises:
            ValueError: If the ability has already been used this match.
        """
        if self._double_turn_used:
            raise ValueError(
                f"{self._name} has already used their Double Turn this match."
            )
        self._double_turn_used = True

    def reset_for_new_match(self) -> None:
        """
        Reset all per-match state so this player can compete in a rematch.

        Resets:
            - rounds_won        → 0
            - double_turn_used  → False

        Does NOT change name or symbol (those are permanent).
        """
        self._rounds_won = 0
        self._double_turn_used = False

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def get_status_summary(self) -> str:
        """
        Return a single-line summary of the player's current match state.

        Useful for scoreboards and debugging without coupling to Display.

        Returns:
            E.g. "Alice [X] | Rounds won: 1 | Double Turn: available"
        """
        double_turn_status = (
            "available" if self.double_turn_available else "used"
        )
        return (
            f"{self._name} [{self._symbol}] | "
            f"Rounds won: {self._rounds_won} | "
            f"Double Turn: {double_turn_status}"
        )

    # ------------------------------------------------------------------
    # Private validators
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_name(name: str) -> None:
        """
        Raise ValueError if name is not a non-empty string.

        Args:
            name: The candidate name to validate.

        Raises:
            ValueError: If name is empty or whitespace-only.
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError(
                "Player name must be a non-empty string."
            )

    @staticmethod
    def _validate_symbol(symbol: str) -> None:
        """
        Raise ValueError if symbol is not SYMBOL_X or SYMBOL_O.

        Args:
            symbol: The candidate symbol to validate.

        Raises:
            ValueError: If symbol is not "X" or "O".
        """
        valid_symbols = {SYMBOL_X, SYMBOL_O}
        if symbol not in valid_symbols:
            raise ValueError(
                f"Player symbol must be one of {valid_symbols}, "
                f"got '{symbol}'."
            )

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """Return a concise human-readable description of the player."""
        return f"{self._name} ({self._symbol})"

    def __repr__(self) -> str:
        return (
            f"Player(name={self._name!r}, symbol={self._symbol!r}, "
            f"rounds_won={self._rounds_won}, "
            f"double_turn_used={self._double_turn_used})"
        )

    def __eq__(self, other: object) -> bool:
        """
        Two players are equal if they share the same symbol.

        This allows simple identity checks like:
            if last_mover == current_player:
        """
        if not isinstance(other, Player):
            return NotImplemented
        return self._symbol == other._symbol
