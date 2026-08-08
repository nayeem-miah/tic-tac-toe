"""
input_validator.py
------------------
Responsibility:
    Validates all player input before it touches the board.

    Three independent validation layers, applied in order:
        1. Type check  — is the raw string parseable as an integer?
        2. Range check — is the integer between 1 and 25?
        3. Occupancy   — is the cell still empty on the board?

    Returns a ValidationResult for every check so callers
    receive a structured (is_valid, error_message) pair instead
    of catching raw exceptions.

    Contains NO board mutation logic, NO player logic, NO display logic.
    Follows Single Responsibility Principle (SRP).

    Design note:
        All methods are static — InputValidator holds no state of its
        own.  This makes it trivial to port: in C it becomes a set of
        pure functions; in C++ a class with only static methods.
"""

from dataclasses import dataclass
from utils.constants import TOTAL_CELLS


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ValidationResult:
    """
    Immutable container for a single validation outcome.

    Attributes:
        is_valid     : True if the input passed the validation check.
        error_message: Human-readable reason for failure, or empty
                       string when is_valid is True.
        value        : Parsed integer value on success, or None on failure.
    """

    is_valid: bool
    error_message: str
    value: int | None = None

    def __bool__(self) -> bool:
        """Allow truth-testing a result directly: ``if result: ...``"""
        return self.is_valid


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------

class InputValidator:
    """
    Stateless validator for Tic-Tac-Toe move input.

    Usage example::

        result = InputValidator.validate_move("13", board)
        if not result:
            print(result.error_message)
        else:
            board.update_cell(result.value, symbol)
    """

    # ------------------------------------------------------------------
    # Private factory helpers  (DRY: remove repeated ValidationResult(...) calls)
    # ------------------------------------------------------------------

    @staticmethod
    def _ok(value: int) -> ValidationResult:
        """Return a passing ValidationResult carrying *value*."""
        return ValidationResult(is_valid=True, error_message="", value=value)

    @staticmethod
    def _fail(message: str) -> ValidationResult:
        """Return a failing ValidationResult with the given *message*."""
        return ValidationResult(is_valid=False, error_message=message)

    # ------------------------------------------------------------------
    # Primary (composite) check
    # ------------------------------------------------------------------

    @staticmethod
    def validate_move(raw_input: str, board) -> ValidationResult:
        """
        Run all three validation layers in sequence and return the first
        failure encountered, or a passing result if all checks pass.

        Layers:
            1. validate_integer  — raw string → integer
            2. validate_range    — integer within [1, 25]
            3. validate_occupancy — cell is still empty on the board

        Args:
            raw_input: The string the player typed (may be anything).
            board    : A Board instance (used only for occupancy check).

        Returns:
            A ValidationResult.  On success, ``result.value`` holds the
            validated cell number as an ``int``.
        """
        # Layer 1 – parse
        integer_result = InputValidator.validate_integer(raw_input)
        if not integer_result:
            return integer_result

        # Layer 2 – range
        range_result = InputValidator.validate_range(integer_result.value)
        if not range_result:
            return range_result

        # Layer 3 – occupancy
        return InputValidator.validate_occupancy(integer_result.value, board)

    # ------------------------------------------------------------------
    # Individual validation layers
    # ------------------------------------------------------------------

    @staticmethod
    def validate_integer(raw_input: str) -> ValidationResult:
        """
        Check whether raw_input can be parsed as a whole number.

        Accepts positive and negative integers; range is checked
        separately.  Leading/trailing whitespace is stripped first.

        Args:
            raw_input: The raw string from stdin.

        Returns:
            ValidationResult(is_valid=True,  value=<int>)  on success.
            ValidationResult(is_valid=False, error_message=...)  on failure.

        Examples::

            validate_integer("13")    → ValidationResult(True,  "", 13)
            validate_integer("  7 ")  → ValidationResult(True,  "", 7)
            validate_integer("abc")   → ValidationResult(False, "...")
            validate_integer("3.5")   → ValidationResult(False, "...")
            validate_integer("")      → ValidationResult(False, "...")
        """
        stripped = raw_input.strip()

        if not stripped:
            return InputValidator._fail(
                f"No input received. Please enter a number between 1 and {TOTAL_CELLS}."
            )

        try:
            parsed = int(stripped)
        except ValueError:
            return InputValidator._fail(
                f"'{stripped}' is not a valid number. "
                f"Please enter a whole number between 1 and {TOTAL_CELLS}."
            )

        return InputValidator._ok(parsed)

    @staticmethod
    def validate_range(cell_number: int) -> ValidationResult:
        """
        Check whether cell_number falls within the legal cell range [1, 25].

        Args:
            cell_number: A parsed integer (output of validate_integer).

        Returns:
            ValidationResult(is_valid=True,  value=cell_number)  on success.
            ValidationResult(is_valid=False, error_message=...)  on failure.

        Examples::

            validate_range(1)   → ValidationResult(True,  "", 1)
            validate_range(25)  → ValidationResult(True,  "", 25)
            validate_range(0)   → ValidationResult(False, "...")
            validate_range(26)  → ValidationResult(False, "...")
            validate_range(-5)  → ValidationResult(False, "...")
        """
        if not (1 <= cell_number <= TOTAL_CELLS):
            return InputValidator._fail(
                f"{cell_number} is out of range. "
                f"Cell numbers must be between 1 and {TOTAL_CELLS}."
            )

        return InputValidator._ok(cell_number)

    @staticmethod
    def validate_occupancy(cell_number: int, board) -> ValidationResult:
        """
        Check whether the given cell is still unoccupied on the board.

        The board reference is typed as ``Any`` (not imported) to keep
        this module independent of the Board class.  Only the public
        ``is_cell_empty`` and ``get_cell`` interface is used.

        Args:
            cell_number: A range-validated cell number.
            board      : A Board instance exposing ``is_cell_empty()``
                         and ``get_cell()``.

        Returns:
            ValidationResult(is_valid=True,  value=cell_number)  on success.
            ValidationResult(is_valid=False, error_message=...)  on failure.

        Examples::

            # Cell 5 is free
            validate_occupancy(5, board)  → ValidationResult(True, "", 5)

            # Cell 5 is taken by "X"
            validate_occupancy(5, board)  → ValidationResult(False, "Cell 5 is already taken by X ...")
        """
        if not board.is_cell_empty(cell_number):
            occupant = board.get_cell(cell_number)
            return InputValidator._fail(
                f"Cell {cell_number} is already taken by '{occupant}'. "
                f"Please choose a different cell."
            )

        return InputValidator._ok(cell_number)
