import matplotlib.pyplot as plt

from numbergame.game import Game
from numbergame.bots import LinearSearchBot
from numbergame.statistics import RunStatistics

bot = LinearSearchBot()
game = Game(bot, maximum_target=1000)

dataset = RunStatistics(LinearSearchBot, [game.run() for _ in range(10_000)])
fig, ax = dataset.plot()
plt.show()
