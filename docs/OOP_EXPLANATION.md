# Object-Oriented Programming in the 5×5 Tic-Tac-Toe Project

> This document explains how the project applies the core principles of
> Object-Oriented Programming (OOP). Every example references real code
> that exists in the project.

---

## Table of Contents

1. [Class](#1-class)
2. [Object](#2-object)
3. [Encapsulation](#3-encapsulation)
4. [Abstraction](#4-abstraction)
5. [Composition](#5-composition)
6. [Reusability](#6-reusability)
7. [Maintainability](#7-maintainability)

---

## 1. Class

### Definition

A **class** is a blueprint that defines the structure (attributes) and behaviour
(methods) of a concept in the program. It does not hold data by itself — it
only describes what data and behaviour an instance of that concept will have.

### How this project uses classes

Every meaningful concept in the game is modelled as its own class. Each class
has a single, clearly stated responsibility.

| Class | File | Responsibility |
|---|---|---|
| `Board` | `game/board.py` | Owns and manages the 5×5 grid |
| `Player` | `game/player.py` | Represents a human player's identity and match state |
| `WinChecker` | `game/win_checker.py` | Detects a five-in-a-row winning line |
| `DrawChecker` | `game/draw_checker.py` | Detects a full-board draw |
| `MoveTimer` | `game/timer.py` | Counts down 15 seconds for a move |
| `TimedInputReader` | `game/timer.py` | Reads stdin within a time limit |
| `DoubleTurnManager` | `game/double_turn.py` | Manages the Double Turn special ability |
| `BestOfThree` | `game/best_of_three.py` | Tracks the match score |
| `InputValidator` | `utils/input_validator.py` | Validates player input |
| `GameRound` | `game/game_round.py` | Controls one complete round |
| `Match` | `game/match.py` | Orchestrates the Best-of-Three match |
| `Display` | `ui/display.py` | Produces all console output |

### Example — the `Board` class

```python
# game/board.py

class Board:
    """Manages the 5x5 Tic-Tac-Toe grid."""

    _ROW_SEP: str = "-" * (BOARD_SIZE * 6 - 1)

    def __init__(self) -> None:
        self._grid: list[list[str]] = []
        self.create_board()

    def create_board(self) -> None:
        self._grid = [
            [str(row * BOARD_SIZE + col + 1) for col in range(BOARD_SIZE)]
            for row in range(BOARD_SIZE)
        ]

    def update_cell(self, cell_number: int, symbol: str) -> None:
        ...

    def get_cell(self, cell_number: int) -> str:
        ...
```

`Board` defines *what a game board is* — its internal grid and all the
operations that can be performed on it. The class itself is just the
blueprint; no data is stored until an instance is created.

---

## 2. Object

### Definition

An **object** is a specific instance of a class. When a class is
instantiated with `ClassName()`, Python allocates memory, calls `__init__`,
and returns a live object with its own separate state.

### How this project uses objects

All game-play happens through objects. `main.py` is the **Composition Root**
— the one place where all objects are created and connected.

```python
# main.py

def main() -> None:
    display = Display()                         # one Display object

    name_x, name_o = _collect_player_names()
    player_x = Player(name=name_x, symbol="X") # one Player object for X
    player_o = Player(name=name_o, symbol="O") # one Player object for O

    match = Match(
        player_x=player_x,
        player_o=player_o,
        display=display,
    )
    match.run()                                 # the Match object runs the game
```

Inside `Match.__init__`, two more objects are created:

```python
# game/match.py

def __init__(self, player_x, player_o, display) -> None:
    self._board = Board()            # one Board object, shared across all rounds
    self._score = BestOfThree(...)   # one BestOfThree object for score tracking
```

And inside `Match.run()`, a fresh `GameRound` object is created for each round:

```python
game_round = GameRound(
    board=self._board,
    player_x=self._player_x,
    player_o=self._player_o,
    display=self._display,
    round_number=round_number,
)
winner = game_round.play()
```

Each object has its **own state**. For example, `player_x.rounds_won` and
`player_o.rounds_won` are stored independently even though both are
instances of the same `Player` class.

---

## 3. Encapsulation

### Definition

**Encapsulation** means bundling an object's data (attributes) and the
methods that operate on that data inside the same class, while hiding the
internal implementation details from the outside world. External code can
only interact with the object through its **public interface**.

### How this project applies encapsulation

#### Private attributes

Every class in this project stores its data in private attributes (prefixed
with `_`). They cannot be accessed or modified directly from outside the class.

```python
# game/player.py

class Player:
    def __init__(self, name: str, symbol: str) -> None:
        self._name: str = name.strip()          # private
        self._symbol: str = symbol              # private
        self._rounds_won: int = 0               # private
        self._double_turn_used: bool = False    # private
```

Attempting `player._rounds_won = 99` from outside the class bypasses all
guards. The public interface is the only correct way to change state.

#### Read-only properties

Public data is exposed through `@property` decorators that allow reading but
not direct writing:

```python
@property
def rounds_won(self) -> int:
    return self._rounds_won

@property
def double_turn_available(self) -> bool:
    return not self._double_turn_used
```

#### Guard conditions on mutators

When state *must* change, a mutator method validates the transition before
allowing it:

```python
def use_double_turn(self) -> None:
    if self._double_turn_used:
        raise ValueError(
            f"{self._name} has already used their Double Turn this match."
        )
    self._double_turn_used = True
```

This guarantees that `_double_turn_used` can only ever change from `False`
to `True`, never backwards — regardless of who calls the method.

#### `Board` protects its grid

The `Board` class never exposes its internal `_grid` list directly.
External code calls `get_grid()`, which returns a **shallow copy**:

```python
def get_grid(self) -> list[list[str]]:
    return [row[:] for row in self._grid]   # copy, not the original
```

This means a caller can read the grid but cannot corrupt the board's
internal state by mutating the returned list.

`update_cell()` enforces two rules before modifying the grid:

```python
def update_cell(self, cell_number: int, symbol: str) -> None:
    self._validate_cell_number(cell_number)   # guard 1: range check
    if not self.is_cell_empty(cell_number):   # guard 2: occupancy check
        raise ValueError(...)
    row, col = self._cell_to_row_col(cell_number)
    self._grid[row][col] = symbol
```

No caller can place a mark on an occupied cell or outside the grid.

---

## 4. Abstraction

### Definition

**Abstraction** means hiding complex internal implementation details behind a
simple, clean public interface. A caller only needs to know *what* a method
does, not *how* it does it.

### How this project applies abstraction

#### `InputValidator.validate_move()`

Behind a single method call, three separate validation layers are hidden:

```python
# utils/input_validator.py

@staticmethod
def validate_move(raw_input: str, board) -> ValidationResult:
    # Layer 1 – can the string be parsed as an integer?
    integer_result = InputValidator.validate_integer(raw_input)
    if not integer_result:
        return integer_result

    # Layer 2 – is the integer within [1, 25]?
    range_result = InputValidator.validate_range(integer_result.value)
    if not range_result:
        return range_result

    # Layer 3 – is the cell still empty on the board?
    return InputValidator.validate_occupancy(integer_result.value, board)
```

The caller in `GameRound` only needs to write:

```python
validation = InputValidator.validate_move(raw, self._board)
if not validation:
    self._display.show_invalid_move(validation.error_message)
```

The caller has no knowledge of the three-layer pipeline.

#### `WinChecker.check_winner()`

Behind one method, four directional checks are hidden:

```python
@staticmethod
def check_winner(board, symbol: str) -> bool:
    grid = board.get_grid()
    return (
        WinChecker.check_rows(grid, symbol)
        or WinChecker.check_columns(grid, symbol)
        or WinChecker.check_main_diagonal(grid, symbol)
        or WinChecker.check_anti_diagonal(grid, symbol)
    )
```

The caller simply writes `WinChecker.check_winner(self._board, player.symbol)`
and receives `True` or `False`.

#### `GameRound.play()`

The entire turn loop — input reading, validation, board marking, win/draw
detection — is abstracted behind a single method:

```python
winner = game_round.play()   # returns a Player or None
```

`Match` does not know how turns work. It only knows that `play()` starts a
round and returns a result.

#### `Match.run()`

Similarly, the full Best-of-Three match lifecycle is hidden behind:

```python
match.run()
```

`main.py` does not know how rounds are sequenced, how scores are tracked, or
how the match concludes.

---

## 5. Composition

### Definition

**Composition** is an OOP design pattern where a class is built by combining
(composing) other objects, rather than inheriting from a parent class. The
phrase is *"has-a"* rather than *"is-a"*.

This project uses **composition exclusively** — there is no class hierarchy
and no `class A(B):` anywhere in the codebase.

### How this project applies composition

#### `GameRound` is composed of all independent modules

```python
# game/game_round.py

class GameRound:
    def __init__(self, board, player_x, player_o, display, round_number):
        self._board = board               # HAS-A Board
        self._player_x = player_x         # HAS-A Player (X)
        self._player_o = player_o         # HAS-A Player (O)
        self._display = display           # HAS-A Display
        self._round_number = round_number
        self._reader = TimedInputReader(  # HAS-A TimedInputReader
            time_limit=MOVE_TIME_LIMIT
        )
```

`GameRound` also calls the stateless classes `WinChecker`, `DrawChecker`,
`InputValidator`, and `DoubleTurnManager` during a turn. It does not inherit
from any of them.

#### `Match` is composed of the objects it owns

```python
# game/match.py

class Match:
    def __init__(self, player_x, player_o, display):
        self._player_x = player_x         # HAS-A Player (X)
        self._player_o = player_o         # HAS-A Player (O)
        self._display = display           # HAS-A Display
        self._board = Board()             # HAS-A Board (created here)
        self._score = BestOfThree(...)    # HAS-A BestOfThree (created here)
```

`Match` creates `GameRound` objects dynamically at the start of each round
and discards them when the round is over. This means each round starts with
a freshly constructed controller.

#### Composition diagram

```
main.py
  └── creates ──► Player × 2
  └── creates ──► Display
  └── creates ──► Match
                    ├── owns ──► Board
                    ├── owns ──► BestOfThree
                    └── creates per round ──► GameRound
                                                ├── ref ──► Board
                                                ├── ref ──► Player × 2
                                                ├── ref ──► Display
                                                └── owns ──► TimedInputReader
```

No class in this diagram inherits from another. All relationships are
ownership (*owns*) or reference (*ref*).

---

## 6. Reusability

### Definition

**Reusability** means that a class or module can be used in multiple
contexts without modification.

### How this project achieves reusability

#### `MoveTimer` and `TimedInputReader`

These two classes contain **no game-specific logic**. They know nothing about
boards, players, or moves. `MoveTimer` simply counts down seconds;
`TimedInputReader` simply reads a line from stdin within a time limit.
Either class could be copied into a completely different project and used
without any changes.

#### `InputValidator` is context-independent

`InputValidator` only receives a raw string and a board reference. It does
not know who typed the string or whose turn it is. The same validator handles
input for both the normal move and the two extra moves in a Double Turn
sequence.

#### `WinChecker` accepts any board-like object

`WinChecker` operates on `get_grid() → list[list[str]]`, not on a `Board`
type. Any object that exposes this method can be checked for a winning line.
This is known as **duck typing** — the checker cares about the interface, not
the concrete class.

#### `ValidationResult` and `DoubleTurnResult` are reusable containers

Both are frozen dataclasses — immutable, self-contained result objects. They
can carry a result from one layer of the program to another without coupling
those layers:

```python
# utils/input_validator.py

@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    error_message: str
    value: int | None = None

    def __bool__(self) -> bool:
        return self.is_valid
```

The `__bool__` method allows the result to be used directly in an `if`
statement, which reduces repetitive code at every call site.

#### `BestOfThree` is independent of `GameRound`

`BestOfThree` receives only a winner symbol (`"X"`, `"O"`, or `None`) from
`Match`. It has no dependency on how the round was played. If the game rules
changed — for example, if rounds could time out — `BestOfThree` would require
no modification.

---

## 7. Maintainability

### Definition

**Maintainability** means that the codebase is structured so that future
changes — adding features, fixing bugs, or adjusting rules — can be made in
one place without unintended side effects elsewhere.

### How this project achieves maintainability

#### Single Responsibility Principle

Every class has **one reason to change**. If the display layout needs to
change, only `Display` needs to be edited. If the timer duration changes,
only `constants.py` and `MoveTimer` are involved. If the board size changes,
only `Board` and `constants.py` need updating.

Examples:

| Change needed | Only file(s) to edit |
|---|---|
| Change time limit from 15s to 20s | `utils/constants.py` — `MOVE_TIME_LIMIT` |
| Change activation keyword from `"double"` to `"power"` | `game/double_turn.py` — `ACTIVATION_KEYWORD` |
| Change win condition from 5-in-a-row to 4-in-a-row | `game/win_checker.py` |
| Change the banner style | `ui/display.py` |
| Add a third player | `game/player.py`, `game/game_round.py` |

#### Centralised constants

All magic values are stored in `utils/constants.py`:

```python
# utils/constants.py

BOARD_SIZE      = 5
TOTAL_CELLS     = 25
MOVE_TIME_LIMIT = 15
MAX_ROUNDS      = 3
ROUNDS_TO_WIN   = 2
SYMBOL_X        = "X"
SYMBOL_O        = "O"
```

If `BOARD_SIZE` changes to `4`, the `Board`, `WinChecker`, and `Display`
classes all read from the same constant automatically — there is no need to
search the entire codebase for hardcoded `5` values.

#### Exception handling is layered

Exceptions are caught at the level where they can be handled meaningfully:

- `Board.update_cell()` raises `ValueError` for invalid input — this is the
  lowest layer, closest to the data.
- `GameRound._place_move()` catches `ValueError` from the board and converts
  it into a user-visible message via `Display.show_invalid_move()`.
- `Match.run()` catches unexpected `Exception` during a round and treats the
  round as a draw rather than crashing the entire match.
- `main()` catches `KeyboardInterrupt` and `EOFError` and exits gracefully.

This layered structure means that error handling logic does not leak into the
wrong level of the program.

#### Separation of concerns between I/O and logic

All game logic classes (`Board`, `Player`, `WinChecker`, etc.) contain no
`print()` calls. All output is centralised in `Display`. This means the
presentation can be changed — for example, switching from console output to a
file log or a GUI — without touching any game logic.

#### Test coverage supports safe changes

The project includes **92 unit tests** across six test files. Before and
after any change, the tests can be run to verify that the existing behaviour
has not been broken. This is the practical result of maintainable design:
the classes are small and focused enough to be tested independently.

---

## Summary Table

| OOP Concept | How this project demonstrates it |
|---|---|
| **Class** | 12 classes, each modelling one real concept (Board, Player, Match, …) |
| **Object** | Objects created in `main.py`; each has independent state (e.g., separate `rounds_won` per player) |
| **Encapsulation** | All attributes prefixed `_`; public access only through properties and validated mutators |
| **Abstraction** | Complex pipelines hidden behind single method calls (`validate_move`, `check_winner`, `play`) |
| **Composition** | `GameRound` and `Match` are built from other objects; no class inherits from another |
| **Reusability** | `MoveTimer`, `TimedInputReader`, `InputValidator`, `WinChecker` usable in any context |
| **Maintainability** | One responsibility per class; constants centralised; I/O separated from logic; 92 unit tests |
