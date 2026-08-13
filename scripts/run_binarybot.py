import matplotlib.pyplot as plt

from numbergame.game import Game
from numbergame.bots import BinarySearchBot
from numbergame.statistics import RunStatistics

bot = BinarySearchBot()
game = Game(bot, maximum_target=1000)

dataset = RunStatistics(BinarySearchBot, [game.run() for _ in range(10_000)])
fig, ax = dataset.plot()
plt.show()
