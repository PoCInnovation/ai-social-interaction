##
## POC Project, 2024
## Social Interaction
## File description: core
## core
##

ERROR_MESSAGE = "There is one or multiple errors in the message you sent"

def send_message(receiver: str, request: str):
    pass

class Core:
    def __init__(self) -> None:
        self.environnement = "A small village with multiple habitants"

    def request_is_valid(request: str) -> bool:
        # Check if the request follow the correct grammar syntax
        return True

    def parse_request(request: str) -> dict:
        # Parse the request depending of the grammar
        return {}

    def send_anwsers(receivers_list: list, message: str):
        for receiver in receivers_list:
            send_message(receiver, message)

    def process(self, request: str, sender: str):
        if (not self.request_is_valid(request)):
            send_message(sender, ERROR_MESSAGE)
            return
        parsed_request = self.parse_request(request)
        receivers_list = self.get_receivers_list(parsed_request)
        answer = self.get_request_anwser(parsed_request)
        self.send_anwsers(receivers_list, answer)


def main():
    core = Core()
    core.process("Send:Bonjour mon ami:ANTOINE")

main()