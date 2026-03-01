import socket
import threading
import os

HOST = '127.0.0.1'
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = {}
addresses = {}

def broadcast_users():
    users = ",".join(clients.keys())
    for client in clients.values():
        client.send(f"USERS:{users}".encode())

def handle(client):
    username = client.recv(1024).decode()
    clients[username] = client
    broadcast_users()

    while True:
        try:
            message = client.recv(1024)

            if message.startswith(b"FILE|"):
                header = message.decode().split("|")
                receiver = header[1]
                filename = header[2]
                filesize = int(header[3])

                file_data = b""
                while len(file_data) < filesize:
                    file_data += client.recv(1024)

                if receiver in clients:
                    clients[receiver].send(f"FILE|{username}|{filename}|{filesize}".encode())
                    clients[receiver].send(file_data)

            else:
                receiver, msg = message.decode().split("|", 1)
                if receiver in clients:
                    clients[receiver].send(f"PRIVATE|{username}|{msg}".encode())

        except:
            break

    client.close()

while True:
    client, addr = server.accept()
    threading.Thread(target=handle, args=(client,), daemon=True).start()