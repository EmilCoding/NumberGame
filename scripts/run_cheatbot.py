import matplotlib.pyplot as plt

from numbergame.bots import CheatBot
from numbergame.statistics import run_experiment

dataset = run_experiment(CheatBot, 1_000, 10_000)
fig, ax, _ = dataset.plot()
plt.show()
