"""
Server side.
"""
import socket

server_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#Server runs off teh local host
server_soc.bind((socket.gethostname(), 1234))

#Server listens for clients
server_soc.listen(5)
while True:
#Server accepts client connections
	clientsocket, address = server_soc.accept()
	print(f"Connection from {address} has been created!")
	clientsocket.send(bytes("Hi There", "utf-8"))

