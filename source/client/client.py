import socket
import sys
import select
from memory import Memory

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345
BUFFER_SIZE = 1024

def send_message(socket, message):
    message_header = f"{len(message):<{BUFFER_SIZE}}"
    socket.send(bytes(message_header, 'utf-8') + bytes(message, 'utf-8'))

def receive_message(socket):
    message_header = socket.recv(BUFFER_SIZE)
    if not message_header:
        print('Déconnexion du serveur')
        sys.exit()
    message_length = int(message_header.decode('utf-8').strip())
    message = socket.recv(message_length).decode('utf-8')
    return message


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_HOST, SERVER_PORT))

while True:
    sockets_list = [sys.stdin, client_socket]
    read_sockets, _, _ = select.select(sockets_list, [], [])

    for notified_socket in read_sockets:
        if notified_socket == client_socket:
            message = receive_message(client_socket)
            print(f"Message reçu du serveur: {message}")
            if message.endswith("WHAT ACTION DO YOU WANT TO DO ?"):
                action = memory.get_action(message.split("WHAT")[0])
                print("action :\n" + action)
                send_message(client_socket, action)
            if message.startswith("STARTING MESSAGE"):
                message = message.split(":")
                memory = Memory()
                memory.create_memory(message[1], message[2])
                memory.synthesizes_memory()
        # else:
        #     message = sys.stdin.readline().strip()
        #     message = '''
        #     {
        #         "action": "go_to_location",
        #         "sender": "pierre",
        #         "receiver": "",
        #         "location": "parc",
        #         "group_to_join": "",
        #         "message": "" 
        #     }
        #     '''
        #     send_message(client_socket, message)
