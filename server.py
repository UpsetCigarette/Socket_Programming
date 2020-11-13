"""
Server side.
"""
import socket, sys, threading
from threading import Thread

users = []
class User(object):
    pass

#@ make the TCP socket and put it in the variable sock
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = int(sys.argv[1])
#@ bind sock on the default ip address, with the port found in port
sock.bind(("127.0.0.1", port))
sock.listen(1)

def handle_connection(conn,info):
    user = User()
    users.append(user)
    user.info = info
    user.conn = conn
    #@ send a "What is your name?" prompt on the connection conn
    user.conn.sendall(b"What is your name?")
    name = conn.recv(1024)
    user.name = name
    msgToSend = "Welcome " + str(user.name) + "!"
    #@ send a welcome message along conn that includes the name that was received
    user.conn.sendall(msgToSend.encode())
    try:
        while True:
            #@ receive some data from conn
            data = user.conn.recv(1024)
            for other in users:

                if other == user:
                    continue
                try:
                    other.conn.sendall(name+b": "+data)
                except:
                    users.remove(other)
    except:
        #@ close conn
        user.conn.close()
        try:
            del users[info]
        except:
            pass

while True:
    Thread(target=handle_connection,args=sock.accept()).start()
