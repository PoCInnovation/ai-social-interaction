from core import Core
import socket
import select

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345
BUFFER_SIZE = 1024
MAX_CLIENTS = 10

clients = {}

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(MAX_CLIENTS)

sockets_list = [server_socket]
core = Core()

print(f'Serveur démarré sur {SERVER_HOST}:{SERVER_PORT}')

def receive_message(client_socket):
    try:
        message_header = client_socket.recv(BUFFER_SIZE)
        if not len(message_header):
            return False
        message_length = int(message_header.decode('utf-8').strip())
        return client_socket.recv(message_length).decode('utf-8')
    except:
        return False

def send_message_to_client(target_client_name, message):
    for client_socket, client_name in clients.items():
        if str(client_name).lower == str(target_client_name).lower:
            try:
                message_header = f"{len(message):<{BUFFER_SIZE}}".encode('utf-8')
                client_socket.send(message_header + message.encode('utf-8'))
                return True
            except:
                return False
    return False

while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()
            client_name = receive_message(client_socket)
            if client_name is False:
                continue
            sockets_list.append(client_socket)
            clients[client_socket] = client_name
            core.add_new_user(client_name)
            print(f'Nouvelle connexion établie depuis {client_address[0]}:{client_address[1]} avec le nom {client_name}')
        else:
            message = receive_message(notified_socket)
            if message is False:
                print(f'Connexion fermée depuis {clients[notified_socket]}')
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue
            client_name = clients[notified_socket]
            print(f'Message reçu de {client_name}: {message}')
            core.process(message)

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]