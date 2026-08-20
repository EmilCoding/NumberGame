import numpy as np
import matplotlib.pyplot as plt

from scipy.optimize import curve_fit

from numbergame.game import Game
from numbergame.bots import BinarySearchBot
from numbergame.statistics import RunStatistics

bot = BinarySearchBot()

dataset: dict[int, RunStatistics] = {}
for gamesize in [10, 50, 100, 500, 1_000, 5_000, 10_000]:
    print(f"Run experiment for gamesize: {gamesize}")
    game = Game(bot, max_target=gamesize)
    dataset[gamesize] = RunStatistics(BinarySearchBot, [game.run() for _ in range(10_000)])
sizes = np.array(list(dataset))
means = np.array([data.mean for data in dataset.values()])
stds = np.array([data.std for data in dataset.values()])


# Fit to logarithmic model
x = np.linspace(sizes.min(), sizes.max())


def fitfunc(log2x, a: float, b: float):
    return a*log2x + b


(a, b), pcov, *_ = curve_fit(fitfunc, np.log2(sizes), means, sigma=stds)


fig, ax = plt.subplots()
ax.plot(x, a*np.log2(x) + b, label=f'f(x) = {a:0.2f} $\\log_2(x)$ + {b:0.2f}')
ax.errorbar(sizes, means, stds, label='Data', linestyle='', marker='o')
ax.set_xscale('log')
ax.set_xlabel('Size of guess interval')
ax.set_ylabel('Average number of guesses')
ax.set_title('Performance of the binary search strategy')
ax.legend()
ax.grid(True)
plt.show()
