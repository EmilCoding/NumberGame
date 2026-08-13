import math
import dataclasses
import matplotlib.pyplot as plt

from typing import NamedTuple
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from numbergame.bots import Bot


class QuartilesInfo(NamedTuple):
    minimum: float
    quarentile_25: float
    median: float
    quarentile_75: float
    maximum: float


@dataclasses.dataclass
class RunStatistics:
    bottype: str | type[Bot]
    raw_data: list[None | int] = dataclasses.field(repr=False)

    n_total: int = dataclasses.field(init=False)
    n_sucess: int = dataclasses.field(init=False)
    filtered_data: list[int] = dataclasses.field(repr=False, init=False)

    mean: float = dataclasses.field(init=False)
    std: float = dataclasses.field(init=False)
    quarentiles: QuartilesInfo = dataclasses.field(init=False)
    completion_percentage: float = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        self.bottype = self.bottype.__name__ if isinstance(self.bottype, type) else self.bottype
        self.filtered_data = sorted(filter(None, self.raw_data))

        self.n_total = len(self.raw_data)
        self.n_sucess = len(self.filtered_data)
        self.completion_percentage = 100 * self.n_sucess / self.n_total

        self.mean = mean(self.filtered_data)
        self.std = std(self.filtered_data, self.mean)
        self.quarentiles = quarenties(self.filtered_data)

    def plot(
        self,
        fig: None | Figure = None,
        ax: None | Axes = None,
    ) -> tuple[Figure, Axes]:
        fig = fig or plt.figure()
        ax = ax or fig.gca()

        ax.hist(self.filtered_data)
        ax.set_xlabel('Number of runs')
        ax.set_ylabel('Probability density function')
        ax.set_title(f'Performance of {self.bottype} - Completion {self.completion_percentage:0.0f} %')

        _, q25, median, q75, __ = self.quarentiles
        ax.axvline(q25, label='Q25', linestyle='--', color='black')
        ax.axvline(median, label='Median', linestyle='-', color='black')
        ax.axvline(q75, label='Q75', linestyle='--', color='black')

        return fig, ax


def mean(numbers: list[int] | list[float]) -> float:
    if 0 == (n_elements := len(numbers)):
        raise ValueError('Cannot compute average of empty sequence')
    return sum(numbers) / n_elements


def std(numbers: list[int] | list[float], /, __mean: None | float = None) -> float:
    if 0 == (n_elements := len(numbers)):
        raise ValueError('Cannot compute standard deviation of empty sequence')
    if 1 == n_elements:
        raise ValueError('Cannot compute standard deviation of a single number')

    __mean = __mean or mean(numbers)
    variance = sum((x - __mean)**2 for x in numbers) / (n_elements - 1)
    return math.sqrt(variance)


def quarenties(numbers: list[int] | list[float]) -> QuartilesInfo:
    n_points = len(numbers)
    sorted_numbers = sorted(numbers)
    return QuartilesInfo(
        sorted_numbers[0],
        sorted_numbers[n_points//4],
        sorted_numbers[n_points//2],
        sorted_numbers[3*n_points//4],
        sorted_numbers[-1],
    )


if __name__ == '__main__':
    from numbergame import Game
    from numbergame.bots import BinarySearchBot

    bot = BinarySearchBot(output_to_terminal=True)
    game = Game(bot, maximum_target=100)

    sample = [game.run() for _ in range(100)]

    stats = RunStatistics(type(bot), sample)
    stats.plot()
    plt.show()
