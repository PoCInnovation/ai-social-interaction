##
## POC Project, 2024
## Social Interaction
## File description: core
## core
##

import json

BUFFER_SIZE = 1024

INVALID_ACTION = "The action you sent is not valid"
INVALID_DISCUSSION_GROUP = "The discussion group you sent is invalid"
INVALID_LOCATION = "The location you sent is invalid"
INVALID_SENDER = "The sender is invalid or missing"
MISSING_ARGUMENTS = "The message is missing required arguments"
ERROR_MESSAGE = "There is one or multiple errors in the message you sent"
ZONE_ERROR = "There is an error with your current zone"
PERSON_ERROR = "The person you are trying to talk to does not exist or is currently not in your zone"

class Core:
    def __init__(self) -> None:
        self.current_time = 0
        self.clients = []
        self.client_socket_map = {}
        self.places = {
            "parc": [],
            "street": [],
            "work": [],
            "restaurant": [],
            "market": [],
            "school": []
        }

    def send_message(self, socket, message):
        print(f"Envoi de: {message}")
        message_header = f"{len(message):<{BUFFER_SIZE}}"
        socket.send(bytes(message_header, 'utf-8') + bytes(message, 'utf-8'))

    def send_message_to_client(self, target_client_name, message):
        place = self.get_current_place(target_client_name)
        group_participants = ""
        place_participants = ""

        if ((self.get_current_discussion_group(target_client_name))):
            group_participants = ", ".join(self.get_current_discussion_group(target_client_name))
        if ((self.get_current_place_participants(target_client_name))):
            place_participants = ", ".join(self.get_current_place_participants(target_client_name))

        message = f"You are in the {place} with {place_participants} Your current chat groupe is with {group_participants}\n{message}" # it's {self.current_time} time\n{message}"

        for client_socket, client_name in self.client_socket_map.items():
            if str(client_name).lower() == str(target_client_name).lower():
                try:
                    message_header = f"{len(message):<{BUFFER_SIZE}}".encode('utf-8')
                    client_socket.send(message_header + message.encode('utf-8'))
                    return True
                except:
                    return False
        return False

    # Execute finished actions
    def execute_finished_actions(self, current_time):
        self.current_time = current_time

        for client in self.clients:
            if client["current_action"] != None and client["current_action"]["execution_time"] == current_time:
                client["current_action"]["function"](client["current_action"]["data"])
                client["current_action"] = None

    # Ask actions to do
    def ask_actions_to_do(self, clients: dict):
        self.client_socket_map = clients.copy()

        for client in self.clients:
            if client["current_action"] == None:
                print(f"{client['name']} IL FAIT RIEN")
                self.send_message_to_client(client["name"], "WHAT ACTION DO YOU WANT TO DO ?")

    def add_new_user(self, user):
        self.places["street"].append([user])
        self.clients.append({"name": user, "current_action": None})

    def process(self, notified_socket, request: str, updated_clients, current_time):
        self.current_time = current_time
        self.client_socket_map = updated_clients.copy()
    
        # Verify if the json file is complete
        try:
            data: dict = json.loads(request)
        except json.JSONDecodeError:
            self.send_message(notified_socket, ERROR_MESSAGE)
            return

        actions_dict = {
            "go_to_location": self.go_to_location,
            "join_group": self.join_group,
            "speak_in_group": self.speak_in_group,
        }

        if not data.get("sender"):
            self.send_message(notified_socket, INVALID_SENDER)
            return

        if data.get("action") not in actions_dict:
            self.send_message_to_client(data["sender"], INVALID_ACTION)
            return

        if not self.validate_arguments(data):
            self.send_message_to_client(data["sender"], MISSING_ARGUMENTS)
            return

        action = actions_dict[data["action"]]
        action(data, current_time)




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
        return []

    # Remove Sender From his current discussion group
    def remove_from_current_group(self, sender: str):
        discussion_group = self.get_current_discussion_group(sender)
        if discussion_group is not None:
            discussion_group.remove(sender)

    # Destroy discussion group when nobody is inside
    def clean_useless_discussion_groups(self):
        for place in self.places:
            self.places[place] = [group for group in self.places[place] if group]





    # Sender go to an specific location
    def go_to_location(self, data: dict, current_time: int):

        GO_TO_LOCATION_TIME = 2

        location = data.get("location").lower()
        if location in self.places:
            for client in self.clients:
                if client["name"].lower() == data["sender"].lower():
                    self.remove_from_current_group(data["sender"])
                    client["current_action"] = {"name": "go to location", "execution_time": current_time + GO_TO_LOCATION_TIME, "data": data, "function": self.execute_go_to_location}
            self.send_message_to_client(data["sender"], f"You start moving to {location}")
        else:
            self.send_message_to_client(data["sender"], INVALID_LOCATION)

    def execute_go_to_location(self, data):
        for client in self.clients:

            if client["name"].lower() == data["sender"].lower():
                client["current_action"] = None
        location = data.get("location").lower()
        self.places[location].append([data["sender"]])
        self.send_message_to_client(data["sender"], f"You moved successfully to {location}")



    # Sender join an specific discussion group
    def join_group(self, data: dict, current_time: int):
        for place in self.places:
            for discussion_group in self.places[place]:
                if data["group_to_join"] in discussion_group:
                    self.remove_from_current_group(data["sender"])
                    discussion_group.append(data["sender"])
                    for neighbor in discussion_group:
                        self.send_message_to_client(neighbor, f"{data['sender']} joined your discussion group")
                    self.send_message_to_client(data["sender"], f"You moved successfully to {data['group_to_join']}'s discussion group")
                    return
        self.send_message_to_client(data["sender"], INVALID_DISCUSSION_GROUP)




    # Sender speak in his current discussion group
    def speak_in_group(self, data: dict, current_time: int):
        discussion_group = self.get_current_discussion_group(data["sender"])
        if discussion_group is None:
            self.send_message_to_client(data["sender"], INVALID_DISCUSSION_GROUP)
            return
        for neighbor in discussion_group:
            self.send_message_to_client(neighbor, f"{data['sender']} said: '{data['message']}'")
