"""
display.py
----------
Responsibility:
    Handles ALL console output for the game (View layer).

    Every message the player sees is produced here.
    No logic other than formatting and printing.
    Does not read input. Does not mutate state.

    Follows Single Responsibility Principle (SRP).
    Follows Open/Closed Principle (OCP) — new message types are
    added as new methods without changing existing ones.
"""

from game.board import Board
from game.player import Player
from utils.constants import BOARD_SIZE, MOVE_TIME_LIMIT


# Visual constants — change here to restyle all output at once.
_WIDE = 49
_SEP_HEAVY = "=" * _WIDE
_SEP_LIGHT = "-" * _WIDE
_SEP_STAR  = "*" * _WIDE


class Display:
    """Renders all game output to the console."""

    # ------------------------------------------------------------------
    # Board rendering
    # ------------------------------------------------------------------

    def render_board(self, board: Board) -> None:
        """
        Print the current 5x5 grid state.

        Delegates to Board.display_board() so grid-formatting
        logic lives in one place.

        Args:
            board: The Board instance to render.
        """
        print()
        board.display_board()
        print()

    # ------------------------------------------------------------------
    # Game-flow messages
    # ------------------------------------------------------------------

    def show_welcome(self) -> None:
        """Print the welcome / title banner at match start."""
        print()
        print(_SEP_HEAVY)
        print("  CUSTOMIZED 5×5 TIC-TAC-TOE".center(_WIDE))
        print("  Best of Three Match".center(_WIDE))
        print("  Win by placing 5 in a row, column, or diagonal".center(_WIDE))
        print(_SEP_HEAVY)
        print()

    def show_round_start(self, round_number: int) -> None:
        """
        Announce the start of a new round.

        Args:
            round_number: 1, 2, or 3.
        """
        print()
        print(_SEP_HEAVY)
        print(f"  ROUND {round_number}  —  BEGIN!".center(_WIDE))
        print(_SEP_HEAVY)
        print()

    def show_turn_prompt(self, player: Player, time_limit: int) -> None:
        """
        Print the move prompt for the active player.

        Includes a Double Turn hint if the ability is still available.

        Args:
            player    : The player whose turn it is.
            time_limit: Seconds available for this move.
        """
        print(_SEP_LIGHT)
        print(f"  {player.name} [{player.symbol}]  |  {time_limit}s to move")

        if player.double_turn_available:
            print("  Tip: type 'double' to activate your Double Turn (once per match)")

        print(f"  Enter cell number (1–25): ", end="", flush=True)

    def show_invalid_move(self, reason: str) -> None:
        """
        Inform the player their input was rejected.

        Args:
            reason: A short human-readable explanation.
        """
        print(f"\n  [!] Invalid: {reason}")

    def show_timeout(self, player: Player) -> None:
        """
        Inform everyone that the active player ran out of time.

        Args:
            player: The player whose turn timed out.
        """
        print(f"\n  [⏰] Time's up! {player.name} [{player.symbol}]'s turn is skipped.")

    def show_double_turn_prompt(self, player: Player) -> None:
        """
        Display context before asking for the first move of a double turn.

        Args:
            player: The player who just activated Double Turn.
        """
        print(f"\n  Enter your first move: ", end="", flush=True)

    def show_double_turn_activated(self, player: Player) -> None:
        """
        Announce that Double Turn has been activated.

        Args:
            player: The player who activated it.
        """
        print()
        print(_SEP_LIGHT)
        print(f"  ★ Double Turn activated — {player.name} [{player.symbol}] gets 2 moves!".center(_WIDE))
        print(_SEP_LIGHT)

    # ------------------------------------------------------------------
    # Round outcome messages
    # ------------------------------------------------------------------

    def show_round_winner(self, player: Player) -> None:
        """
        Announce that a player has won the current round.

        Args:
            player: The winning player.
        """
        print()
        print(_SEP_STAR)
        print(f"  ✓ {player.name} [{player.symbol}] wins the round!".center(_WIDE))
        print(_SEP_STAR)

    def show_round_draw(self) -> None:
        """Announce that the current round ended in a draw."""
        print()
        print(_SEP_STAR)
        print("  This round is a DRAW — no winner.".center(_WIDE))
        print(_SEP_STAR)

    # ------------------------------------------------------------------
    # Match outcome messages
    # ------------------------------------------------------------------

    def show_match_winner(self, player: Player) -> None:
        """
        Announce the Best-of-Three match winner.

        Args:
            player: The player who won the match.
        """
        print()
        print(_SEP_HEAVY)
        print(f"  🏆  {player.name} [{player.symbol}] wins the Best of Three!".center(_WIDE))
        print(_SEP_HEAVY)
        print()

    def show_scoreboard(self, player_x: Player, player_o: Player) -> None:
        """
        Print the current round-win tally for both players.

        Args:
            player_x: The player using symbol X.
            player_o: The player using symbol O.
        """
        print()
        print(_SEP_LIGHT)
        print("  SCOREBOARD".center(_WIDE))
        print(f"  {player_x.name} [X]: {player_x.rounds_won} round(s) won")
        print(f"  {player_o.name} [O]: {player_o.rounds_won} round(s) won")
        print(_SEP_LIGHT)

    def show_goodbye(self) -> None:
        """Print a closing message when the match ends."""
        print()
        print(_SEP_HEAVY)
        print("  Thank you for playing! Goodbye.".center(_WIDE))
        print(_SEP_HEAVY)
        print()
