import matplotlib.pyplot as plt

from numbergame.game import Game
from numbergame.bots import CheatBot
from numbergame.statistics import RunStatistics

bot = CheatBot()
game = Game(bot, max_target=1000)

dataset = RunStatistics(CheatBot, [game.run() for _ in range(10_000)])
fig, ax = dataset.plot()
plt.show()
