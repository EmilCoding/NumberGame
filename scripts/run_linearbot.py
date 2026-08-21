import matplotlib.pyplot as plt

from numbergame.bots import LinearSearchBot
from numbergame.statistics import run_experiment

dataset = run_experiment(LinearSearchBot, 1_000, 10_000)
fig, ax, _ = dataset.plot()
plt.show()