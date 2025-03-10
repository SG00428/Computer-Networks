import socket
import time

# Disable Nagle's Algorithm
TCP_NODELAY = 1  

# File to be sent
file_name = "testfile.txt"

# Create a TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, TCP_NODELAY)  # Disable Nagle's Algorithm

server_address = ('127.0.0.1', 12345)
client_socket.connect(server_address)

# Send file
with open(file_name, "rb") as file:
    data = file.read(40)  # Send 40 bytes at a time
    while data:
        client_socket.sendall(data)
        time.sleep(1)  # Simulate 40 bytes/sec transfer rate
        data = file.read(40)

print("File transfer completed (No Nagle, No Delayed-ACK).")
client_socket.close()
