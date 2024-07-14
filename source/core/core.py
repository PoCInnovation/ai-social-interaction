##
## POC Project, 2024
## Social Interaction
## File description: core
## core
##

from groq import Groq
import os


ERROR_MESSAGE = "There is one or multiple errors in the message you sent"
SYNTAX_ERROR_MESSAGE = "There is a syntax error in your request"
ACTION_ERROR_MESSAGE = "The action you chose is invalid"
ARGUMENT_NUMBER_ERROR_MESSAGE = "There is an error in the number of argument for the action you selected"
ZONE_ERROR_MESSAGE = "There is an error with your current zone"
PERSON_ERROR_MESSAGE = "The person you are trying to talk to does not exists or is currently not in your zone"
ERROR_CODE = 600
SYNTAX_ERROR_CODE = 601
ACTION_ERROR_CODE = 602
ARGUMENT_NUMBER_ERROR_CODE = 603
ZONE_ERROR_CODE = 604
PERSON_ERROR_CODE = 605

cost_of_action = {
    "move": 15,
    "talk" : 1,
}

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def ask_message(message):
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=message,
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )
    res=""
    for chunk in completion:
        res += chunk.choices[0].delta.content or ""
    return res

def ask_question(question):
    return ask_message([
        {
            "role": "user",
            "content": question
        }
    ])


def send_message(receiver: str, request: str, code: int = 0):
    return (receiver, request, code)


class Core:
    def __init__(self, entities={}, debug=False) -> None:
        self.places = {
            "park" : ["ANTOINE"],
            "street" : [],
            "work" : ["MARTIN"],
            "restaurent" : [],
            "market" : [],
            "school" : [],
        }
        self.street = [] # it's a temporary transition area where AI can't do anything, element = [DESTINATION, AI_NAME, DURATION_OF_TRANSITION_LEFT]
        self.entities = entities
        self.debug = debug
        self.turn_number = 0
    
    # Main function that ask entities what they want to do
    def loop_on_entities(self):
        self.turn_number += 1
        self.print_debug(f"\n----- Turn {self.turn_number} -----")
        for entity in self.entities.values():
            entity.cooldown -= 1
            action = entity.process("test")
            if action != "None":
                self.print_debug(f"\nRequest: \"{action}\" | from: {entity.name}")
                receiver, reply, code = self.process(action, entity)
                self.print_debug(f"Reply: \"{reply}\" | to: {receiver} | code: {code}")
            elif entity.cooldown > 0:
                self.print_debug(f"\n{entity.name} wait for {entity.cooldown} turn")
            else:
                self.print_debug(f"\n{entity.name} has nothing more to do")

        self.move_all_entity()
        self.print_debug(f"\n----- End turn {self.turn_number} -")

    def move_all_entity(self):
        new_street = []
        for transition_info in self.street:
            transition_info[2] -= 1
            if transition_info[2] <= 0:
                self.places[transition_info[1]].append(transition_info[0])
            else:
                new_street.append(transition_info)
        self.street = new_street

    # Process response from an entity
    def process(self, request: str, entity):
        request_split = request.split(":")
        actions_dict = {
            "move": self.move,
            "check": self.check,
            "talk": self.talk,
        }

        if (request_split[0] not in actions_dict or not self.request_is_valid(request)):
            return send_message(request_split[1], f"{ERROR_MESSAGE}->{request}", ERROR_CODE)
        receiver, message, code = actions_dict[request_split[0]](*(request_split[1:]))
        if code == 0:
            entity.cooldown += cost_of_action[request_split[0]]
        return receiver, message, code

    def request_is_valid(self, request: str) -> bool:
        # Check if the request follow the correct grammar syntax
        # If the request is a movement check if the place exists and if not return False
        return True
    
    # Moving the "sender" to a place
    def move(self, sender: str, place: str):
        for p in self.places:
            if sender in self.places[p]:
                self.places[p].remove(sender)
                break
        self.street.append([sender, place, cost_of_action["move"]])
        return send_message(sender, f"You start moving to {place}")

    # Check which persons are in the same zone as the sender
    def check(self, sender: str, request: str):
        message = "There is the list of the persons that are actually next to you: "
        sender_place = self.get_place(sender)

        if (sender_place == None):
            return send_message(sender, ZONE_ERROR_MESSAGE, ZONE_ERROR_CODE)
        for person in self.places[sender_place]:
            if (person != sender):
                message = f"{message}, {person}"
        return send_message(sender, message)

    # Talk to a person that is in the same zone as you
    def talk(self, sender: str, receiver: str, message):
        sender_place = self.get_place(sender)

        if (sender_place == None):
            return send_message(sender, ZONE_ERROR_MESSAGE, ZONE_ERROR_CODE)
        if (not receiver in self.places[sender_place]):
            return send_message(sender, PERSON_ERROR_MESSAGE, PERSON_ERROR_CODE)
        self.temp_talk(sender, receiver, message)
        return send_message(receiver, f"message:{sender}:{message}")
    
    def temp_talk(self, sender: str, receiver: str, message):
        answer = message
        for _ in range(5):
            last_answer = answer
            answer = ask_question(f"You are {sender}, {receiver} ask you \"{answer}\", what do you respond (write only the answer)")
            print(f"\nSender: {sender} | Receiver: {receiver} | Message: {last_answer} | Answer: {answer}")
            last_answer = answer
            answer = ask_question(f"You are {receiver}, {sender} ask you \"{answer}\", what do you respond (write only the answer)")
            print(f"\nSender: {receiver} | Receiver: {sender} | Message: {last_answer} | Answer: {answer}")

    def get_place(self, character: str):
        for place_name, character_list in self.places.items():
            if character in character_list:
                return place_name
        return None
    
    def print_places(self):
        print("")
        for places, characters in self.places.items():
            print(places, ":", ", ".join(characters))
        print("street:")
        for transition_info in self.street:
            print("Name:", transition_info[0], "| Destination:", transition_info[1], "| Turn left:", transition_info[2])
    
    def print_debug(self, *args):
        if self.debug:
            print(*args)


class Entity:
    def __init__(self, name, action_list=[]):
        self.name = name
        self.action_list = action_list
        self.cooldown = 1
        self.current_action = "None"

    def process(self, message):
        if self.cooldown <= 0 and len(self.action_list) > 0:
            return self.action_list.pop(0)
        return "None"


if __name__ == "__main__":
    core = Core(
        entities={
            "MARTIN" : Entity("MARTIN", ["move:MARTIN:park", "talk:MARTIN:ANTOINE:Bonjour mon ami"]),
            "ANTOINE" : Entity("ANTOINE", ["move:ANTOINE:park"]),
        },
        debug=True
    )   
    core.print_places()

    nbr_cycle = 30
    for i in range(nbr_cycle):
        core.loop_on_entities()
        core.print_places()


def ask_action():
    return ask_question("You are MICHEL a villager, you can choose one action between those one : move (to an other place), talk (to an other person)."
                       "You are in the park. The person around you are MARTIN and GUSTAVE."
                       "You can move to : parc, work, restaurent, cafe."
                       "Write the answer like those exemple format: [move:work], [talk:GUSTAVE], [talk:MARTIN], ...")

def extract_response(ai_response):
    if "[" in ai_response and "]" in ai_response:
        response = ai_response.split("[")[1].split("]")[0]
        if ":" not in response:
            return -1
        return response.split(":")
    return -1

def get_action():
    error_counter = 0
    response = extract_response(ask_action())
    while response == -1:
        error_counter += 1
        if error_counter >= 5:
            print("ERROR: to much error in extraction")
            exit(0)
        response = extract_response(ask_action())
    return [param.strip() for param in response]


if __name__ == "__main__":
    for _ in range(10):
        print(get_action())
