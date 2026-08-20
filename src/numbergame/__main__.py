"""Run a game using the standard settings."""
from numbergame.game import Game
from numbergame.player import CLI

player = CLI()
Game(player).run()
