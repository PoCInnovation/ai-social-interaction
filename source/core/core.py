##
## POC Project, 2024
## Social Interaction
## File description: core
## core
##
import json

INVALID_ACTION = "The action you sent is not valid"
INVALID_DISCUSSION_GROUP = "The discussion group you sent is invalid"
INVALID_LOCATION = "The location you sent is invalid"
INVALID_SENDER = "The sender is invalid or missing"
MISSING_ARGUMENTS = "The message is missing required arguments"
ERROR_MESSAGE = "There is one or multiple errors in the message you sent"
ZONE_ERROR = "There is an error with your current zone"
PERSON_ERROR = "The person you are trying to talk to does not exist or is currently not in your zone"

def send_message(receiver: str, request: str):
    print(f"receiver: {receiver}\n{request}\n")

class Core:
    def __init__(self) -> None:
        self.places = {
            "parc": [],
            "street": [],
            "work": [],
            "restaurant": [],
            "market": [],
            "school": []
        }

    # Verify if the json file is complete
    def process(self, request: str):
        try:
            data: dict = json.loads(request)
        except json.JSONDecodeError:
            print(ERROR_MESSAGE)
            return

        actions_dict = {
            "go_to_location": self.go_to_location,
            "join_group": self.join_group,
            "speak_in_group": self.speak_in_group,
        }

        if not data.get("sender"):
            print(INVALID_SENDER)
            return

        if data.get("action") not in actions_dict:
            send_message(data["sender"], INVALID_ACTION)
            return

        if not self.validate_arguments(data):
            send_message(data["sender"], MISSING_ARGUMENTS)
            return

        action = actions_dict[data["action"]]
        action(data)

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

    # Remove Sender From his current discussion group
    def remove_from_current_group(self, sender: str):
        discussion_group = self.get_current_discussion_group(sender)
        if discussion_group is not None:
            discussion_group.remove(sender)

    # Destroy discussion group when nobody is inside
    def clean_useless_discussion_groups(self):
        for place in self.places:
            self.places[place] = [group for group in self.places[place] if group]

    # Send go to an specific location
    def go_to_location(self, data: dict):
        self.remove_from_current_group(data["sender"])
        location = data.get("location")
        if location in self.places:
            self.places[location].append([data["sender"]])
            send_message(data["sender"], f"You moved successfully to {location}")
        else:
            send_message(data["sender"], INVALID_LOCATION)

    # Sender join an specific discussion group
    def join_group(self, data: dict):
        for place in self.places:
            for discussion_group in self.places[place]:
                if data["group_to_join"] in discussion_group:
                    self.remove_from_current_group(data["sender"])
                    discussion_group.append(data["sender"])
                    for neighbor in discussion_group:
                        send_message(neighbor, f"{data['sender']} joined your discussion group")
                    send_message(data["sender"], f"You moved successfully to {data['group_to_join']}'s discussion group")
                    return
        send_message(data["sender"], INVALID_DISCUSSION_GROUP)

    # Sender speak in his current discussion group
    def speak_in_group(self, data: dict):
        discussion_group = self.get_current_discussion_group(data["sender"])
        if discussion_group is None:
            send_message(data["sender"], INVALID_DISCUSSION_GROUP)
            return
        for neighbor in discussion_group:
            send_message(neighbor, f"{data['sender']} said: '{data['message']}'")

def main():
    core = Core()
    with open("test.json", "r") as f:
        string = f.read()
    core.process(string)

main()
