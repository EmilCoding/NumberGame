import random
import itertools
from abc import ABC, abstractmethod
from numbergame.game import UI, Signal, _ABSOLUTE_MAX_NUMBER


class DoNotCompute(Exception):
    pass


class CannotInterpretText(ValueError):
    pass


class Bot(UI, ABC):
    """Bot that is able to play `The Number Game`"""
    maximum_target: int

    def __init__(self, /, output_to_terminal: bool = False) -> None:
        self.output_to_terminal = output_to_terminal

    @abstractmethod
    def get_guess(self, prompt: str) -> int:
        """Request a guesses from the player."""

    def provide_feedback(self, signal: Signal, prompt: str) -> None:
        """Provide feedback to the user regarding their guess."""
        if self.output_to_terminal:
            print(prompt)

    def echo(self, message: str) -> None:
        """Echo a message to the user. Default implementation is muted."""
        if self.output_to_terminal:
            print(message)


class RandoBot(Bot):
    """Makes a random guess within the bounds set by the game [1, maximum_target]"""

    def get_guess(self, _: str) -> int:
        assert self.maximum_target, "Maximum target must be provided before playing the game."
        return random.randint(1, self.maximum_target)


class LinearSearchBot(Bot):
    """Bot start guessing from 1, then 2, then 3, etc."""
    guesser: itertools.count

    def restart(self, maximum_target: int) -> None:
        super().restart(maximum_target)
        self.guesser = itertools.count(1)

    def get_guess(self, _: str) -> int:
        return self.guesser.__next__()


class BinarySearchBot(Bot):
    """Uses a binary search approach to guess the number."""
    lower_limit: int
    upper_limit: int
    last_answer: None | int = None

    def restart(self, maximum_target: int) -> None:
        super().restart(maximum_target)
        self.lower_limit = 1
        self.upper_limit = self.maximum_target
        self.last_answer = None

    def get_guess(self, _: str) -> int:
        """Request a guesses from the player."""
        self.upper_limit = self.upper_limit or self.maximum_target or _ABSOLUTE_MAX_NUMBER
        self.last_answer = (self.lower_limit + self.upper_limit) // 2
        return self.last_answer

    def provide_feedback(self, signal: Signal, prompt: str) -> None:
        """Provide feedback to the user regarding their guess."""
        if self.output_to_terminal:
            print(prompt)

        assert self.last_answer, "Bot must have guessed before getting feedback"
        if signal is Signal.TOO_LOW:
            self.lower_limit = self.last_answer
            return
        if signal is Signal.TOO_HIGH:
            self.upper_limit = self.last_answer
            return
        raise CannotInterpretText(f'Could not interpret {prompt}')


class CheatBot(Bot):
    answer: int

    def restart(self, maximum_target: int) -> None:
        random.seed(42)
        self.answer = random.randint(1, maximum_target)
        random.seed(42)

    def get_guess(self, prompt: str) -> int:
        """Request a guesses from the player."""
        return self.answer


ALL_BOT_TYPES: list[type[Bot]] = [RandoBot, LinearSearchBot, BinarySearchBot]


if __name__ == '__main__':
    from numbergame import Game
    max_value = 100

    bot = BinarySearchBot(output_to_terminal=True)
    game = Game(bot, max_target=max_value)
    game.run()
