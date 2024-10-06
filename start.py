# from sys import argv
from source.client.memory import Memory
import signal
import time
import sys
import os
import json

def get_config():
    with open("config.json") as f:
        config = json.load(f)
    return (config['clientsNumber'], config['simulationDuration'])

def signal_handler(sig, frame):
    os.system('pkill -f "python ./main client"')
    os.system('pkill -f "python ./main server"')
    print("\nclient and server destroyed, program terminated cleanly")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


# if len(argv) < 3:
#     print("please precise a number of client and second, ex : python start_project.py 5 10, for 5 client running for 10 seconds")
#     exit(1)
# try:
#     int(argv[1])
# except ValueError:
#     print("please enter a valid value for the number of client")
#     exit(1)
# try:
#     int(argv[2])
# except ValueError:
#     print("please enter a valid value for the number of seconds")
#     exit(1)

memory = Memory()
memory.ask_simple_question("hello")

clientsNumber, simulationDuration = get_config()

os.system("./main server &")
for i in range(int(clientsNumber)):
    os.system("./main client &")

time.sleep(int(simulationDuration))

os.system('pkill -f "python ./main client"')
os.system('pkill -f "python ./main server"')
