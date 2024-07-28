import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

context = "For a simulation of a village, you are a villager in a small town."
with open(os.path.dirname(__file__) + "/../../norm.txt", "r") as norm_file:    
    action_norm = norm_file.read()

def ask_question(messages):
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=messages,
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

class Memory:
    def __init__(self) -> None:
        self.action = ""
        self.memory = ""
        self.name = ""

    # Create a memory string from a description
    def create_memory(self, name,  description):
        self.name = name
        messages = [
                {"role": "system","content": context + ".Your name is " + self.name + description},
                {"role": "user", "content": "From this description, create a memory text with 1000 words without anything else"}
            ]
        self.memory = ask_question(messages)

    # Return a synthesized memory of the memory
    def synthesizes_memory(self):
        messages = [
                {"role": "system","content": context + ".Your name is " + self.name + self.memory},
                {"role": "user", "content": "Synthesizes your memory with 1000 words without message"}
            ]
        self.memory = ask_question(messages)

    # Add an event to the memory
    def add_to_memory(self, event):
        messages = [
                {"role": "system","content": context + ".Your name is " + self.name + self.memory},
                {"role": "user", "content": "Add this to your memory without message:" + event}
            ]
        self.memory = ask_question(messages)

    # Check if the entity want to continu his action
    def ask_continue_action(self, position, env, time, event):
        messages = [
            {"role": "system","content": context + ".Your name is " + self.name + self.memory},
            {"role": "system","content": "You are in the " + position + " with " + env + "it's " + time + ", you are currently doing :" + self.action + " and " + event},
            {"role": "user","content" : "Response with only :  [Yes] if you want to keep making your action or response with only : [No] if you want to make an other action"}
        ]
        res = ask_question(messages)
        print(res)
        if res == "[No]":
            return False
        return True

    # Get an action in the json format of norm.txt
    def get_action(self, env_message):
        messages = [
            {"role": "system","content": context + ".Your name is " + self.name + self.memory},
            {"role": "system","content": env_message},
            {"role": "user","content" : "Choose an action to do only answer with this json format :" + action_norm}
        ]
        action = ask_question(messages)
        return action


# if __name__ == "__main__":
#     description = "You'r a Blacksmith, you love soccers and you are married with Janisse."
#     places = "house, park, townhall, school, work"
#     position = "house"
#     time = "10am"
#     env = "Janisse, Matthieu, Thomas"

#     memory = Memory()
#     memory.create_memory("Antoine", description)
#     memory.synthesizes_memory()
#     memory.add_to_memory("I need to talk with janisse")
#     memory.action = "Waiting for janisse to arrive"
#     memory.action = memory.get_action(position, env, time, "Thomas and Antoine")
#     print(memory.action)
