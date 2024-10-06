from random import randint
from pyglet import shapes
import pyglet.text


class Area():
    def __init__(self, name, position=(100, 100), batch=None):
        self._position = position
        self.batch = batch
        color = (randint(50, 255), randint(50, 255), randint(50, 255))
        self.name = name
        self.player_list = []
        self.rectangle = shapes.Rectangle(position[0], position[1], 300, -300, color=color, batch=batch)
        self.label = pyglet.text.Label(name, x=position[0], y=position[1]+10, font_size=12, batch=batch)

    def add_player(self, player):
        self.player_list.append(player)

    def move_player(self):
        for i, player in enumerate(self.player_list):
            player.position = (self.position[0] + 100 + i*120, self.position[1] - 40)

    def reset_player_list(self):
        self.player_list = []

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, val):
        self._position = val
        self.rectangle.x = val[0]
        self.rectangle.y = val[1]
        self.label.x = val[0]
        self.label.y = val[1] + 10
