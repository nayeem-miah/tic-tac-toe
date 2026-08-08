"""
game_round.py
-------------
Responsibility:
    Controls one complete round of Tic-Tac-Toe from the first move to
    the last.

    Composes every independent module:
        Board         — grid state
        Player        — player identity & ability tracking
        TimedInputReader — timed stdin reads (Windows-compatible)
        InputValidator   — parse, range, occupancy checks
        WinChecker       — five-in-a-row detection
        DrawChecker      — full-board / no-winner detection
        DoubleTurnManager — activation keyword & eligibility

    Delegates ALL console output to Display.
    Returns the winning Player, or None for a draw.

    Follows Single Responsibility Principle (SRP).
    Follows Dependency Inversion Principle (DIP) — depends on class
    references, not on concrete I/O or global state.
"""

from typing import Optional

from game.board import Board
from game.player import Player
from game.timer import TimedInputReader
from game.win_checker import WinChecker
from game.draw_checker import DrawChecker
from game.double_turn import DoubleTurnManager
from ui.display import Display
from utils.input_validator import InputValidator
from utils.constants import MOVE_TIME_LIMIT


class GameRound:
    """
    Executes a single round of the 5×5 Tic-Tac-Toe game.

    A round ends when either:
        - A player places five marks in a row, column, or diagonal.
        - All 25 cells are occupied and neither player has won (draw).

    Usage::

        round_obj = GameRound(board, player_x, player_o, display, 1)
        winner = round_obj.play()   # Player or None
    """

    def __init__(
        self,
        board: Board,
        player_x: Player,
        player_o: Player,
        display: Display,
        round_number: int,
    ) -> None:
        """
        Initialise a round.

        Args:
            board       : Shared Board instance (reset at round start).
            player_x    : Player using symbol X.
            player_o    : Player using symbol O.
            display     : Display instance for all output.
            round_number: Which round this is (1, 2, or 3).
        """
        self._board = board
        self._player_x = player_x
        self._player_o = player_o
        self._display = display
        self._round_number = round_number
        self._reader = TimedInputReader(time_limit=MOVE_TIME_LIMIT)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def play(self) -> Optional[Player]:
        """
        Execute the round from start to finish.

        Resets the board, alternates turns between players, and returns
        as soon as a win or draw condition is met.

        Returns:
            The winning Player, or None if the round is a draw.
        """
        self._board.reset_board()
        self._display.show_round_start(self._round_number)
        self._display.render_board(self._board)

        current_player = self._player_x

        while True:
            is_over, winner = self._take_turn(current_player)
            if is_over:
                return winner
            current_player = self._get_other_player(current_player)

    # ------------------------------------------------------------------
    # Turn orchestration
    # ------------------------------------------------------------------

    def _take_turn(self, player: Player) -> tuple[bool, Optional[Player]]:
        """
        Handle one full turn for the given player.

        Reads a single input which may be:
            - A cell number → validate and place.
            - The keyword 'double' → activate Double Turn (2 moves).
            - Nothing (timeout) → skip the turn.

        Args:
            player: The currently active player.

        Returns:
            (True, winner_or_None) if the round ended.
            (False, None)          if the round continues.
        """
        try:
            self._display.show_turn_prompt(player, MOVE_TIME_LIMIT)
            raw = self._reader.read_input(prompt="")
        except KeyboardInterrupt:
            raise  # let main() handle Ctrl+C cleanly
        except Exception as exc:  # noqa: BLE001
            print(f"\n  [Error] Could not read input: {exc}")
            return False, None

        if raw is None:
            self._display.show_timeout(player)
            return False, None

        if DoubleTurnManager.is_activation_request(raw):
            return self._handle_double_turn_input(raw, player)

        return self._place_move(raw, player)

    def _handle_double_turn_input(
        self, raw: str, player: Player
    ) -> tuple[bool, Optional[Player]]:
        """
        Process a 'double' keyword from the player.

        If eligible, grants two consecutive moves.
        If ineligible, shows an error and skips the turn.

        Args:
            raw   : The raw 'double' string (passed to DoubleTurnManager).
            player: The currently active player.

        Returns:
            (True, winner_or_None) if the round ended after an extra move.
            (False, None)          if ineligible (turn skipped) or round continues.
        """
        result = DoubleTurnManager.try_activate(raw, player)

        if not result.activated:
            self._display.show_invalid_move(result.message)
            return False, None

        self._display.show_double_turn_activated(player)

        # First move of the double turn
        is_over, winner = self._execute_extra_move(player)
        if is_over:
            return True, winner

        # Second move of the double turn
        return self._execute_extra_move(player)

    def _execute_extra_move(
        self, player: Player
    ) -> tuple[bool, Optional[Player]]:
        """
        Prompt and execute one move as part of a Double Turn sequence.

        Args:
            player: The player making the extra move.

        Returns:
            (True, winner_or_None) if the round ended.
            (False, None)          if the round continues or timed out.
        """
        self._display.show_turn_prompt(player, MOVE_TIME_LIMIT)
        raw = self._reader.read_input(prompt="")

        if raw is None:
            self._display.show_timeout(player)
            return False, None

        return self._place_move(raw, player)

    # ------------------------------------------------------------------
    # Move placement
    # ------------------------------------------------------------------

    def _place_move(
        self, raw: str, player: Player
    ) -> tuple[bool, Optional[Player]]:
        """
        Validate raw input as a cell number and mark the board.

        On validation failure the turn is lost (one attempt per turn).
        On success the board is updated and the round-over condition is
        checked.

        Args:
            raw   : The raw string entered by the player.
            player: The currently active player.

        Returns:
            (True, winner_or_None) if the round ended after this move.
            (False, None)          if the round continues or input was invalid.
        """
        validation = InputValidator.validate_move(raw, self._board)

        if not validation:
            self._display.show_invalid_move(validation.error_message)
            return False, None

        try:
            self._board.update_cell(validation.value, player.symbol)
        except ValueError as exc:
            # Safety net: InputValidator should have caught this already.
            self._display.show_invalid_move(str(exc))
            return False, None

        self._display.render_board(self._board)

        return self._check_round_over(player)

    # ------------------------------------------------------------------
    # Round-over detection
    # ------------------------------------------------------------------

    def _check_round_over(
        self, last_player: Player
    ) -> tuple[bool, Optional[Player]]:
        """
        Determine whether the round has ended after a move was placed.

        Win is checked before draw: if the last move fills the board
        AND creates a winning line, it is a win, not a draw.

        Args:
            last_player: The player who just placed a mark.

        Returns:
            (True, last_player) if last_player won.
            (True, None)        if the board is full with no winner.
            (False, None)       if the round is still in progress.
        """
        if WinChecker.check_winner(self._board, last_player.symbol):
            self._display.show_round_winner(last_player)
            return True, last_player

        if DrawChecker.is_draw(self._board):
            self._display.show_round_draw()
            return True, None

        return False, None

    # ------------------------------------------------------------------
    # Player rotation
    # ------------------------------------------------------------------

    def _get_other_player(self, current: Player) -> Player:
        """
        Return the player who is NOT currently active.

        Args:
            current: The player who just finished their turn.

        Returns:
            player_o if current is player_x, else player_x.
        """
        return self._player_o if current == self._player_x else self._player_x
