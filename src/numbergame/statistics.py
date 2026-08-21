import math
import time
import itertools
import dataclasses
import matplotlib.pyplot as plt

from typing import Any, NamedTuple
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from numbergame.bots import Bot
from numbergame.game import Game


class QuartilesInfo[Number: int | float](NamedTuple):
    min: Number
    q25: Number
    median: Number
    q75: Number
    max: Number


@dataclasses.dataclass
class RunStatistics:
    """Dataclass containin statistical information on the performance of a `Bot`"""
    bottype: str | type[Bot]
    max_target: int
    max_questions: int
    raw_data: list[None | int] = dataclasses.field(repr=False)

    n_total: int = dataclasses.field(init=False)
    n_sucess: int = dataclasses.field(init=False)
    completion_percentage: float = dataclasses.field(init=False)
    filtered_data: list[int] = dataclasses.field(repr=False, init=False)

    # Statistical quantities
    mean: float = dataclasses.field(init=False, doc="Average score from winning runs")
    std: float = dataclasses.field(init=False, doc="Standard deviation in scores from winning runs")
    quarentiles: QuartilesInfo = dataclasses.field(init=False, doc='Quarenties of winning runs')

    def __post_init__(self) -> None:
        self.bottype = self.bottype.__name__ if isinstance(self.bottype, type) else self.bottype
        self.filtered_data = sorted(filter(None, self.raw_data))

        self.n_total = len(self.raw_data)
        self.n_sucess = len(self.filtered_data)
        self.completion_percentage = round(100 * self.n_sucess / self.n_total, 2)

        self.mean = round(mean(self.filtered_data), 2)
        self.std = round(std(self.filtered_data, self.mean), 2)
        self.quarentiles = quarenties(self.filtered_data)

    def plot(self, fig: None | Figure = None, ax: None | Axes = None, **options) -> tuple[Figure, Axes, tuple[Any, Any]]:
        fig = fig or plt.figure()
        ax = ax or fig.gca()

        count, bins, _ = ax.hist(self.filtered_data, **options)
        ax.set_xlabel('Number of guesses')
        ax.set_ylabel('Count')
        ax.set_title(f'Performance of {self.bottype} - Completion {self.completion_percentage} %')

        _, q25, median, q75, __ = self.quarentiles
        ax.axvline(q25, label='Q25', linestyle='--', color='black')
        ax.axvline(median, label='Median', linestyle='-', color='orange')
        ax.axvline(q75, label='Q75', linestyle='--', color='black')

        return fig, ax, (count, bins)


def run_experiment(
    bottype: type[Bot],
    max_target: int,
    total_runs: int,
    /,
    verbose: bool = True,
    batchsize: int = 1_000,
    **kwargs: Any,
) -> RunStatistics:
    """Gather data on the performance on a given game. The games are batched in groupes."""
    n_batches = math.ceil(total_runs / batchsize)
    batch_results: list[list[None | int]] = []

    game = Game(bottype(), max_target=max_target, **kwargs)
    for i, run_indices in enumerate(itertools.batched(range(total_runs), batchsize), start=1):
        start = time.perf_counter()
        batch_results.append([game.run() for i in run_indices])
        end = time.perf_counter()
        if verbose:
            print(f"Finished running batch {i}/{n_batches} in {end - start:0.2f} seconds.")

    results = sum(batch_results, start=[])
    return RunStatistics(bottype, max_target, game.max_questions, results)


def performance_scaling(
    bottype: type[Bot],
    sizes: list[int],
    runs_per_size: int,
    /,
    verbose: bool = True,
    **kwargs: Any,
) -> list[RunStatistics]:
    """Run experiments on using different values of max-target."""
    results = []
    for max_target in sizes:
        start = time.perf_counter()
        stats = run_experiment(bottype, max_target, runs_per_size, verbose=False, **kwargs)
        end = time.perf_counter()
        results.append(stats)
        if verbose:
            print(f"Finished gathering data for {max_target=} - Finished in {end - start:0.2f} seconds.")

    return results


def mean[Number: int | float](numbers: list[Number]) -> float:
    """Calculate the mean of a non-empty list of numbers"""
    if 0 == (n_elements := len(numbers)):
        raise ValueError('Cannot compute average of empty sequence')
    return sum(numbers) / n_elements


def std[Number: int | float](numbers: list[Number], /, __mean: None | float = None) -> float:
    """Calculate the standard deviation of list of two or more numbers.

    Args:
        numbers (list[int | float]): List of numbers.
        __mean (None | float, optional): Provide a mean value if known in advance.
        If no value is provided, the mean is calculated on run-time. Defaults to None.

    Raises:
        IndexError: If list is empty.
        IndexError: If list only contains a single number

    Returns:
        float: Computed standard deviation as a float.
    """
    match n_elements := len(numbers):
        case 0:
            raise IndexError('Cannot compute standard deviation of empty sequence')
        case 1:
            raise ValueError('Cannot compute standard deviation of a single number')

    __mean = __mean or mean(numbers)
    variance = sum((x - __mean)**2 for x in numbers) / (n_elements - 1)
    return math.sqrt(variance)


def quarenties[Number: int | float](numbers: list[Number]) -> QuartilesInfo[Number]:
    """Calculate the quarenties of a list of numbers."""
    n_points = len(numbers)
    sorted_numbers = sorted(numbers)
    return QuartilesInfo(
        sorted_numbers[0],
        sorted_numbers[n_points // 4],
        sorted_numbers[n_points // 2],
        sorted_numbers[3 * n_points // 4],
        sorted_numbers[-1],
    )


if __name__ == '__main__':
    from numbergame import Game
    from numbergame.bots import BinarySearchBot

    fig, axes = plt.subplots(1, 2)

    # Single size run
    print(stats := run_experiment(BinarySearchBot, 1_000, 1_000))
    stats.plot(fig, axes[0])

    # Scaling
    run_statistics = performance_scaling(BinarySearchBot,
                                         [100, 500, 1000, 1500, 5000, 10000],
                                         10_000
                                         )
    axes[1].plot([stats.max_target for stats in run_statistics],
                 [stats.mean for stats in run_statistics],
                 'o'
                 )

    plt.show()
