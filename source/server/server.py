from source.server.core import Core
import socket
import select
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DataConfig

class Server:

    def receive_message(self, client_socket, core):
        try:
            message_header = client_socket.recv(DataConfig.BUFFER_SIZE)
            if not len(message_header):
                return False
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')
            core.print_debug(f"Received: {message}")
            return message
        except:
            return False

    def run(self):

        current_time = 0
        client_socket_map = {}

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((DataConfig.SERVER_HOST, DataConfig.SERVER_PORT))
        server_socket.listen(DataConfig.MAX_CLIENTS)

        sockets_list = [server_socket]
        core = Core(debug=False)

        print(f'Serveur démarré sur {DataConfig.SERVER_HOST}:{DataConfig.SERVER_PORT}')

        while True:

            start_time = time.time()
            core.execute_finished_actions(current_time)
            core.ask_actions_to_do(client_socket_map)
            core.transfer_info()
            while time.time() - start_time < 4:

                read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list, 1)

                for notified_socket in read_sockets:
                    if notified_socket == server_socket:
                        client_socket, client_address = server_socket.accept()
                        client_name, description = core.get_new_description()
                        sockets_list.append(client_socket)
                        client_socket_map[client_socket] = client_name
                        core.add_new_user(client_name)
                        print(f'Nouvelle connexion établie depuis {client_address[0]}:{client_address[1]} avec le nom {client_name}')
                        core.send_message(client_socket, "STARTING MESSAGE:" + client_name + ":" + description)
                    else:
                        message = self.receive_message(notified_socket, core)
                        if message is False:
                            print(f'Connexion fermée depuis {client_socket_map[notified_socket]}')
                            sockets_list.remove(notified_socket)
                            # core.remove_client()
                            core.remove_client(client_socket_map[notified_socket])
                            del client_socket_map[notified_socket]
                            continue
                        client_name = client_socket_map[notified_socket]
                        core.process(notified_socket, message, client_socket_map, current_time)

                for notified_socket in exception_sockets:
                    sockets_list.remove(notified_socket)
                    del client_socket_map[notified_socket]
            current_time += 1
