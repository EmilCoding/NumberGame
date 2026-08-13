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
from typing import Any, Callable
from abc import ABC, abstractmethod


DEFAULT_MAX_NUMBER = 1_000
DEFAULT_MAX_QUESTIONS = 1_000
INTRO_PROMP = """
Welcome to the number game.
--------------------------

The rules are simple. You have to guess a number between 1 and {:_}
(both limits included.) You do this in a series of rounds. Lowest number
of guesses wins.
"""

_ABSOLUTE_MAX_NUMBER = 100_000
_ABSOLUTE_MAX_QUESTIONS = 1_000_000


class Signal(enum.StrEnum):
    TOO_LOW = enum.auto()
    TOO_HIGH = enum.auto()
    OUT_OF_RANGE = enum.auto()
    COULD_NOT_INTERPRET_ANSWER = enum.auto()


class MaxAttempts(Exception):
    """Raised when a player fails to supply a valid guess within the limit.

    The exception stores the number of attempts that were made before the game
    decided the input loop had failed.
    """
    attempts: int

    def __init__(self, attempts: int) -> None:
        self.attempts = attempts
        super().__init__(f"Failed after {attempts} attempts.")


class Game:
    """A configurable number-guessing game played through injected I/O hooks.

    The class encapsulates the random target generation, user prompt loop, and
    win/loss reporting. The default interface uses Python's built-in ``input`` and
    ``print`` functions, but other callables can be supplied to integrate with
    tests or external UI layers.
    """
    ui: UI
    ui_input_getter: Callable[[str], str]
    ui_output: Callable[[str], None]

    max_target: int = DEFAULT_MAX_NUMBER
    max_question: int = DEFAULT_MAX_QUESTIONS

    def __init__(self, ui: UI, /, maximum_target: int = DEFAULT_MAX_NUMBER, max_question: int = DEFAULT_MAX_QUESTIONS) -> None:
        """Create a number game with configurable bounds and I/O callbacks.

        Args:
            ui: Interface between user and game.
            maximum_target: Largest secret number that can be generated.
            max_question: Maximum number of guesses allowed for a round.

        Raises:
            AssertionError: If any configuration value is not a positive integer.
        """
        self.ui = ui
        self.max_target = maximum_target
        self.max_question = max_question

        assert is_positive_integer(maximum_target), "'max_target' must be a positive integer."
        assert is_positive_integer(max_question), "'max_question' must be a positive integer."

        if self.max_target > _ABSOLUTE_MAX_NUMBER:
            self.max_target = _ABSOLUTE_MAX_NUMBER
            warnings.warn(colorama.Fore.YELLOW + "Given 'max-target' was too high. Lowered it to an acceptable level" + colorama.Fore.RESET)
        if self.max_question > _ABSOLUTE_MAX_QUESTIONS:
            self.max_question = _ABSOLUTE_MAX_QUESTIONS
            warnings.warn(colorama.Fore.YELLOW + "Given 'max-questions' was too high. Lowered it to an acceptable level" + colorama.Fore.RESET)

        self.ui.maximum_target = maximum_target

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
        for score in range(1, self.max_question + 1):
            if target == (userinput := self._get_guess_from_user()):
                return score
            if userinput < target:
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
        for attempts in range(1, self.max_question + 1):
            try:
                return int(rawinput := self.ui.get_guess('Please enter an integer: '))
            except ValueError:
                self.ui.provide_feedback(Signal.COULD_NOT_INTERPRET_ANSWER, f"Cannot intepret {rawinput} as a string - Please try again")
        raise MaxAttempts(attempts)

    def _generate_random_target_number(self) -> int:
        """Generate a random target in the inclusive range [1, max_target]."""
        return random.randint(1, self.max_target)


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


class PlayerUI(UI):

    def get_guess(self, prompt: str) -> str:
        return input(prompt)

    def provide_feedback(self, signal: Signal, prompt: str) -> None:
        self.echo(prompt)

    def echo(self, message: str) -> None:
        print(message)


def is_positive_integer(n: Any) -> bool:
    return isinstance(n, int) and n > 0


if __name__ == '__main__':
    game = Game(PlayerUI())
    game.run()
