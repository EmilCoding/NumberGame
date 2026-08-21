import matplotlib.pyplot as plt

from numbergame.bots import BinarySearchBot
from numbergame.statistics import run_experiment

dataset = run_experiment(BinarySearchBot, 1_000, 10_000)
fig, ax, _ = dataset.plot()
plt.show()