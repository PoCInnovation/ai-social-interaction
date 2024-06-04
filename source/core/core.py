##
## POC Project, 2024
## Social Interaction
## File description: core
## core
##

ERROR_MESSAGE = "There is one or multiple errors in the message you sent"
ZONE_ERROR = "There is an error with your current zone"
PERSON_ERROR = "The person to the one you are trying to talk does not exists or is currently not in your zone"

def send_message(receiver: str, request: str):
    pass

class Core:
    def __init__(self) -> None:
        self.places = {
            "parc" : [],
            "street" : [],
            "work" : [],
            "restaurent" : [],
            "market" : [],
            "school" : [],
        }

    def request_is_valid(request: str) -> bool:
        # Check if the request follow the correct grammar syntax
        # If the request is a movement check if the place exists and if not return False
        return True

    def process(self, request: str, sender: str):

        actions_dict = {
            "move": self.move,
            "check": self.check,
            "talk": self.talk,
        }

        if (not self.request_is_valid(request)):
            send_message(sender, ERROR_MESSAGE)
            return
    
    # Moving the "sender" to a place
    def move(self, sender: str, place: str):
        for p in self.places:
            if sender in self.places[p]:
                self.places[p].remove(sender)
                break
        self.places[place].append(sender)
        send_message(sender, f"You moved succesfully to {place}")

    # Check which persons are in the same zone as the sender
    def check(self, sender: str, request: str):
        message = "There is the list of the persons that are actually next to you: "
        sender_place = None

        for p in self.places:
            if sender in self.places[p]:
                sender_place = p
                break
        if (sender_place == None):
            send_message(sender, ZONE_ERROR)
            return
        for person in self.places[sender_place]:
            if (person != sender):
                message = f"{message}, {person}"
        send_message(sender, message)

    # Talk to a person that is in the same zone as you
    def talk(self, sender: str, receiver: str, message):
        sender_place = None

        for p in self.places:
            if sender in self.places[p]:
                sender_place = p
                break
        if (sender_place == None):
            send_message(sender, ZONE_ERROR)
            return
        if (not receiver in self.places[sender_place]):
            send_message(sender, ZONE_ERROR)
            return
        send_message(receiver, f"Message of {sender}: {message}")


def main():
    core = Core()
    core.process("Send:Bonjour mon ami:ANTOINE")

main()