"""
main.py
-------
Responsibility:
    Application entry point and Composition Root.

    Does exactly four things:
        1. Collect player names from stdin.
        2. Construct all top-level objects (Players, Display, Match).
        3. Run the match.
        4. Ask whether the players want to replay or exit.

    Contains NO game logic, NO board logic, NO display formatting.
    All game behaviour lives in the classes it composes.

    This thin entry point ports directly to C (main function) and
    C++ (main function with object construction).
"""

from game.player import Player
from game.match import Match
from ui.display import Display
from utils.constants import SYMBOL_X, SYMBOL_O


# ---------------------------------------------------------------------------
# Name collection
# ---------------------------------------------------------------------------

def _get_player_name(prompt: str) -> str:
    """
    Read a non-empty player name from stdin.

    Keeps asking until the user provides at least one non-whitespace
    character.

    Args:
        prompt: The text shown to the user.

    Returns:
        A stripped, non-empty name string.
    """
    while True:
        try:
            name = input(prompt).strip()
        except EOFError:
            # stdin closed (e.g. piped input ended) — propagate to caller
            raise
        if name:
            return name
        print("  Name cannot be empty. Please try again.")


def _collect_player_names() -> tuple[str, str]:
    """
    Ask both players for their display names.

    Returns:
        A (name_x, name_o) tuple.
    """
    print("\n  Enter player names")
    print("  " + "-" * 30)
    name_x = _get_player_name("  Player X — enter your name: ")
    name_o = _get_player_name("  Player O — enter your name: ")
    return name_x, name_o


# ---------------------------------------------------------------------------
# Replay prompt
# ---------------------------------------------------------------------------

def _ask_replay() -> bool:
    """
    Ask the players whether they want to play another match.

    Accepts 'y' or 'yes' (case-insensitive) as confirmation.
    Any other input is treated as 'no'.

    Returns:
        True  if the players want to replay.
        False if they want to exit.
    """
    try:
        answer = input("  Play again? (y/n): ").strip().lower()
        return answer in {"y", "yes"}
    except EOFError:
        # stdin closed — treat as 'no'
        return False


# ---------------------------------------------------------------------------
# Object construction
# ---------------------------------------------------------------------------

def _build_players(name_x: str, name_o: str) -> tuple[Player, Player]:
    """
    Construct both Player instances.

    Args:
        name_x: Name for the X player.
        name_o: Name for the O player.

    Returns:
        A (player_x, player_o) tuple.
    """
    player_x = Player(name=name_x, symbol=SYMBOL_X)
    player_o = Player(name=name_o, symbol=SYMBOL_O)
    return player_x, player_o


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Bootstrap and run one or more Best-of-Three matches.

    Lifecycle:
        1. Collect player names (once — names persist across rematches).
        2. Loop:
            a. Reset player match-state for a fresh match.
            b. Construct and run a Match.
            c. Prompt for replay or exit.
    """
    display = Display()

    # --- Setup phase ---------------------------------------------------
    try:
        name_x, name_o = _collect_player_names()
        player_x, player_o = _build_players(name_x, name_o)
    except (KeyboardInterrupt, EOFError):
        print("\n\n  Setup cancelled. Goodbye!\n")
        return

    # --- Match loop ----------------------------------------------------
    while True:
        # Reset per-match state (rounds won, Double Turn availability)
        player_x.reset_for_new_match()
        player_o.reset_for_new_match()

        try:
            match = Match(
                player_x=player_x,
                player_o=player_o,
                display=display,
            )
            match.run()

        except KeyboardInterrupt:
            print("\n\n  Match interrupted by user (Ctrl+C). Exiting...\n")
            return

        except Exception as exc:  # noqa: BLE001
            print(f"\n  [Error] An unexpected error occurred: {exc}")
            print("  The match has been terminated.\n")
            return

        # --- Replay prompt ---------------------------------------------
        if not _ask_replay():
            break

    print("\n  Exiting. Thanks for playing!\n")


if __name__ == "__main__":
    main()
