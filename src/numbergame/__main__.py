"""Run a game using the standard settings."""
from numbergame.game import Game, PlayerUI

player = PlayerUI()
Game(player).run()
