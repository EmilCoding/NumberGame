"""Classic number-guessing game logic and prompt handling.

The module defines a small console game in which the player attempts to guess a
random integer within a configurable range. The game is intentionally designed
around dependency injection so that the input and output streams can be replaced
by tests or alternate UIs while leaving the game rules unchanged.
"""
import enum
import random
import colorama
import warnings
from typing import Any
from abc import ABC, abstractmethod


DEFAULT_MAX_NUMBER = 1_000
DEFAULT_MAX_QUESTIONS = 1_000
DEFALT_MAX_USERINPUT_ATTEMPS = 100
INTRO_PROMP = """
Welcome to the number game.
--------------------------

The rules are simple. You have to guess a number between 1 and {:_}
(both limits included.) You do this in a series of rounds. Lowest number
of guesses wins.
"""
_ABSOLUTE_MAX_NUMBER = 1_000_000
_ABSOLUTE_MAX_QUESTIONS = 3_000_000
_ABSOLUTE_MAX_USERINPUT_ATTEMPS = DEFALT_MAX_USERINPUT_ATTEMPS


class Signal(enum.StrEnum):
    TOO_LOW = enum.auto()
    TOO_HIGH = enum.auto()
    CORRECT = enum.auto()
    OUT_OF_RANGE = enum.auto()
    ANSWER_ACCEPTED = enum.auto()
    UNACCEPTABLE_ANSWER = enum.auto()


class MaxAttempts(Exception):
    """Raised when a player fails to supply a valid guess within the limit.

    The exception stores the number of attempts that were made before the game
    decided the input loop had failed.
    """
    attempts: int

    def __init__(self, attempts: int) -> None:
        self.attempts = attempts
        super().__init__(f"Failed after {attempts} attempts.")


class UI(ABC):
    maximum_target: int

    def restart(self, maximum_target: int) -> None:
        """Reset user interface before running a game."""
        self.maximum_target = maximum_target

    @abstractmethod
    def get_guess(self, prompt: str) -> int | str:
        """Request a guesses from the player."""

    @abstractmethod
    def provide_feedback(self, signal: Signal, prompt: str) -> None:
        """Provide feedback to the user regarding their guess."""

    @abstractmethod
    def echo(self, message: str) -> None:
        """Echo a message to the user"""


class Game:
    """A configurable number-guessing game played through injected I/O hooks.

    The class encapsulates the random target generation, user prompt loop, and
    win/loss reporting. The default interface uses Python's built-in ``input`` and
    ``print`` functions, but other callables can be supplied to integrate with
    tests or external UI layers.
    """
    ui: UI
    max_target: int
    max_questions: int
    max_userinput_attempts: int

    def __init__(
        self,
        ui: UI,
        /,
        max_target: int = DEFAULT_MAX_NUMBER,
        max_questions: int = DEFAULT_MAX_QUESTIONS,
        max_userinput_attempts: int = DEFALT_MAX_USERINPUT_ATTEMPS
    ) -> None:
        """Create a number game with configurable bounds and I/O callbacks.

        Args:
            ui: Interface between user and game.
            max_target: Largest secret number that can be generated.
            max_question: Maximum number of guesses allowed for a round.
            max_userinput_attempts (int): Maximum number of attempts given to the user when getting input.

        Raises:
            AssertionError: If any configuration value is not a positive integer.
        """
        self.ui = ui
        self.max_target = validate_integer(max_target, _ABSOLUTE_MAX_NUMBER, 'max_target')
        self.max_questions = validate_integer(max_questions, _ABSOLUTE_MAX_QUESTIONS, 'max_questions')
        self.max_userinput_attempts = validate_integer(max_userinput_attempts, _ABSOLUTE_MAX_USERINPUT_ATTEMPS, 'max_userinput_attempts')
        self.ui.maximum_target = max_target

    def run(self) -> None | int:
        """Run a full game round and return the final score if the player wins.

        Returns:
            The player score on success, or ``None`` if the player exhausts the
            allowed number of guesses.
        """
        # Greet player and generate target
        self.ui.echo(INTRO_PROMP.format(self.max_target))
        target = self._generate_random_target_number()
        self.ui.restart(self.max_target)

        # Play the game
        score = self._gameloop(target)

        # Give feedback to user
        if isinstance(score, int):
            self.ui.echo(colorama.Fore.GREEN + f'Your score was {score}' + colorama.Fore.RESET)
            self.ui.echo("Please come back again some day ;)")
        else:
            # Player lost
            self.ui.echo(colorama.Fore.RED
                         + f"Sorry! You lost. You did not guess the number in {self.max_target} rounds."
                         + colorama.Fore.RESET
                         )

        return score

    def _gameloop(self, target: int) -> None | int:
        """Main game loop of the number game.

        Ask the player for a number and compare with `target`.
        - If guess is correct, the player won. Return number of guesses.
        - If guess is wrong, the provide feedback and increment number of guesses by 1.

        Args:
            target: The secret number the player must find.

        Returns:
            The guess count on success, otherwise ``None``.
        """
        for score in range(1, self.max_questions + 1):
            userinput = self._get_guess_from_user()
            if target == userinput:
                self.ui.provide_feedback(Signal.CORRECT, f"Guess {userinput} is correct!")
                return score
            if not 0 <= userinput <= self.max_target:
                self.ui.provide_feedback(Signal.OUT_OF_RANGE, f"Guess {userinput} is of out of range [1, {self.max_target}]")
            elif userinput < target:
                self.ui.provide_feedback(Signal.TOO_LOW, f"Guess {userinput} was too low")
            else:
                self.ui.provide_feedback(Signal.TOO_HIGH, f"Guess {userinput} was too high")
        return None

    def _get_guess_from_user(self) -> int:
        """Read and validate a single integer guess from the configured input.

        The method keeps asking until it receives an integer conversion that
        succeeds. If repeated input is invalid, it raises ``MaxAttempts``.

        Returns:
            A valid integer guess.

        Raises:
            MaxAttempts: If the input loop exceeds the configured guess limit.
        """
        for attempts in range(1, self.max_userinput_attempts + 1):
            rawinput = self.ui.get_guess('Please enter an integer: ')
            try:
                integer = self._interpret_as_integer(rawinput)
                self.ui.provide_feedback(Signal.ANSWER_ACCEPTED, "Ansert acceptable")
                return integer
            except ValueError, TypeError:
                self.ui.provide_feedback(Signal.UNACCEPTABLE_ANSWER, f"Cannot intepret {rawinput} as a string - Please try again")
        raise MaxAttempts(attempts)

    def _interpret_as_integer(self, __input: Any) -> int:
        match __input:
            case int():
                return __input
            case str():
                return int(__input)
            case float():
                raise TypeError('Floating point valued guesses are not allowed')
            case _:
                raise ValueError(f'Cannot handle the input type {type(__input)}')

    def _generate_random_target_number(self) -> int:
        """Generate a random target in the inclusive range [1, max_target]."""
        return random.randint(1, self.max_target)


class PlayerUI(UI):

    def get_guess(self, prompt: str) -> str:
        return input(prompt)

    def provide_feedback(self, signal: Signal, prompt: str) -> None:
        self.echo(prompt)

    def echo(self, message: str) -> None:
        print(message)


def validate_integer(value: Any, max_value: int, field_name: str) -> int:
    if not isinstance(value, int):
        raise TypeError(f'{field_name} must be a positive integer. Was given as {type(value)}')
    if value <= 0:
        raise ValueError(f'{field_name} must be a positive integer. {value=}')
    if value > max_value:
        warnings.warn(colorama.Fore.YELLOW
                      + f"Given {field_name} was too high. Lowered it to an acceptable level"
                      + colorama.Fore.RESET)
        return max_value
    return value


if __name__ == '__main__':
    game = Game(PlayerUI())
    game.run()
