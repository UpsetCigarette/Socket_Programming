"""
Unfinished Client Code
"""
import socket
import select
import errno
import threading
from threading import Thread
import sys


HEADERSIZE = 10

global message
global prompt_string

IP = "127.0.0.1"
PORT = 1060

message = input("Username: ")
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)

username = message.encode('utf-8')
username_header = f"{len(username):<{HEADERSIZE}}".encode('utf-8')
client_socket.send(username_header + username)
prompt_string = prompt_string = username.decode("utf-8")  + " >> "

def send():
    global message
    while (len(message) > 0):
        try:
            #@ send the encoded on the socket sock
            message = message.encode('utf-8')
            message_header = f"{len(message):<{HEADERSIZE}}".encode('utf-8')
            client_socket.send(message_header + message)
            message = input(prompt_string)
        except:
            break
    #@ close sock
    client_socket.close()
def receive():
    while (True):
        try:
            while True:
                # receive things
                username_header = client_socket.recv(HEADERSIZE)
                if not len(username_header):
                    print("Connection closed by the server")
                    sys.exit()
                username_length = int(username_header.decode('utf-8').strip())
                username = client_socket.recv(username_length).decode('utf-8')

                message_header = client_socket.recv(HEADERSIZE)
                message_length = int(message_header.decode('utf-8').strip())
                message = client_socket.recv(message_length).decode('utf-8')

                print(f"{username} >> {message}")
            
        except:
            break

while True:
    sending_thread = threading.Thread(target=send)
    receiving_thread = threading.Thread(target=receive)
    try:
        sending_thread.start()
        receiving_thread.start()
        sending_thread.join()
        receiving_thread.join()
    except: print("whoops")
    
