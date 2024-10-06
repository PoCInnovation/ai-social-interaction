from sys import argv
import os


if len(argv) < 2:
    print("please precise a number of client, ex : python start_project.py 5, for 5 client")
    exit(0)
try:
    int(argv[1])
except ValueError:
    print("please enter a valid value for the number of client")
    exit(0)
os.system("./main server &")
for i in range(int(argv[1])):
    os.system("./main client &")
os.system("python graphic_interface.py")
os.system('pkill -f "python ./main client"')
os.system('pkill -f "python ./main server"')
