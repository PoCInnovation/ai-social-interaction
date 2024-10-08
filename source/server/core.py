from dotenv import load_dotenv
import logging
import random
import json
import sys
import os
import random
import logging
from datetime import datetime

logging.basicConfig(
    filename="./logs/" + datetime.now().strftime("%m-%d-%Y_%H:%M") + ".log",
    encoding="utf-8",
    filemode="w",
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    level=logging.DEBUG
)
logging.info("program start")

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DataConfig

from dotenv import load_dotenv

load_dotenv()



def cp_dict(value):
    if not isinstance(value, dict):
        return value
    return {key:cp_dict(val) for key, val in value.items()}



class Core:
    def __init__(self, debug = False) -> None:
        self.debug = debug
        self.current_time = 0
        self.clients = []
        self.client_socket_map = {}
        self.places = {
            #"parc": [],
            "street": [],
            #"work": [],
            "restaurant": [],
            #"market": [],
            #"school": []
        }
        with open(os.path.dirname(__file__) + "/descriptions.txt", "r") as description_file:
            self.descriptions = description_file.read().split("\n")

    def process(self, notified_socket, request: str, updated_clients, current_time):
        self.current_time = current_time
        self.client_socket_map = updated_clients.copy()

        # Verify if the json file is complete
        try:
            data: dict = json.loads(request)
        except json.JSONDecodeError:
            self.send_message(notified_socket, DataConfig.ERROR_MESSAGE)
            return

        actions_dict = {
            "go_to_location": self.go_to_location,
            "join_group": self.join_group,
            "speak_in_group": self.speak_in_group,
        }

        if not data.get("sender"):
            self.send_message(notified_socket, DataConfig.INVALID_SENDER)
            return

        if data.get("action") not in actions_dict:
            self.send_message_to_client(data["sender"], DataConfig.INVALID_ACTION)
            return

        if not self.validate_arguments(data):
            self.send_message_to_client(data["sender"], DataConfig.MISSING_ARGUMENTS)
            return

        action = actions_dict[data["action"]]
        action(data, current_time)

    def send_message(self, socket, message):
        self.print_debug(f"Envoi: {message}")
        message_header = f"{len(message):<{DataConfig.BUFFER_SIZE}}"
        socket.send(bytes(message_header, 'utf-8') + bytes(message, 'utf-8'))

    def send_message_to_client(self, target_client_name, message):
        self.print_debug(f"Envoi a {target_client_name}: {message}")
        place = self.get_current_place(target_client_name)

        group_participants = ""
        place_participants = ""

        if (self.get_current_discussion_group(target_client_name)) != None:
            for group_participant in self.get_current_discussion_group(target_client_name):
                if (group_participant != target_client_name):
                    group_participants += group_participant + ", "

        if (self.get_current_place_participants(target_client_name)) != None:
            for place_participant in self.get_current_place_participants(target_client_name):
                if (place_participant != target_client_name):
                    place_participants += place_participant + ", "
        
        if group_participants == "":
            group_participants = "Nobody"
        if (place_participants) == "":
            place_participants = "Nobody"

        if (place == None):
            return

        rm = message
        message = f"You are in the {place} the persons in your current zone are {place_participants} " # it's {self.current_time} time\n{message}"

        if group_participants != "Nobody":
            message = f"{message}but your current discussion groupe is composed of {group_participants}\n{rm}"
        else:
            message = f"{message}but you are currently alone in your discussion group\n{rm}"

        for client_socket, client_name in self.client_socket_map.items():
            if str(client_name).lower() == str(target_client_name).lower():
                try:
                    message_header = f"{len(message):<{DataConfig.BUFFER_SIZE}}".encode('utf-8')
                    client_socket.send(message_header + message.encode('utf-8'))
                    return True
                except:
                    return False
        return False

    # Execute finished actions
    def execute_finished_actions(self, current_time):
        self.current_time = current_time

        print("-"*10, "Current_time:", current_time, "-"*10)
        for client in self.clients:
            self.print_client_info(client, current_time)
            if client["current_action"] != None and client["current_action"]["execution_time"] == current_time:
                client["current_action"]["function"](client["current_action"]["data"])
                client["current_action"] = None

    # Ask actions to do
    def ask_actions_to_do(self, clients: dict):
        self.client_socket_map = clients.copy()
        for client in self.clients:
            if client["current_action"] == None:
                self.send_message_to_client(client["name"], "WHAT ACTION DO YOU WANT TO DO ?")

    def add_new_user(self, user):
        self.places["street"].append([user.lower()])
        self.clients.append({"name": user.lower(), "current_action": None})

    # Verify if the json file is complete
    def validate_arguments(self, data: dict) -> bool:
        action = data.get("action")
        if action == "go_to_location":
            return "location" in data
        elif action == "join_group":
            return "group_to_join" in data
        elif action == "speak_in_group":
            return "message" in data
        return False

    # Get The current discussion group of the sender
    def get_current_discussion_group(self, sender: str) -> list:
        for place in self.places:
            for discussion_group in self.places[place]:
                if sender in discussion_group:
                    return discussion_group
        return None

    # Get The current place group of the sender
    def get_current_place(self, sender: str) -> str:
        for place in self.places:
            for discussion_group in self.places[place]:
                if sender in discussion_group:
                    return place
        return None

    # Get the current place's participans
    def get_current_place_participants(self, sender: str) -> str:
        people = []
        for place in self.places:
            for discussion_group in self.places[place]:
                for entity in discussion_group:
                    people.append(entity)
        return people

    # Remove Sender From his current discussion group
    def remove_from_current_group(self, sender: str):
        discussion_group = self.get_current_discussion_group(sender)
        if discussion_group is not None:
            discussion_group.remove(sender)

    # Destroy discussion group when nobody is inside
    def clean_useless_discussion_groups(self):
        for place in self.places:
            self.places[place] = [group for group in self.places[place] if group]

    def get_new_description(self):
        if (len(self.descriptions) != 0):
            description = self.descriptions.pop(random.randint(0, len(self.descriptions) - 1))
        else:
            description = "Tobby:You'r a shy guy, you don't speak a lot"
        return tuple(description.split(":"))

    def print_debug(self, *args, **kwargs):
        logging.debug(*args)
        if self.debug:
            print(*args, **kwargs)

    def print_client_info(self, client, current_time):
        if client["current_action"] != None:
            print(f"{client['name']} | ", end="")
            print(', '.join(str(key)+': '+str(value) for key, value in client['current_action']['data'].items() if value and key != 'sender'), end="")
            print(f" | time left: {client['current_action']['execution_time'] - current_time}")
        else:
            print(f"{client['name']} | do nothing")

    def transfer_info(self):
        clients_data = [cp_dict(client_data) for client_data in self.clients]
        f = open("core_to_graphic_interface.txt", "a")
        for client in clients_data:
            if client["current_action"] != None and client["current_action"]["function"] != None:
                del client["current_action"]["function"]
        f.write("|".join(map(str, clients_data))+"\n")
        f.close()

    def remove_client(self, client_name):
        for i in range(len(self.clients)):
            if self.clients[i]["name"] == client_name:
                del self.clients[i]


    # Sender go to an specific location
    def go_to_location(self, data: dict, current_time: int):

        GO_TO_LOCATION_TIME = 2

        location = data.get("location").lower()
        data["sender"] = data["sender"].lower()
    
        if location in self.places:
            for client in self.clients:
                if client["name"].lower() == data["sender"].lower():
                    self.remove_from_current_group(data["sender"])
                    client["current_action"] = {"name": "go to location", "execution_time": current_time + GO_TO_LOCATION_TIME, "data": data, "function": self.execute_go_to_location}
                    client["location"] = "street"

            self.send_message_to_client(data["sender"], f"You start moving to {location}")
        else:
            self.send_message_to_client(data["sender"], DataConfig.INVALID_LOCATION)

    def execute_go_to_location(self, data):

        for client in self.clients:
            if client["name"].lower() == data["sender"]:
                client["current_action"] = None
                client["location"] = data["location"]
        location = data.get("location").lower()
        self.places[location].append([data["sender"]])
        self.send_message_to_client(data["sender"], f"You moved successfully to {location}")




    # Sender join an specific discussion group
    def join_group(self, data: dict, current_time: int):

        JOIN_GROUP_TIME = 1

        data["sender"] = data["sender"].lower()
        data["group_to_join"] = data["group_to_join"].lower()

        print(self.places)

        for place in self.places:
            for discussion_group in self.places[place]:
                if data["group_to_join"] in discussion_group:
                    for client in self.clients:
                        if client["name"].lower() == data["sender"]:
                            self.remove_from_current_group(data["sender"])
                            client["current_action"] = {"name": "join_group", "execution_time": current_time + JOIN_GROUP_TIME, "data": data, "function": self.execute_join_group}
                            self.send_message_to_client(data["sender"], f"You start moving to {data['group_to_join']}'s discussion group")
                            return        
        self.send_message_to_client(data["sender"], DataConfig.INVALID_DISCUSSION_GROUP)

    # Execute Join discussion group
    def execute_join_group(self, data: dict):
        for place in self.places:
            for discussion_group in self.places[place]:
                if data["group_to_join"] in discussion_group:
                    discussion_group.append(data["sender"])
                    for neighbor in discussion_group:
                        self.send_message_to_client(neighbor, f"{data['sender']} joined your discussion group")
                    self.send_message_to_client(data["sender"], f"You moved successfully to {data['group_to_join']}'s discussion group")
                    return
        self.send_message_to_client(data["sender"], DataConfig.INVALID_DISCUSSION_GROUP)


    # Sender speak in his current discussion group
    def speak_in_group(self, data: dict, current_time: int):

        SPEAK_IN_GROUP_TIME = 1

        data["sender"] = data["sender"].lower()

        for client in self.clients:
            if client["name"].lower() == data["sender"]:
                client["current_action"] = {"name": "speak_in_group", "execution_time": current_time + SPEAK_IN_GROUP_TIME, "data": data, "function": self.execute_speak_in_group}



    def execute_speak_in_group(self, data: dict):
        discussion_group = self.get_current_discussion_group(data["sender"])
        if discussion_group is None:
            self.send_message_to_client(data["sender"], DataConfig.INVALID_DISCUSSION_GROUP)
            return
        print(f"--------------------{len(discussion_group)}------------------")
        if len(discussion_group) == 1:
            self.send_message_to_client(data["sender"], DataConfig.NO_CURRENT_DISCUSSION_GROUP)
            return
        for neighbor in discussion_group:
            if neighbor != data["sender"]:
                self.send_message_to_client(neighbor, f"{data['sender']} said: '{data['message']}'")
