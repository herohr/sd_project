import socket

a= socket.socket()

a.bind(("0.0.0.0", 8089))

a.listen(100)

while True:
    sock, addr = a.accept()
    print(sock.recv(4096).decode())