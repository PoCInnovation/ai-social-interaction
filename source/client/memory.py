import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

torch.random.manual_seed(0)

class Memory:
    def __init__(self) -> None:
        self.action = ""
        self.memory = ""
        self.name = ""

        self.context = "For a simulation of a village, you are a villager in a small town."
        self.model = AutoModelForCausalLM.from_pretrained(
            "microsoft/Phi-3.5-mini-instruct",
        device_map="cuda",
        torch_dtype="auto",
        trust_remote_code=True
        )
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/Phi-3.5-mini-instruct")
        self.pipe = pipeline(
        "text-generation",
        model=self.model,
        tokenizer=self.tokenizer
        )
        self.generation_args = {
        "max_new_tokens": 500,
        "return_full_text": False,
        "do_sample": False,
        }
        with open(os.path.dirname(__file__) + "/../../norm.txt", "r") as norm_file:    
            self.action_norm = norm_file.read()


    def ask_question(self, messages):
        output = self.pipe(messages, **self.generation_args)
        return output[0]['generated_text']

    # Create a memory string from a description
    def create_memory(self, name,  description):
        self.name = name
        messages = [
                {"role": "system","content": self.context + ".Your name is " + self.name + description},
                {"role": "user", "content": "From this description, create a memory text with 1000 words without anything else"}
            ]
        self.memory = self.ask_question(messages)

    # Return a synthesized memory of the memory
    def synthesizes_memory(self):
        messages = [
                {"role": "system","content": self.context + ".Your name is " + self.name + self.memory},
                {"role": "user", "content": "Synthesizes your memory with 1000 words without message"}
            ]
        self.memory = self.ask_question(messages)

    # Add an event to the memory
    def add_to_memory(self, event):
        messages = [
                {"role": "system","content": self.context + ".Your name is " + self.name + self.memory},
                {"role": "user", "content": "Add this to your memory without message:" + event}
            ]
        self.memory = self.ask_question(messages)

    # Check if the entity want to continu his action
    def ask_continue_action(self, position, env, time, event):
        messages = [
            {"role": "system","content": self.context + ".Your name is " + self.name + self.memory},
            {"role": "system","content": "You are in the " + position + " with " + env + "it's " + time + ", you are currently doing :" + self.action + " and " + event},
            {"role": "user","content" : "Response with only :  [Yes] if you want to keep making your action or response with only : [No] if you want to make an other action"}
        ]
        res = self.ask_question(messages)
        print(res)
        if res == "[No]":
            return False
        return True

    # Get an action in the json format of norm.txt
    def get_action(self, env_message):
        messages = [
            {"role": "system","content": self.context + ".Your name is " + self.name + self.memory},
            {"role": "system","content": env_message},
            {"role": "user","content" : "Choose an action to do only answer with this json format :" + self.action_norm}
        ]
        action = self.ask_question(messages)
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
