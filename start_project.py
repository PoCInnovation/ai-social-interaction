from sys import argv
import os
import time


if len(argv) < 3:
    print("please precise a number of client and second, ex : python start_project.py 5 10, for 5 client running for 10 seconds")
    exit(0)
try:
    int(argv[1])
except ValueError:
    print("please enter a valid value for the number of client")
    exit(0)
try:
    int(argv[2])
except ValueError:
    print("please enter a valid value for the number of seconds")
    exit(0)
os.system("./main server &")
for i in range(int(argv[1])):
    os.system("./main client &")
time.sleep(int(argv[2]))
os.system('pkill -f "python ./main client"')
os.system('pkill -f "python ./main server"')