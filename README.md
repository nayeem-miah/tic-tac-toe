# Customized 5×5 Tic-Tac-Toe

A modern, object-oriented Python console implementation of a customized 5×5 Tic-Tac-Toe game. It features timed moves, a special "Double Turn" ability, and is structured as a Best-of-Three match format.

## Overview
This project is a command-line interface (CLI) implementation of Tic-Tac-Toe played on an expanded **5×5 board**. While traditional Tic-Tac-Toe is played on a 3×3 grid, this version challenges players to secure **five marks in a row** to win. It incorporates competitive elements such as move timers, custom rules, and multi-round match structures to provide an engaging and strategic gameplay experience.

---

## Features

*   **5×5 Game Board:** A larger grid containing 25 cells numbered from 1 to 25.
*   **Two Players:** Standard player tokens represented by **Player X** and **Player O**.
*   **Cell Selection (1–25):** Players select their desired moves by typing the corresponding cell number from 1 to 25.
*   **Five-in-a-Row Win Condition:** The required line length to win is exactly 5 consecutive marks.
*   **Directional Winner Detection:** The game evaluates winning configurations across all rows, columns, the main diagonal (top-left to bottom-right), and the anti-diagonal (top-right to bottom-left).
*   **15-Second Timed Moves:** Each turn is subject to a strict 15-second time limit to keep matches fast-paced.
*   **Turn Forfeiture:** Failing to input a move within the 15-second limit results in skipping the player's turn.
*   **Double Turn Ability:** Each player can invoke a special `double` command **once per match**, granting two consecutive moves to seize the upper hand.
*   **Best-of-Three Format:** Matches consist of up to 3 rounds. The first player to accumulate 2 round wins is declared the overall match champion.
*   **Score Tracking:** Running scores (round victories, draws, rounds played) are tracked and displayed on a scoreboard at the end of each round.
*   **Draw Detection:** Automatically detects a draw if all 25 cells are filled without any player achieving a 5-cell winning line.
*   **Replay System:** Allows players to initiate a brand-new match after completion, resetting their scores and abilities while keeping their names.

---

## Programming Paradigm

This project is built from the ground up following the **Object-Oriented Programming (OOP)** paradigm. The codebase is highly modular, adhering to clean coding standards, encapsulation, and the Single Responsibility Principle (SRP).

### Class and Component Responsibilities

The logic is divided into specialized modules and classes:

#### Core Game Logic (`game/`)
*   **`Board`** ([board.py](file:///c:/Users/nayeen/projects/Tic%20Tac%20Toe/game/board.py)): Manages the 5×5 internal grid state, registers player moves, validates cell availability, and resets itself between rounds.
*   **`Player`** ([player.py](file:///c:/Users/nayeen/projects/Tic%20Tac%20Toe/game/player.py)): Represents player profiles, managing names, symbols, and tracking the single-use Double Turn flag.
*   **`GameRound`** ([game_round.py](file:///c:/Users/nayeen/projects/Tic%20Tac%20Toe/game/game_round.py)): Directs the turn loop, move inputs, and status evaluations for a single round.
*   **`Match`** ([match.py](file:///c:/Users/nayeen/projects/Tic%20Tac%20Toe/game/match.py)): Orchestrates the Best-of-Three match loop and manages round transitions.
*   **`BestOfThree`** ([best_of_three.py](file:///c:/Users/nayeen/projects/Tic%20Tac%20Toe/game/best_of_three.py)): Handles the scoreboard state, recording round outcomes and checking if the match is won.
*   **`WinChecker`** ([win_checker.py](file:///c:/Users/nayeen/projects/Tic%20Tac%20Toe/game/win_checker.py)): A stateless evaluator verifying 5-in-a-row lines on the board.
*   **`DrawChecker`** ([draw_checker.py](file:///c:/Users/nayeen/projects/Tic%20Tac%20Toe/game/draw_checker.py)): Verifies draw states based on board emptiness and win status.
*   **`DoubleTurnManager`** ([double_turn.py](file:///c:/Users/nayeen/projects/Tic%20Tac%20Toe/game/double_turn.py)): Manages activation requests and eligibility checks for the Double Turn special ability.
*   **`MoveTimer` & `TimedInputReader`** ([timer.py](file:///c:/Users/nayeen/projects/Tic%20Tac%20Toe/game/timer.py)): Uses multi-threading utilities (`threading.Timer` and `queue.Queue`) to read console input within a 15-second timeout window.

#### User Interface (`ui/`)
*   **`Display`** ([display.py](file:///c:/Users/nayeen/projects/Tic%20Tac%20Toe/ui/display.py)): The View layer of the project. It coordinates all terminal outputs, displaying boards, banners, error messages, and timers.

#### Utilities (`utils/`)
*   **`InputValidator`** ([input_validator.py](file:///c:/Users/nayeen/projects/Tic%20Tac%20Toe/utils/input_validator.py)): Inspects and validates coordinates to ensure type correctness, range limits, and cell emptiness.
*   **Constants** ([constants.py](file:///c:/Users/nayeen/projects/Tic%20Tac%20Toe/utils/constants.py)): Centralizes variables like board size (5), win length (5), and time limit (15) for easy configuration.

---

## Project Structure

The project file structure is organized as follows:

```text
Tic Tac Toe/
│
├── main.py                  # Match composition root & setup bootstrap
│
├── game/                    # Core logic classes
│   ├── __init__.py
│   ├── best_of_three.py     # Match score tracker
│   ├── board.py             # 5x5 board state
│   ├── double_turn.py       # Special double turn manager
│   ├── draw_checker.py      # Draw condition evaluator
│   ├── game_round.py        # Single round loop manager
│   ├── match.py             # Best-of-three match manager
│   ├── player.py            # Player profile & abilities
│   ├── timer.py             # Timed input utilities
│   └── win_checker.py       # Winning line checker
│
├── ui/                      # View classes
│   ├── __init__.py
│   └── display.py           # CLI board & prompt decorator
│
├── utils/                   # Shared utility modules
│   ├── __init__.py
│   ├── constants.py         # Static configuration
│   └── input_validator.py   # Turn command parsing & validation
│
├── tests/                   # Automated unittest suite
│   ├── __init__.py
│   ├── test_board.py
│   ├── test_double_turn.py
│   ├── test_draw_checker.py
│   ├── test_player.py
│   ├── test_timer.py
│   └── test_win_checker.py
│
└── docs/                    # Design documentation
    ├── DEVELOPER_GUIDE.md
    └── OOP_EXPLANATION.md
```

---

## How the Game Works

1.  **Enter Player Names:** The game starts by prompting for distinct names for Player X and Player O.
2.  **Turn Loop Begins:** Player X is prompted to make a move.
3.  **Command / Cell Input:** On their turn, a player must type either:
    *   A cell number between `1` and `25` (e.g., `13` to mark the center cell).
    *   The keyword `double` (case-insensitive) to activate their Double Turn.
4.  **Board Update:**
    *   If a cell number is entered, the board is updated with the player's symbol.
    *   If `double` is successfully activated, the player immediately receives two consecutive moves.
5.  **Validation and Timing:**
    *   The input must be submitted within 15 seconds. If the timer expires, the turn is skipped.
    *   If invalid input is entered, the turn is skipped.
6.  **Checking Conditions:** After a valid token is placed, the game checks if the player won (5 marks in a row) or if the board is full (draw).
7.  **Match Progression:** The rounds alternate until a player wins 2 rounds, concluding the Best-of-Three match.
8.  **Replay Prompt:** After the match ends, players can opt to play again or exit.

---

## Requirements

*   **Python:** Version `3.10` or higher.
*   **External Dependencies:** None. The application runs entirely on Python's built-in standard library.

---

## Installation & Running

Follow these instructions to run the game on Windows using PowerShell:

### 1. Clone the repository
```powershell
git clone <repository-url>
cd "Tic Tac Toe"
```

### 2. Check your Python version
Ensure you have Python 3.10+ installed:
```powershell
python --version
```

### 3. Run the Game
```powershell
python main.py
```

### 4. Run the Automated Tests
Execute the full test suite using Python's built-in unittest framework:
```powershell
python -m unittest discover -s tests
```
