import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # Disable Nagle
server.setsockopt(socket.IPPROTO_TCP, socket.TCP_QUICKACK, 0)  # Enable Delayed-ACK
server.bind(("127.0.0.1", 12345))
server.listen(1)

print("Server is listening...")

conn, addr = server.accept()
print(f"Connected to {addr}")

with open("received_no_nagle_delayed.txt", "wb") as f:
    while True:
        data = conn.recv(40)
        if not data:
            break
        f.write(data)

print("File transfer completed successfully.")
conn.close()
server.close()
