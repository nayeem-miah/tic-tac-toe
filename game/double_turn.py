"""
double_turn.py
--------------
Responsibility:
    Implements the Double Turn special ability as a self-contained
    feature module.

    Rules:
        - A player activates Double Turn by typing the keyword "double"
          instead of a cell number when prompted.
        - Each player may use Double Turn only once per match.
        - Once activated, the player receives two consecutive turns
          (the caller executes the extra turn; this module only manages
          eligibility and activation).
        - After use the ability is permanently consumed for that player
          in the current match (tracked on the Player instance).

    Provides:
        DoubleTurnResult   — immutable result container.
        DoubleTurnManager  — stateless manager (static methods only).

    Contains NO board logic, NO display logic, NO game-loop logic.
    Does NOT call input() — raw input is always passed in by the caller.
    Follows Single Responsibility Principle (SRP).
"""

from dataclasses import dataclass

# Keyword constant — change here to rename the activation command.
ACTIVATION_KEYWORD: str = "double"


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DoubleTurnResult:
    """
    Immutable outcome of a Double Turn activation attempt.

    Attributes:
        activated      : True if Double Turn was successfully activated.
        message        : Human-readable description of the outcome.
        is_keyword     : True if the raw input was the activation keyword
                         (regardless of whether activation succeeded).
    """

    activated: bool
    message: str
    is_keyword: bool

    def __bool__(self) -> bool:
        """Allow truth-testing: ``if result:`` ↔ result.activated."""
        return self.activated


# ---------------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------------

class DoubleTurnManager:
    """
    Stateless manager for the Double Turn special ability.

    All methods are static — this class holds no instance state.
    Player-level state (whether the ability has been used) lives
    exclusively on the Player instance.

    Usage example::

        raw = reader.read_input(prompt="Your move (or type 'double'): ")

        result = DoubleTurnManager.try_activate(raw, player)

        if result.is_keyword:
            display.show_message(result.message)
            if result.activated:
                # grant the extra turn in the game loop
            # do NOT also try to parse raw as a cell number
        else:
            # treat raw as a normal cell number input
    """

    # ------------------------------------------------------------------
    # Composite activation (primary public interface)
    # ------------------------------------------------------------------

    @staticmethod
    def try_activate(raw_input: str, player) -> DoubleTurnResult:
        """
        Check whether raw_input is the activation keyword and, if so,
        attempt to activate Double Turn for the given player.

        Steps:
            1. Strip and lower-case the input.
            2. If it is NOT the keyword → return a non-keyword result.
            3. If it IS the keyword but the player already used the
               ability → return a failed-activation result with a
               clear explanation.
            4. Otherwise activate the ability on the player and return
               a successful result.

        Args:
            raw_input: The raw string entered by the player (may be
                       anything — cell number, keyword, garbage).
            player   : A Player instance exposing double_turn_available
                       and use_double_turn().

        Returns:
            DoubleTurnResult with activated, message, and is_keyword set.
        """
        if not DoubleTurnManager.is_activation_request(raw_input):
            return DoubleTurnResult(
                activated=False,
                message="",
                is_keyword=False,
            )

        # Input is the keyword — check eligibility
        if not DoubleTurnManager.can_activate(player):
            return DoubleTurnResult(
                activated=False,
                message=(
                    f"{player.name} [{player.symbol}] has already used "
                    f"their Double Turn this match. "
                    f"Please enter a cell number (1–25)."
                ),
                is_keyword=True,
            )

        # Eligible — consume the ability on the player
        player.use_double_turn()

        return DoubleTurnResult(
            activated=True,
            message=(
                f"Double Turn activated! "
                f"{player.name} [{player.symbol}] gets two consecutive moves."
            ),
            is_keyword=True,
        )

    # ------------------------------------------------------------------
    # Individual checks
    # ------------------------------------------------------------------

    @staticmethod
    def is_activation_request(raw_input: str) -> bool:
        """
        Return True if raw_input is the Double Turn activation keyword.

        Comparison is case-insensitive and whitespace-tolerant so that
        "DOUBLE", "Double", and "  double  " all match.

        Args:
            raw_input: The raw string from the player.

        Returns:
            True  if the stripped, lower-cased input equals the keyword.
            False otherwise (including empty strings).

        Examples::

            is_activation_request("double")   →  True
            is_activation_request("DOUBLE")   →  True
            is_activation_request("  double") →  True
            is_activation_request("13")       →  False
            is_activation_request("")         →  False
        """
        return raw_input.strip().lower() == ACTIVATION_KEYWORD

    @staticmethod
    def can_activate(player) -> bool:
        """
        Return True if the player is still eligible to use Double Turn.

        Delegates the eligibility check to Player.double_turn_available
        so that state ownership stays on the Player.

        Args:
            player: A Player instance.

        Returns:
            True  if the player has not yet used their Double Turn.
            False if the ability has already been consumed.
        """
        return player.double_turn_available

