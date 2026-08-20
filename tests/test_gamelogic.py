"""
Test the logic of the `Game` class.
==================================

Parameters that can be changed
------------------------------
max_target: int
max_question: int
max_userinput_attempts: int
UI : Is an injected dependency
"""
import pytest
import itertools
from typing import Any, Generator, Iterable

from numbergame.game import (MaxAttempts, Game, Signal, UI,
                             _ABSOLUTE_MAX_NUMBER, _ABSOLUTE_MAX_QUESTIONS,
                             _ABSOLUTE_MAX_USERINPUT_ATTEMPS
                             )


class UIWithDeterminedOutput(UI):
    """Default test UI.

    Methods are implemented to do nothing in principle so that they
    can be overwritten when needed with minimal changes.
    """
    guess_queue: Iterable[Any]
    guess_generator: Generator[Any, None, None]
    feedback_signals: list[Signal]

    def __init__(
        self,
        /,
        default_guess: None | Any = "",
        guess_queue: None | Iterable[Any] = None,
    ) -> None:
        self.guess_queue = guess_queue or itertools.cycle([default_guess, ])
        self.n_guess_calls = 0
        self.guess_generator = (x for x in self.guess_queue)
        self.feedback_signals = []

    def restart(self, maximum_target: int) -> None:
        self.n_guess_calls = 0
        self.max_target = maximum_target
        self.guess_generator = (x for x in self.guess_queue)
        self.feedback_signals = []

    def get_guess(self, prompt: str) -> int | str:
        """Request a guesses from the player."""
        self.n_guess_calls += 1
        return self.guess_generator.__next__()

    def provide_feedback(self, signal: Signal, prompt: str) -> None:
        """Provide feedback to the user regarding their guess."""
        self.feedback_signals.append(signal)

    def echo(self, message: str) -> None:
        """Echo a message to the user"""
        pass


# ============================================================================================================================ #
# Test the method Game._generation_of_target_number                                                                            #
# ---------------------------------------------------------------------------------------------------------------------------- #
# - [x] Set values from initiallizer                                                                                           #
# - [x] Inforce integer range validation                                                                                       #
# - [x] Inforce maximum value cap and raise warning if overstepped.                                                            #
# ============================================================================================================================ #
@pytest.mark.parametrize('field', ['max_target', 'max_questions', 'max_userinput_attempts'])
@pytest.mark.parametrize('value', [1, 10, 50])
def test_set_options_from_initiallizer(field: str, value: int, ):
    kwargs = {field: value}
    game = Game(UIWithDeterminedOutput(), **kwargs)
    assert value == game.__getattribute__(field)


@pytest.mark.parametrize('field', ['max_target', 'max_questions', 'max_userinput_attempts'])
@pytest.mark.parametrize('value', [None, 1.123, -1321, -1, 0, ])
def test_inforce_integer_range(field: str, value: int, ):
    kwargs = {field: value}
    with pytest.raises(Exception) as error:
        Game(UIWithDeterminedOutput(), **kwargs)
    assert isinstance(error.value, (TypeError, ValueError)), "An expection was raised but not the correct one"


@pytest.mark.parametrize('field,max_value', [
    ('max_target', _ABSOLUTE_MAX_NUMBER),
    ('max_questions', _ABSOLUTE_MAX_QUESTIONS),
    ('max_userinput_attempts', _ABSOLUTE_MAX_USERINPUT_ATTEMPS),
])
def test_set_maximum_cap_on_options(monkeypatch, field: str, max_value: int):
    """Test if options are capped at their maximum values and a warning is raised"""
    # Setup monkeypatch
    called = False

    def mockwarn(*arg, **kwargs):
        nonlocal called
        called = True
    monkeypatch.setattr('warnings.warn', mockwarn)

    kwargs = {field: max_value + 1}
    game = Game(UIWithDeterminedOutput(), **kwargs)
    assert max_value == game.__getattribute__(field), "Field has not forced to max. value"
    assert called, "Warning was not raised"


# ============================================================================================================================ #
# Test the method Game._generation_of_target_number                                                                            #
# ============================================================================================================================ #
@pytest.mark.parametrize('max_target', [10, 100, 500])
def test_generation_of_target_number(max_target: int):
    """Test if the `Game._generation_of_target_number` method covers the full sample space."""
    samplesize: int = 100 * max_target
    game = Game(UIWithDeterminedOutput(), max_target=max_target)

    sample = set(game._generate_random_target_number() for _ in range(samplesize))
    sample_space = set(range(1, max_target + 1))
    assert not (diff := sample_space - sample), f"Method never hit {diff}"
    assert not (extra := sample - sample_space), f"Method generated numbers outside range: {extra}"


# ============================================================================================================================ #
# Test the method Game._interpret_as_integer.                                                                                  #
# ============================================================================================================================ #
@pytest.mark.parametrize('testvalue,expected_output', [
    (123, 123),
    (-123, -123),
    ('3123', 3123),
])
def test_interpret_as_integer_valid(testvalue: Any, expected_output: int):
    game = Game(UIWithDeterminedOutput())
    integer = game._interpret_as_integer(testvalue)
    assert expected_output == integer, f"{integer} != {expected_output}"


@pytest.mark.parametrize('testvalue', [
    'This is not an integer!',
    'Neither is this',
    '1.13181',
    1.13181,
    1e6,
])
def test_interpret_as_integer_invalid(testvalue: Any):
    testui = UIWithDeterminedOutput(default_guess=testvalue)
    game = Game(testui)
    with pytest.raises(Exception):
        game._interpret_as_integer(testvalue)


# ============================================================================================================================ #
# Test the method Game._get_guess_from_user.                                                                                   #
# ---------------------------------------------------------------------------------------------------------------------------  #
# - [x] Test exist on to many failed attempts.                                                                                 #
# - [x] Test proper feedback.                                                                                                  #
# ============================================================================================================================ #
@pytest.mark.parametrize('max_userinput_attempts', [10, 20, 30])
def test_exist_on_too_many_attempts(max_userinput_attempts: int):
    """Test if the maximum number of user-input attempts are inforced"""
    testui = UIWithDeterminedOutput(default_guess='This is not an integer!')
    game = Game(testui, max_userinput_attempts=max_userinput_attempts)
    with pytest.raises(MaxAttempts):
        game._get_guess_from_user()
    assert testui.n_guess_calls == max_userinput_attempts


def test_provide_proper_feedback():
    """Test if proper feedback are provided when getting a guess from the user."""
    testui = UIWithDeterminedOutput(guess_queue=[
            "This is not an integer", "Neither is this",
            "1.12392", 1.132012, 1e-6,
            1,
            ]
    )
    game = Game(testui)
    game._get_guess_from_user()
    *failed_guess_feedback, last_feedback = testui.feedback_signals
    assert all(signal is Signal.UNACCEPTABLE_ANSWER for signal in failed_guess_feedback), "Did not provide proper signal"
    assert last_feedback is Signal.ANSWER_ACCEPTED, "Did not provide answer accepted signal"


# ============================================================================================================================ #
# Test the method Game._gameloop.                                                                                              #
# ---------------------------------------------------------------------------------------------------------------------------  #
# - [x] Dependency on `max_questions`.                                                                                         #
# - [x] Provide correct feedback.                                                                                              #
#   - [x] Too low                                                                                                              #
#   - [x] Too high                                                                                                             #
#   - [x] Correct                                                                                                              #
#   - [x] Out of range                                                                                                         #
# - [x] Score value                                                                                                            #
# ============================================================================================================================ #
@pytest.mark.parametrize('max_questions', [10, 20, 30, 100])
def test_too_many_guesses(max_questions: int):
    testui = UIWithDeterminedOutput(default_guess=1)
    game = Game(testui, max_questions=max_questions)

    assert game._gameloop(target=10) is None, "Game gave a score but shouldn't since the player lost"
    assert testui.n_guess_calls == max_questions, "Mismatch between number of guesses and number of rounds"


@pytest.mark.parametrize('guess,signal', [
    (1, Signal.GUESS_TOO_LOW),
    (6, Signal.GUESS_TOO_HIGH),
    (5, Signal.CORRECT_GUESS),
    (-1, Signal.OUT_OF_RANGE),
    (20, Signal.OUT_OF_RANGE),
])
def test_feedback_signals(guess: int, signal: Signal):
    TARGET = 5
    MAX_TARGET = 10

    testui = UIWithDeterminedOutput(default_guess=guess)
    game = Game(testui, max_target=MAX_TARGET)

    game._gameloop(TARGET)  # Provide a guess that is too low
    assert testui.feedback_signals[-1] is signal


@pytest.mark.parametrize('expected_score', [1, 12, 15, 234])
def test_score(expected_score: int) -> None:
    """
    Test expected score by making (n-1) wrong guesses
    and then the correct guess. This should yield a score
    of n
    """
    TARGET = 5

    guess_pipeline = (expected_score - 1)*[1] + [TARGET]
    testui = UIWithDeterminedOutput(guess_queue=guess_pipeline)
    game = Game(testui)

    assert expected_score == game._gameloop(TARGET)


# ============================================================================================================================ #
# Test the method Game.run.                                                                                                    #
# ---------------------------------------------------------------------------------------------------------------------------  #
# - [x] Generate random number                                                                                                 #
# - [x] restart UI                                                                                                             #
# - [x] Return score                                                                                                           #
#   - [x] Win                                                                                                                  #
#   - [x] Lose                                                                                                                 #
# ============================================================================================================================ #
class UIWasNotReset(Exception):
    pass


class GameWithMockGameLoop(Game):
    target: int
    ui: UIWithDeterminedOutput
    expected_score: None | int = None
    invoked_random_number_generator = False

    def _gameloop(self, target: int) -> None | int:
        """Mock game loop that returns a predetermined score.
        Also check if the ui has been restarted before running.
        """
        if 0 != self.ui.n_guess_calls:
            raise UIWasNotReset
        self.target = target
        return self.expected_score

    def _generate_random_target_number(self) -> int:
        self.invoked_random_number_generator = True
        return super()._generate_random_target_number()


def test_ui_is_reset_before_playing_game():
    testui = UIWithDeterminedOutput()
    game = GameWithMockGameLoop(testui)

    # Make some guesses to change the state of the UI
    # In this way, the mock game class can check if the
    # UI is reset before _gameloop is ran.
    testui.get_guess("A have nothing to say to you")
    testui.get_guess("A have nothing to say to you")
    testui.get_guess("A have nothing to say to you")

    game.run()


@pytest.mark.parametrize('score', [1, 5, 100, 150])
def test_return_correct_score_on_win(score: int):
    testui = UIWithDeterminedOutput()
    game = GameWithMockGameLoop(testui)
    game.expected_score = score
    assert score == game.run()


def test_return_correct_score_on_lost():
    testui = UIWithDeterminedOutput()
    game = GameWithMockGameLoop(testui)
    assert game.run() is None


def test_invoke_random_number_generator() -> None:
    testui = UIWithDeterminedOutput()
    game = GameWithMockGameLoop(testui)
    game.run()
    assert game.invoked_random_number_generator
