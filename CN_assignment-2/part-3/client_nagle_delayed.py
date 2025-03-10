import socket
import time

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 0)  # Enable Nagle
client.connect(("127.0.0.1", 12345))

print("Connected to server. Starting file transfer...")

with open("testfile.txt", "rb") as f:
    while chunk := f.read(40):
        client.sendall(chunk)
        time.sleep(1)

print("File transfer completed successfully.")
client.close()
