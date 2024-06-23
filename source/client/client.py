import socket
import sys
import select

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345
BUFFER_SIZE = 1024

def send_message(socket, message):
    message_header = f"{len(message):<{BUFFER_SIZE}}"
    socket.send(bytes(message_header, 'utf-8') + message)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_HOST, SERVER_PORT))

name = input("Entrez votre nom: ")
send_message(client_socket, bytes(name, 'utf-8'))

while True:
    sockets_list = [sys.stdin, client_socket]
    read_sockets, _, _ = select.select(sockets_list, [], [])

    for notified_socket in read_sockets:
        if notified_socket == client_socket:
            message = client_socket.recv(BUFFER_SIZE)
            if not message:
                print('Déconnexion du serveur')
                sys.exit()
            else:



                # MESSAGE RECU PAR LE CLIENT



                print(message.decode('utf-8'))
        else:
            message = sys.stdin.readline().strip()
            send_message(client_socket, bytes(message, 'utf-8'))
