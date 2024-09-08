./main server &
./main client &
./main client &
./main client &
./main client &
python graphic_interface.py
pkill -f "python ./main client"
pkill -f "python ./main server"
