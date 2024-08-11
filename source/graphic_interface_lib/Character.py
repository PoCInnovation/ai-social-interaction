from random import randint
from pyglet import shapes
import pyglet.text


class Character():
    def __init__(self, position=(0, 0), batch=None):
        self._position = position
        self.batch = batch
        color = (randint(50, 255), randint(50, 255), randint(50, 255))
        self.rectangle = shapes.Rectangle(position[0], position[1], -100, -100, color=color, batch=batch)
        self.label = pyglet.text.Label("", x=0, y=0, font_size=12, batch=batch)
        self.data = None
    
    def draw(self):
        if self.data == None or self.data["name"] == None:
            self.label.position = (-200, -200, 0)
            return
        self.label.position = (self.position[0] - 100, self.position[1] + 10, 0)
        self.label.text = self.data["name"]

    @property
    def position(self):
        return self._position
    
    @position.setter
    def position(self, val):
        self._position = val
        self.rectangle.x = val[0]
        self.rectangle.y = val[1]
