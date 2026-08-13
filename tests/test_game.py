"""
Test the flow of a game.


Features:

- [ ] Generate a target number
- [ ] Input should be recieved
- [ ] Output should be recieved
- [x] Logic should be handelled correctly
    - [x] Too low
    - [x] Too high
    - [x] Perfect
- [x] Too many attempts
"""
import pytest
from numbergame.game import MaxAttempts, game


def test_game_logic() -> None:
    output_pipeline = [-1, 1000, 1]
    def getinput() -> int:
        return output_pipeline.pop(0)

    # Define output function such that last output is saved in local variable.
    expected_output = [
        'Guess -1 was too low',
        'Guess 1000 was too high',
    ]
    def getoutput(message: str) -> None:
        assert message == expected_output.pop(0)

    assert 3 == game(getinput, getoutput, max_target = 1)


@pytest.mark.parametrize('max_attempts', [5, 10, 100])
def test_too_many_attempts(max_attempts: int) -> None:
    def getinput() -> int: return -1
    output_buffer: list[str] = []
    def getoutput(message: str) -> None:
        output_buffer.append(message)
    assert None == game(getinput, getoutput, max_question=max_attempts)
    assert max_attempts == len(output_buffer)
