"""
match.py
--------
Responsibility:
    Manages the Best-of-Three match lifecycle.

    Composes:
        Board         — created once, reset by GameRound between rounds
        BestOfThree   — score tracking, match-over logic, result display
        GameRound     — executes each individual round
        Display       — all console output

    Drives rounds until BestOfThree.is_match_over() returns True.
    Returns the match winner (Player) or None if all rounds drew.

    Contains NO board logic, NO turn logic, NO input reading.
    Follows Single Responsibility Principle (SRP).
"""

from typing import Optional

from game.board import Board
from game.player import Player
from game.game_round import GameRound
from game.best_of_three import BestOfThree
from ui.display import Display
from utils.constants import SYMBOL_X, SYMBOL_O


class Match:
    """
    Orchestrates a Best-of-Three Tic-Tac-Toe match.

    Usage::

        match = Match(player_x, player_o, display)
        champion = match.run()
    """

    def __init__(
        self,
        player_x: Player,
        player_o: Player,
        display: Display,
    ) -> None:
        """
        Initialise a match.

        Creates the shared Board and the BestOfThree score tracker.
        Both players must already be constructed before passing here.

        Args:
            player_x: The player assigned symbol X.
            player_o: The player assigned symbol O.
            display : The shared Display instance for all output.
        """
        self._player_x = player_x
        self._player_o = player_o
        self._display = display
        self._board = Board()
        self._score = BestOfThree(player_x.name, player_o.name)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(self) -> Optional[Player]:
        """
        Execute the full Best-of-Three match.

        Plays rounds in sequence until:
            - A player accumulates ROUNDS_TO_WIN (2) round victories, or
            - MAX_ROUNDS (3) rounds have been completed.

        Returns:
            The winning Player, or None if the match produced no winner
            (all rounds ended in a draw).
        """
        self._display.show_welcome()

        round_number = 0

        while not self._score.is_match_over():
            round_number += 1
            try:
                winner = self._play_one_round(round_number)
            except KeyboardInterrupt:
                raise  # let main() handle Ctrl+C
            except Exception as exc:  # noqa: BLE001
                print(
                    f"\n  [Error] Round {round_number} ended unexpectedly: {exc}"
                    "\n  Counting the round as a draw."
                )
                winner = None
            self._record_and_display_result(round_number, winner)

        return self._conclude_match()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _play_one_round(self, round_number: int) -> Optional[Player]:
        """
        Construct and execute a single GameRound.

        Args:
            round_number: The 1-based round number (1, 2, or 3).

        Returns:
            The winning Player, or None for a draw.
        """
        game_round = GameRound(
            board=self._board,
            player_x=self._player_x,
            player_o=self._player_o,
            display=self._display,
            round_number=round_number,
        )
        return game_round.play()

    def _record_and_display_result(
        self, round_number: int, winner: Optional[Player]
    ) -> None:
        """
        Update the score and print the round result plus running tally.

        Args:
            round_number: The round that just finished.
            winner      : Winning Player, or None for a draw.
        """
        winner_symbol = winner.symbol if winner is not None else None
        self._score.record_round_result(winner_symbol)
        self._score.display_round_result(round_number, winner_symbol)
        self._score.display_score()

    def _conclude_match(self) -> Optional[Player]:
        """
        Print the final match outcome and return the match winner.

        Called once after the main loop exits.

        Returns:
            The winning Player, or None if no one won the match.
        """
        winner_symbol = self._score.get_match_winner()

        if winner_symbol is not None:
            match_winner = self._resolve_player(winner_symbol)
            self._display.show_match_winner(match_winner)
        else:
            # All rounds drew — no overall match winner
            pass

        self._score.display_match_result()
        self._display.show_goodbye()

        return self._resolve_player(winner_symbol) if winner_symbol else None

    def _resolve_player(self, symbol: str) -> Player:
        """
        Return the Player instance that corresponds to the given symbol.

        Args:
            symbol: SYMBOL_X or SYMBOL_O.

        Returns:
            The matching Player instance.
        """
        return self._player_x if symbol == SYMBOL_X else self._player_o
