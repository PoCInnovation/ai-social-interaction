import pyglet
from pyglet import shapes


class InfoLabel:
    def __init__(self, text="placeholder", position=(0, 0), batch=None, visible=True):
        self._text = text
        self._position = position
        self.width = max(len(line) for line in text.split("\n")) * 11
        self.rectangle1 = shapes.Rectangle(position[0] - 2, position[1] + 2, self.width+14, -200, color=(255, 255, 255), batch=batch)
        self.rectangle2 = shapes.Rectangle(position[0], position[1], self.width+10, -196, color=(0, 0, 0), batch=batch)
        self.label = pyglet.text.Label(text, x=position[0]+5, y=position[1]-20, font_size=15, width=self.width, multiline=True, batch=batch)
        self._visible = visible
        self.visible = visible
    
    def update_info(self, entity):
        if entity == None:
            return
        self.text = str(entity.data)
    
    @property
    def position(self):
        return self._position
    
    @position.setter
    def position(self, val):
        self.__position = val
        self.rectangle1.x = val[0] - 2
        self.rectangle1.y = val[1] + 2
        self.rectangle2.x = val[0]
        self.rectangle2.y = val[1]
        self.label.x = val[0] + 5
        self.label.y = val[1] - 20
    
    @property
    def text(self):
        return self._text
    
    @text.setter
    def text(self, val):
        self._text = val
        self.width = max(len(line) for line in val.split("\n")) * 11
        self.rectangle1.width = self.width + 14
        self.rectangle2.width = self.width + 10
        self.label.width = max(self.width, 10)
        self.label.text = val
    
    @property
    def visible(self):
        return self._visible
    
    @visible.setter
    def visible(self, val):
        self._visible = val
        self.rectangle1.visible = val
        self.rectangle2.visible = val
        self.label.visible = val
