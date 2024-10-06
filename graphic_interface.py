import pyglet
import json
from pyglet.window import key
from source.graphic_interface_lib.InfoLabel import InfoLabel
from source.graphic_interface_lib.Character import Character
from source.graphic_interface_lib.Area import Area


window = pyglet.window.Window(1920, 1080)
keys = pyglet.window.key.KeyStateHandler()
window.push_handlers(keys)
batch = pyglet.graphics.Batch()


info = InfoLabel("Entity inspector", (0, window.height), batch=batch)
data_receive_buffer = ""

entity_focus = None
area_list = [
    Area("street", (900, 800), batch=batch),
    Area("parc", (200, 400), batch=batch),
    Area("work", (600, 400), batch=batch),
    Area("restaurant", (1200, 400), batch=batch)
]
player_list = [Character((-200, -200), batch=batch) for _ in range(20)]



def update_character_data(player_list, data_list):
    for player in player_list:
        player.data = None
    for player, player_data in zip(player_list, data_list):
        player.data = player_data
    for i, player in enumerate(player_list):
        if player.data != None:
            player.position = (200 + 110 * i, 700)
        else:
            player.position = (-200, -200)


def update_character(player_list, data_receive_buffer: str):
    data_receive_buffer += get_info("core_to_graphic_interface.txt")
    if "\n" in data_receive_buffer:
        str_data = data_receive_buffer.split("\n")[-2]
        if str_data != "":
            data_list = [json.loads(str_client_data.replace("None", "\"None\"").replace("\'", "\"")) for str_client_data in str_data.split("|")]
            update_character_data(player_list, data_list)
        data_receive_buffer = data_receive_buffer.split("\n")[-1]


def update_area(area_list, player_list):
    for area in area_list:
        area.reset_player_list()
        for player in filter(lambda player: player.data != None, player_list):
            if player.data["location"] == area.name:
                area.add_player(player)
        area.move_player()


def get_info(filename):
    f = open(filename, "r+")
    txt = f.read()
    f.truncate(0)
    f.close()
    return txt


def check_collision(x, y, player):
    rec = player.rectangle
    return rec.x+rec.width < x < rec.x and rec.y+rec.height < y < rec.y



def update(dt):
    update_character(player_list, data_receive_buffer)
    update_area(area_list, player_list)
    info.update_info(entity_focus)


@window.event
def on_draw():
    for player in player_list:
        player.draw()
    window.clear()
    batch.draw()


@window.event
def on_mouse_press(x, y, button, modifiers):
    global entity_focus

    if button != 1:
        return
    for player in player_list:
        if check_collision(x, y, player):
            entity_focus = player


pyglet.clock.schedule_interval(update, 1/60.0)
pyglet.app.run()
