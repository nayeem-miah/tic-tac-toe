# Developer Documentation â€” Customized 5Ã—5 Tic-Tac-Toe

> **Language**: Python 3.10+  
> **Paradigm**: Object-Oriented Programming (OOP), Composition  
> **Design Principles**: SOLID, PEP 8, Clean Code  
> **Test Framework**: `unittest`

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Folder Structure](#2-folder-structure)
3. [Module Reference](#3-module-reference)
4. [Class Reference](#4-class-reference)
5. [Class Relationships](#5-class-relationships)
6. [Data Flow](#6-data-flow)
7. [Game Flow](#7-game-flow)

---

## 1. Project Overview

A two-player, console-based Tic-Tac-Toe game played on a **5Ã—5 grid**. A player wins a round by placing **5 marks in a row, column, or diagonal**. The full match is **Best of Three** â€” first to win 2 rounds wins the match.

### Special Features

| Feature | Description |
|---|---|
| **Double Turn** | Each player may type `"double"` once per match to receive two consecutive moves |
| **Move Timer** | Each move must be made within **15 seconds** or the turn is forfeited |
| **Best of Three** | Match ends when one player wins 2 rounds, or all 3 rounds have been played |

### Key Design Decisions

| Decision | Rationale |
|---|---|
| **Composition over inheritance** | Modules are composed in `GameRound` and `Match`; no class inherits from another |
| **Stateless checker classes** | `WinChecker`, `DrawChecker`, `InputValidator`, `DoubleTurnManager` hold no state â€” all logic lives in static methods |
| **Separation of I/O** | All console output routes through `Display`; game modules never call `print()` directly (except `BestOfThree`) |
| **Single Composition Root** | `main.py` is the only place where objects are constructed and wired together |
| **Threading for timed input** | Python's `input()` blocks on Windows; a daemon thread + `queue.Queue` pattern allows a real timeout |

---

## 2. Folder Structure

```
Tic Tac Toe/
â”‚
â”œâ”€â”€ main.py                    # Entry point & Composition Root
â”‚
â”œâ”€â”€ game/                      # Core game logic package
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ board.py               # 5Ã—5 grid state and cell access
â”‚   â”œâ”€â”€ player.py              # Player identity and per-match state
â”‚   â”œâ”€â”€ win_checker.py         # Five-in-a-row detection
â”‚   â”œâ”€â”€ draw_checker.py        # Full-board / no-winner draw detection
â”‚   â”œâ”€â”€ timer.py               # Countdown timer and timed stdin reader
â”‚   â”œâ”€â”€ double_turn.py         # Double Turn ability manager
â”‚   â”œâ”€â”€ best_of_three.py       # Score tracking and match-over logic
â”‚   â”œâ”€â”€ game_round.py          # Single-round turn loop (core composer)
â”‚   â””â”€â”€ match.py               # Best-of-Three match orchestrator
â”‚
â”œâ”€â”€ ui/                        # Presentation layer package
â”‚   â”œâ”€â”€ __init__.py
â”‚   â””â”€â”€ display.py             # All console output (View layer)
â”‚
â”œâ”€â”€ utils/                     # Shared utilities package
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ constants.py           # All magic values in one place
â”‚   â””â”€â”€ input_validator.py     # Input parsing and validation pipeline
â”‚
â””â”€â”€ tests/                     # Unit test package
    â”œâ”€â”€ __init__.py
    â”œâ”€â”€ test_board.py           # 26 Board tests
    â”œâ”€â”€ test_player.py          # 22 Player tests
    â”œâ”€â”€ test_win_checker.py     # 21 WinChecker tests
    â”œâ”€â”€ test_draw_checker.py    # 13 DrawChecker tests
    â”œâ”€â”€ test_timer.py           # 15 Timer tests
    â””â”€â”€ test_double_turn.py     # 25 DoubleTurnManager tests
```

### Package Dependency Map

```
main.py
  â”œâ”€â”€ game.player
  â”œâ”€â”€ game.match
  â”œâ”€â”€ ui.display
  â””â”€â”€ utils.constants

game.match
  â”œâ”€â”€ game.board
  â”œâ”€â”€ game.player
  â”œâ”€â”€ game.game_round
  â”œâ”€â”€ game.best_of_three
  â””â”€â”€ ui.display

game.game_round
  â”œâ”€â”€ game.board
  â”œâ”€â”€ game.player
  â”œâ”€â”€ game.timer
  â”œâ”€â”€ game.win_checker
  â”œâ”€â”€ game.draw_checker
  â”œâ”€â”€ game.double_turn
  â”œâ”€â”€ ui.display
  â””â”€â”€ utils.input_validator

game.draw_checker
  â””â”€â”€ game.win_checker        â† sibling dependency

utils.input_validator
  â””â”€â”€ utils.constants

ui.display
  â”œâ”€â”€ game.board
  â”œâ”€â”€ game.player
  â””â”€â”€ utils.constants
```

---

## 3. Module Reference

### `main.py` â€” Application Entry Point

**Responsibility**: Composition Root. Collects player names, constructs all top-level objects, runs the match loop, and handles replay.

**Contains**: Four pure functions (no classes).

| Function | Signature | Purpose |
|---|---|---|
| `main()` | `() â†’ None` | Bootstrap and match loop |
| `_collect_player_names()` | `() â†’ tuple[str, str]` | Read both player names from stdin |
| `_get_player_name()` | `(prompt: str) â†’ str` | Read a single non-empty name; loops until valid |
| `_ask_replay()` | `() â†’ bool` | Ask "Play again?" â€” returns True for y/yes |
| `_build_players()` | `(name_x, name_o) â†’ tuple[Player, Player]` | Construct both Player instances |

**Exception handling**:
- Setup phase: catches `KeyboardInterrupt` and `EOFError` â†’ prints cancellation message
- Match loop: catches `KeyboardInterrupt` â†’ clean exit; catches `Exception` â†’ error message + exit

---

### `utils/constants.py` â€” Shared Constants

Single source of truth for every magic value in the project.

| Constant | Type | Value | Used by |
|---|---|---|---|
| `BOARD_SIZE` | `int` | `5` | `Board`, `WinChecker`, `Display` |
| `TOTAL_CELLS` | `int` | `25` | `Board`, `InputValidator` |
| `WIN_LENGTH` | `int` | `5` | Documentation only (= `BOARD_SIZE`) |
| `SYMBOL_X` | `str` | `"X"` | `Player`, `BestOfThree`, `DrawChecker` |
| `SYMBOL_O` | `str` | `"O"` | `Player`, `BestOfThree`, `DrawChecker` |
| `EMPTY_CELL` | `str` | `" "` | Reserved; not currently used in logic |
| `MOVE_TIME_LIMIT` | `int` | `15` | `MoveTimer`, `TimedInputReader`, `Display` |
| `MAX_ROUNDS` | `int` | `3` | `BestOfThree` |
| `ROUNDS_TO_WIN` | `int` | `2` | `BestOfThree` |
| `MAX_DOUBLE_TURNS` | `int` | `1` | Documentation only |

---

### `utils/input_validator.py` â€” Input Validation Pipeline

**Responsibility**: Validate raw player input through three sequential layers before it touches the board. Contains `ValidationResult` dataclass and `InputValidator` class.

---

### `game/board.py` â€” Grid State Manager

**Responsibility**: Own and manage the 5Ã—5 grid. No I/O, no player logic, no win detection.

---

### `game/player.py` â€” Player State

**Responsibility**: Represent one human player's identity and per-match mutable state. No game logic.

---

### `game/win_checker.py` â€” Win Detection

**Responsibility**: Detect five-in-a-row in any direction. Stateless. Reads the grid snapshot only.

---

### `game/draw_checker.py` â€” Draw Detection

**Responsibility**: Detect a draw (board full + no winner). Delegates win checking to `WinChecker`.

---

### `game/timer.py` â€” Countdown Timer & Timed Input

**Responsibility**: Provide a reusable countdown timer (`MoveTimer`) and a safe timed stdin reader (`TimedInputReader`). No game logic.

---

### `game/double_turn.py` â€” Double Turn Ability

**Responsibility**: Manage keyword detection and activation eligibility for the Double Turn special ability. Contains `DoubleTurnResult` dataclass and `DoubleTurnManager` class.

---

### `game/best_of_three.py` â€” Match Score Tracker

**Responsibility**: Record round results, determine match-over conditions, and format score summaries.

---

### `game/game_round.py` â€” Single Round Controller

**Responsibility**: Execute one complete round turn-by-turn by composing all independent modules.

---

### `game/match.py` â€” Match Orchestrator

**Responsibility**: Drive the Best-of-Three match by creating and running `GameRound` instances, recording results in `BestOfThree`, and concluding the match.

---

### `ui/display.py` â€” View Layer

**Responsibility**: Produce all console output. Never mutates state. Never reads input.

---

## 4. Class Reference

### `ValidationResult` â€” `utils/input_validator.py`

Frozen dataclass. Immutable result container for a single validation outcome.

```python
@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    error_message: str
    value: int | None = None
```

| Member | Type | Description |
|---|---|---|
| `is_valid` | `bool` | `True` if the input passed the check |
| `error_message` | `str` | Human-readable reason for failure; `""` on success |
| `value` | `int \| None` | Parsed cell number on success; `None` on failure |
| `__bool__()` | `bool` | Returns `is_valid` â€” enables `if result:` pattern |

**Usage pattern**:
```python
result = InputValidator.validate_move(raw, board)
if not result:
    display.show_invalid_move(result.error_message)
else:
    board.update_cell(result.value, player.symbol)
```

---

### `InputValidator` â€” `utils/input_validator.py`

Stateless validator. All methods are `@staticmethod`. Never instantiated.

**Private factory helpers** (DRY, not part of public API):

| Method | Returns |
|---|---|
| `_ok(value: int)` | `ValidationResult(is_valid=True, value=value)` |
| `_fail(message: str)` | `ValidationResult(is_valid=False, error_message=message)` |

**Public validation pipeline**:

| Method | Input | Description |
|---|---|---|
| `validate_move(raw_input, board)` | `str, Board` | Composite: runs all 3 layers in sequence |
| `validate_integer(raw_input)` | `str` | Layer 1: can the string be parsed as `int`? |
| `validate_range(cell_number)` | `int` | Layer 2: is the integer within `[1, 25]`? |
| `validate_occupancy(cell_number, board)` | `int, Board` | Layer 3: is the cell still empty? |

**Pipeline short-circuits**: returns the first failure encountered; never proceeds past a failing layer.

---

### `Board` â€” `game/board.py`

Manages the 5Ã—5 grid. Internally uses a `list[list[str]]` â€” a 2D list of strings.

**Cell encoding**:
- **Empty cell**: stores its own 1-based number as a string (e.g., `"7"`)
- **Occupied cell**: stores the player's symbol (`"X"` or `"O"`)

**Class constant**:
```python
_ROW_SEP: str = "-" * (BOARD_SIZE * 6 - 1)   # shared by display_board() and __str__()
```

| Method | Signature | Description |
|---|---|---|
| `create_board()` | `() â†’ None` | Build the initial 5Ã—5 grid with number strings |
| `reset_board()` | `() â†’ None` | Alias for `create_board()` â€” clears the board for a new round |
| `display_board()` | `() â†’ None` | Print the grid to the console |
| `get_cell(cell_number)` | `(int) â†’ str` | Return cell content; raises `ValueError` if out of range |
| `is_cell_empty(cell_number)` | `(int) â†’ bool` | True if the cell still holds its number string |
| `update_cell(cell_number, symbol)` | `(int, str) â†’ None` | Place a symbol; raises `ValueError` if occupied or out of range |
| `get_grid()` | `() â†’ list[list[str]]` | Return a **shallow copy** of the grid (callers cannot mutate board state) |
| `_cell_to_row_col(cell_number)` | `(int) â†’ tuple[int, int]` | Convert 1-based cell number to (row, col) 0-based index pair |
| `_validate_cell_number(n)` | `(int) â†’ None` | Raise `ValueError` if `n âˆ‰ [1, 25]` |
| `_format_row(row)` | `(list[str]) â†’ str` | Format one grid row for display |

**Cell â†’ (row, col) formula**:
```
zero_based = cell_number - 1
row = zero_based // BOARD_SIZE
col = zero_based % BOARD_SIZE
```

**Cell layout**:
```
 1  |  2  |  3  |  4  |  5
---------------------------------
 6  |  7  |  8  |  9  | 10
---------------------------------
11  | 12  | 13  | 14  | 15
---------------------------------
16  | 17  | 18  | 19  | 20
---------------------------------
21  | 22  | 23  | 24  | 25
```

---

### `Player` â€” `game/player.py`

Represents one human player. Instances survive across all three rounds â€” only per-match state is reset.

**Private attributes**:

| Attribute | Type | Description |
|---|---|---|
| `_name` | `str` | Stripped display name |
| `_symbol` | `str` | Board token: `"X"` or `"O"` |
| `_rounds_won` | `int` | Round victories in the current match |
| `_double_turn_used` | `bool` | Whether the Double Turn ability has been consumed |

**Properties** (read-only):

| Property | Type | Description |
|---|---|---|
| `name` | `str` | Player's display name |
| `symbol` | `str` | Player's board token |
| `rounds_won` | `int` | Round victories |
| `double_turn_available` | `bool` | `True` if `_double_turn_used` is `False` |

**Mutators**:

| Method | Description |
|---|---|
| `increment_rounds_won()` | Add one round victory |
| `use_double_turn()` | Consume the ability; raises `ValueError` if already used |
| `reset_for_new_match()` | Reset `_rounds_won â†’ 0` and `_double_turn_used â†’ False` |

**Dunder methods**:

| Method | Behaviour |
|---|---|
| `__str__()` | `"Alice (X)"` |
| `__repr__()` | Full attribute dump for debugging |
| `__eq__(other)` | `True` if both players share the same `_symbol` |

> âš ï¸ `__eq__` compares symbols, not identity. `Player("Alice","X") == Player("Bob","X")` returns `True`.
> This is used exclusively in `GameRound._get_other_player()` for X/O rotation.

---

### `WinChecker` â€” `game/win_checker.py`

Stateless win evaluator. All methods are `@staticmethod`. Never instantiated.

Accepts any object with a `get_grid() â†’ list[list[str]]` interface (duck-typed, not tightly coupled to `Board`).

| Method | Signature | Description |
|---|---|---|
| `check_winner(board, symbol)` | `(Board, str) â†’ bool` | **Composite**: runs all 4 checks; short-circuits on first win |
| `check_rows(grid, symbol)` | `(list[list[str]], str) â†’ bool` | True if any full row belongs to `symbol` |
| `check_columns(grid, symbol)` | `(list[list[str]], str) â†’ bool` | True if any full column belongs to `symbol` |
| `check_main_diagonal(grid, symbol)` | `(list[list[str]], str) â†’ bool` | True if cells `(0,0)â†’(4,4)` all equal `symbol` |
| `check_anti_diagonal(grid, symbol)` | `(list[list[str]], str) â†’ bool` | True if cells `(0,4)â†’(4,0)` all equal `symbol` |

**Winning diagonals** on a 5Ã—5 grid:

```
Main:  (0,0) (1,1) (2,2) (3,3) (4,4)   â†’  cells 1, 7, 13, 19, 25
Anti:  (0,4) (1,3) (2,2) (3,1) (4,0)   â†’  cells 5, 9, 13, 17, 21
```

---

### `DrawChecker` â€” `game/draw_checker.py`

Stateless draw evaluator. All methods are `@staticmethod`. Never instantiated.

| Method | Signature | Description |
|---|---|---|
| `is_draw(board)` | `(Board) â†’ bool` | `True` iff board is full **and** neither symbol has won |
| `is_board_full(board)` | `(Board) â†’ bool` | `True` iff no cell contains a digit string |
| `count_empty_cells(board)` | `(Board) â†’ int` | Count of cells still holding digit strings (0â€“25) |

**Draw detection logic**:
```
is_draw(board):
    if not is_board_full(board): return False
    if WinChecker.check_winner(board, "X"): return False
    if WinChecker.check_winner(board, "O"): return False
    return True
```

**Empty cell detection**: a cell is empty if `cell_value.isdigit()` returns `True` (i.e., it still holds its own number string). Once marked `"X"` or `"O"`, `isdigit()` returns `False`.

---

### `MoveTimer` â€” `game/timer.py`

Thread-safe countdown timer backed by `threading.Event` and `threading.Timer`.

**Private attributes**:

| Attribute | Type | Description |
|---|---|---|
| `_time_limit` | `int` | Total seconds for the countdown |
| `_start_time` | `float \| None` | Monotonic timestamp from `start()` |
| `_expired_flag` | `threading.Event` | Set by `_on_timeout()` when the timer fires |
| `_timer_thread` | `threading.Timer \| None` | Internal daemon timer thread |

| Method | Description |
|---|---|
| `start()` | Begin countdown in a background daemon thread |
| `stop()` | Cancel the running countdown |
| `reset()` | Cancel + clear expired flag + reset start time |
| `is_expired()` | Thread-safe read of `_expired_flag.is_set()` |
| `remaining_seconds()` | Float, clamped to `â‰¥ 0.0`; full limit if not started |

**Lifecycle**:
```
Timer created â†’ start() â†’ [time passes] â†’ _on_timeout() sets flag
                        â†— OR â†’ stop() cancels the thread (no expiry)
```

---

### `TimedInputReader` â€” `game/timer.py`

Reads one line from stdin within a time window using a background daemon thread and `queue.Queue`.

**Why threading?** Python's `input()` blocks the calling thread indefinitely. On Windows, `select()` does not support stdin, so a separate thread is the only cross-platform solution.

> âš ï¸ **Known limitation**: If a timeout fires before the user presses Enter, the reader thread remains alive â€” blocked on `input()` â€” until the user types something on the next prompt. This is a Windows/Python platform constraint and does not cause data corruption.

**Private attributes**:

| Attribute | Type | Description |
|---|---|---|
| `_time_limit` | `int` | Seconds to wait before returning `None` |
| `_result_queue` | `queue.Queue[Optional[str]]` | Single-item thread-safe queue |

| Method | Description |
|---|---|
| `read_input(prompt)` | Start the reader thread; block on queue for `time_limit` seconds; return `str` or `None` (timeout) |
| `_read_from_stdin(prompt)` | Background thread target: calls `input()`, puts result in queue; handles `EOFError` and `Exception` |

---

### `DoubleTurnResult` â€” `game/double_turn.py`

Frozen dataclass. Immutable result from a `DoubleTurnManager.try_activate()` call.

```python
@dataclass(frozen=True)
class DoubleTurnResult:
    activated: bool      # True only if the ability was successfully consumed
    message: str         # Human-readable outcome description
    is_keyword: bool     # True if the raw input was the activation keyword
```

| Member | Description |
|---|---|
| `__bool__()` | Returns `activated` |

---

### `DoubleTurnManager` â€” `game/double_turn.py`

Stateless ability manager. All methods are `@staticmethod`. Never instantiated.

**Module-level constant**:
```python
ACTIVATION_KEYWORD: str = "double"
```

| Method | Signature | Description |
|---|---|---|
| `try_activate(raw_input, player)` | `(str, Player) â†’ DoubleTurnResult` | **Composite**: checks keyword â†’ checks eligibility â†’ activates |
| `is_activation_request(raw_input)` | `(str) â†’ bool` | Case-insensitive, whitespace-tolerant keyword match |
| `can_activate(player)` | `(Player) â†’ bool` | Returns `player.double_turn_available` |

**`try_activate` state machine**:

```
raw_input
  â”‚
  â”œâ”€ NOT keyword â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â†’ DoubleTurnResult(activated=False, is_keyword=False)
  â”‚
  â””â”€ IS keyword
       â”‚
       â”œâ”€ Player already used it â”€â”€â†’ DoubleTurnResult(activated=False, is_keyword=True, message=rejection)
       â”‚
       â””â”€ Player eligible
            â”‚
            â””â”€ player.use_double_turn()
                 â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â†’ DoubleTurnResult(activated=True, is_keyword=True, message=success)
```

---

### `BestOfThree` â€” `game/best_of_three.py`

Tracks score across up to three rounds and determines match-over conditions.

**Private attributes**:

| Attribute | Type | Description |
|---|---|---|
| `_name_x` | `str` | Display name of the X player |
| `_name_o` | `str` | Display name of the O player |
| `_wins` | `dict[str, int]` | `{SYMBOL_X: n, SYMBOL_O: n}` round win counts |
| `_draws` | `int` | Rounds that ended without a winner |
| `_rounds_played` | `int` | Total rounds completed |

| Method | Description |
|---|---|
| `record_round_result(winner_symbol)` | Record a round outcome (`None` = draw) |
| `is_match_over()` | `True` if any player reached `ROUNDS_TO_WIN` or `MAX_ROUNDS` played |
| `get_match_winner()` | Return the winning symbol, or `None` if no decisive winner |
| `display_round_result(n, symbol)` | Print the result of round `n` |
| `display_score()` | Print the current score tally |
| `display_match_result()` | Print the final match outcome |

---

### `GameRound` â€” `game/game_round.py`

Controls one complete round of the game by composing all independent modules.

**Constructor dependencies** (injected):

| Parameter | Type | Role |
|---|---|---|
| `board` | `Board` | Grid state (reset at round start) |
| `player_x` | `Player` | X symbol player |
| `player_o` | `Player` | O symbol player |
| `display` | `Display` | All output |
| `round_number` | `int` | Used for display banners |

**Own instance**:
- `_reader`: `TimedInputReader` â€” created once per round, reused for all turns

| Method | Return type | Description |
|---|---|---|
| `play()` | `Optional[Player]` | Execute the full round; return winner or `None` (draw) |
| `_take_turn(player)` | `tuple[bool, Optional[Player]]` | Read input and route to move or double-turn handler |
| `_handle_double_turn_input(raw, player)` | `tuple[bool, Optional[Player]]` | Process the `"double"` keyword: reject or grant 2 moves |
| `_execute_extra_move(player)` | `tuple[bool, Optional[Player]]` | One timed move within a double turn |
| `_place_move(raw, player)` | `tuple[bool, Optional[Player]]` | Validate â†’ mark board â†’ check round over |
| `_check_round_over(player)` | `tuple[bool, Optional[Player]]` | Run `WinChecker` then `DrawChecker` |
| `_get_other_player(current)` | `Player` | Return the player who is NOT currently active |

**Return convention** for `tuple[bool, Optional[Player]]`:

| Return value | Meaning |
|---|---|
| `(False, None)` | Round continues â€” player rotation proceeds |
| `(True, player)` | Round over â€” `player` won |
| `(True, None)` | Round over â€” draw |

---

### `Match` â€” `game/match.py`

Orchestrates a Best-of-Three match. Creates `GameRound` instances and manages the scoring lifecycle.

**Constructor dependencies** (injected):

| Parameter | Type | Role |
|---|---|---|
| `player_x` | `Player` | X symbol player |
| `player_o` | `Player` | O symbol player |
| `display` | `Display` | All output |

**Own instances**:
- `_board`: `Board` â€” created once, reset by `GameRound` between rounds
- `_score`: `BestOfThree` â€” score tracker initialised with player names

| Method | Description |
|---|---|
| `run()` | Drive rounds until `_score.is_match_over()`; return match winner or `None` |
| `_play_one_round(round_number)` | Construct and run a `GameRound`; return round winner |
| `_record_and_display_result(n, winner)` | Update `BestOfThree`; display round result and score |
| `_conclude_match()` | Announce the final result; return match winner |
| `_resolve_player(symbol)` | Map a symbol string back to the correct `Player` instance |

---

### `Display` â€” `ui/display.py`

Pure view class. All methods print to the console. No state mutation. No input reading.

**Module-level visual constants**:
```python
_WIDE    = 49          # banner width
_SEP_HEAVY = "=" * 49  # title borders
_SEP_LIGHT = "-" * 49  # section dividers
_SEP_STAR  = "*" * 49  # round result borders
```

| Method | Trigger |
|---|---|
| `render_board(board)` | After every move and at round start |
| `show_welcome()` | Once at match start |
| `show_round_start(n)` | Once at each round start |
| `show_turn_prompt(player, time)` | Before each input read |
| `show_invalid_move(reason)` | On `ValidationResult` failure or double-turn rejection |
| `show_timeout(player)` | When `TimedInputReader` returns `None` |
| `show_double_turn_activated(player)` | On successful double turn activation |
| `show_round_winner(player)` | When `WinChecker` returns `True` |
| `show_round_draw()` | When `DrawChecker.is_draw()` returns `True` |
| `show_match_winner(player)` | When `BestOfThree.get_match_winner()` is not `None` |
| `show_scoreboard(player_x, player_o)` | Available for score display (defined, not yet called from Match) |
| `show_goodbye()` | At match end |

---

## 5. Class Relationships

### Composition Hierarchy

```
main.py  (Composition Root)
â”‚
â”œâ”€â”€ constructs: Player Ã— 2
â”œâ”€â”€ constructs: Display
â””â”€â”€ constructs: Match
                  â”‚
                  â”œâ”€â”€ owns: Board (shared across rounds)
                  â”œâ”€â”€ owns: BestOfThree (score state)
                  â”œâ”€â”€ holds refs: Player Ã— 2, Display
                  â””â”€â”€ creates per round: GameRound
                                            â”‚
                                            â”œâ”€â”€ holds refs: Board, Player Ã— 2, Display
                                            â”œâ”€â”€ creates: TimedInputReader (per round)
                                            â””â”€â”€ calls stateless: WinChecker
                                                                  DrawChecker
                                                                  InputValidator
                                                                  DoubleTurnManager
```

### Dependency Graph (arrows = "depends on")

```
main.py â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–º Player
           â”‚                â–º  Display
           â”‚                â–º  Match
           â”‚
Match â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–º Board
           â”‚                â–º  BestOfThree
           â”‚                â–º  GameRound
           â”‚
GameRound â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–º Board
           â”‚                â–º  Player
           â”‚                â–º  TimedInputReader
           â”‚                â–º  WinChecker
           â”‚                â–º  DrawChecker
           â”‚                â–º  DoubleTurnManager
           â”‚                â–º  Display
           â”‚                â–º  InputValidator
           â”‚
DrawChecker â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–º WinChecker

Display â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–º Board
                                â–º  Player
```

### Ownership vs. Reference

| Object | Owned by | References held by |
|---|---|---|
| `Board` | `Match` | `GameRound`, `Display` |
| `Player Ã— 2` | `main.py` | `Match`, `GameRound`, `Display`, `BestOfThree` (names only) |
| `Display` | `main.py` | `Match`, `GameRound` |
| `BestOfThree` | `Match` | â€” |
| `TimedInputReader` | `GameRound` | â€” |

---

## 6. Data Flow

### 6.1 Input Validation Pipeline

```
Player types a string
        â”‚
        â–¼
TimedInputReader.read_input()
        â”‚ returns raw: str | None
        â–¼
   [None?] â”€â”€YESâ”€â”€â–º Display.show_timeout() â†’ turn skipped
        â”‚
        NO
        â–¼
DoubleTurnManager.is_activation_request(raw)
        â”‚
   [YES?] â”€â”€â”€â”€â”€â”€â–º DoubleTurnManager.try_activate(raw, player)
        â”‚                 â”‚
        â”‚            [activated?] â”€â”€YESâ”€â”€â–º grant 2 moves
        â”‚                 â”‚
        â”‚                 NO
        â”‚                 â–¼
        â”‚          Display.show_invalid_move() â†’ turn skipped
        â”‚
        NO
        â–¼
InputValidator.validate_move(raw, board)
        â”‚
   [invalid?] â”€â”€YESâ”€â”€â–º Display.show_invalid_move() â†’ turn skipped
        â”‚
        NO
        â–¼
Board.update_cell(result.value, player.symbol)
        â”‚
        â–¼
Display.render_board(board)
        â”‚
        â–¼
WinChecker.check_winner(board, symbol)
        â”‚
   [YES?] â”€â”€â”€â”€â”€â”€â–º Display.show_round_winner() â†’ round ends
        â”‚
        NO
        â–¼
DrawChecker.is_draw(board)
        â”‚
   [YES?] â”€â”€â”€â”€â”€â”€â–º Display.show_round_draw() â†’ round ends
        â”‚
        NO
        â–¼
  Continue to next player's turn
```

### 6.2 Round Result Data Flow

```
GameRound.play() returns Optional[Player]
        â”‚
        â–¼
Match._record_and_display_result(round_number, winner)
        â”‚
        â”œâ”€â”€ BestOfThree.record_round_result(winner.symbol | None)
        â”‚           â”‚
        â”‚           â””â”€â”€ updates _wins / _draws / _rounds_played
        â”‚
        â”œâ”€â”€ BestOfThree.display_round_result()
        â””â”€â”€ BestOfThree.display_score()
        â”‚
        â–¼
BestOfThree.is_match_over() â”€â”€ checked by Match.run() loop condition
        â”‚
  [YES?] â”€â”€â”€â”€â”€â”€â–º Match._conclude_match()
                        â”‚
                        â”œâ”€â”€ BestOfThree.get_match_winner() â†’ symbol | None
                        â”œâ”€â”€ Match._resolve_player(symbol) â†’ Player | None
                        â”œâ”€â”€ Display.show_match_winner(player)
                        â”œâ”€â”€ BestOfThree.display_match_result()
                        â””â”€â”€ Display.show_goodbye()
```

### 6.3 Double Turn Data Flow

```
Player types "double"
        â”‚
        â–¼
GameRound._take_turn()
  DoubleTurnManager.is_activation_request("double") â†’ True
        â”‚
        â–¼
GameRound._handle_double_turn_input(raw, player)
  DoubleTurnManager.try_activate("double", player)
        â”‚
   [not activated?] â”€â”€â–º Display.show_invalid_move() â†’ return (False, None)
        â”‚
   [activated]
        â”‚
        â–¼
Display.show_double_turn_activated(player)
        â”‚
        â–¼
GameRound._execute_extra_move(player)   â† Move 1
        â”‚
   [round over?] â”€â”€YESâ”€â”€â–º return (True, winner)
        â”‚
        NO
        â–¼
GameRound._execute_extra_move(player)   â† Move 2
        â”‚
        â–¼
return result
```

---

## 7. Game Flow

### 7.1 High-Level Lifecycle

```
Application Start
       â”‚
       â–¼
main() collects player names â†’ creates Player Ã— 2, Display
       â”‚
       â–¼
       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
       â”‚  Match Loop (until "No" to replay)                  â”‚
       â”‚                                                     â”‚
       â”‚  player_x.reset_for_new_match()                    â”‚
       â”‚  player_o.reset_for_new_match()                    â”‚
       â”‚  Match(player_x, player_o, display)                â”‚
       â”‚  Match.run()                                        â”‚
       â”‚       â”‚                                             â”‚
       â”‚       â””â”€â”€ see Match Lifecycle below                 â”‚
       â”‚                                                     â”‚
       â”‚  _ask_replay() â”€â”€NOâ”€â”€â–º break                       â”‚
       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
       â”‚
       â–¼
"Exiting. Thanks for playing!"
```

### 7.2 Match Lifecycle

```
Match.run()
       â”‚
       â–¼
Display.show_welcome()
       â”‚
       â–¼
       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
       â”‚  Round Loop (while not BestOfThree.is_match_over()) â”‚
       â”‚                                                     â”‚
       â”‚  round_number += 1                                  â”‚
       â”‚  GameRound(board, px, po, display, n).play()        â”‚
       â”‚       â”‚                                             â”‚
       â”‚       â””â”€â”€ returns Optional[Player]                  â”‚
       â”‚                                                     â”‚
       â”‚  BestOfThree.record_round_result(winner.symbol)     â”‚
       â”‚  Display round result + score                       â”‚
       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
       â”‚
       â–¼
Match._conclude_match()
  â†’ show_match_winner / show_goodbye
  â†’ return match winner | None
```

### 7.3 Round Lifecycle

```
GameRound.play()
       â”‚
       â–¼
Board.reset_board()
Display.show_round_start(n)
Display.render_board(board)
current_player = player_x
       â”‚
       â–¼
       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
       â”‚  Turn Loop (infinite â€” exits only on round over)    â”‚
       â”‚                                                     â”‚
       â”‚  is_over, winner = _take_turn(current_player)       â”‚
       â”‚                                                     â”‚
       â”‚  if is_over: return winner                          â”‚
       â”‚                                                     â”‚
       â”‚  current_player = _get_other_player(current_player) â”‚
       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### 7.4 Turn Lifecycle

```
_take_turn(player)
       â”‚
       â–¼
Display.show_turn_prompt(player, 15)
TimedInputReader.read_input("")   â† blocks up to 15 s
       â”‚
       â”œâ”€â”€ None (timeout) â”€â”€â–º show_timeout() â†’ return (False, None)
       â”‚
       â”œâ”€â”€ "double" â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
       â”‚                                          â–¼
       â”‚              _handle_double_turn_input() â”‚
       â”‚                                          â”‚
       â”‚  try_activate() â†’ not activated          â”‚
       â”‚          â””â”€â”€â–º show_invalid_move()        â”‚
       â”‚                return (False, None)      â”‚
       â”‚                                          â”‚
       â”‚  try_activate() â†’ activated              â”‚
       â”‚          â””â”€â”€â–º show_double_turn_activated â”‚
       â”‚               _execute_extra_move()  Ã—2  â”‚
       â”‚               return round result        â”‚
       â”‚                                          â”‚
       â””â”€â”€ cell number â—„â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                  â”‚
                  â–¼
       _place_move(raw, player)
                  â”‚
                  â”œâ”€â”€ invalid â”€â”€â–º show_invalid_move() â†’ (False, None)
                  â”‚
                  â””â”€â”€ valid
                         â”‚
                         â–¼
                  Board.update_cell(n, symbol)
                  Display.render_board(board)
                  _check_round_over(player)
                         â”‚
                         â”œâ”€â”€ WinChecker â†’ True â”€â”€â–º show_round_winner() â†’ (True, player)
                         â”œâ”€â”€ DrawChecker â†’ True â”€â–º show_round_draw()   â†’ (True, None)
                         â””â”€â”€ neither              â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â†’ (False, None)
```

### 7.5 Player Turn Alternation

```
Round starts: current = player_x

Turn 1:  player_x   moves  â†’  current = player_o
Turn 2:  player_o   moves  â†’  current = player_x
Turn 3:  player_x   moves  â†’  current = player_o
  ...

Double Turn activated by player_x at turn N:
  Turn N+0:  player_x   move 1  (extra)
  Turn N+1:  player_x   move 2  (extra)
  Turn N+2:  player_o   resumes normal rotation
```

---

## Appendix â€” Running the Tests

```bash
# With pytest (recommended)
python -m pytest tests/ -v

# With unittest (no external dependency)
python -m unittest discover -s tests -v

# Run a single test file
python -m unittest tests.test_board -v
```

### Test coverage by module

| Module | Test file | Test methods |
|---|---|---|
| `Board` | `test_board.py` | 26 |
| `Player` | `test_player.py` | 22 |
| `WinChecker` | `test_win_checker.py` | 21 |
| `DrawChecker` | `test_draw_checker.py` | 13 |
| `MoveTimer` / `TimedInputReader` | `test_timer.py` | 15 |
| `DoubleTurnManager` | `test_double_turn.py` | 25 |
| **Total** | | **122** |

---

## Appendix â€” Key Constants Quick Reference

| Constant | Value | Where to change |
|---|---|---|
| Board size | `5 Ã— 5` | `BOARD_SIZE` in `constants.py` |
| Win length | `5 in a row` | `WIN_LENGTH` in `constants.py` |
| Time limit | `15 seconds` | `MOVE_TIME_LIMIT` in `constants.py` |
| Rounds to win | `2` | `ROUNDS_TO_WIN` in `constants.py` |
| Max rounds | `3` | `MAX_ROUNDS` in `constants.py` |
| Activation word | `"double"` | `ACTIVATION_KEYWORD` in `double_turn.py` |
