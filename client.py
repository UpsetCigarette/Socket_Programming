"""
Client Side
"""
import socket

client_soc = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

client_soc.connect((socket.gethostname(), 1234))

#The client will receive mesages using this code
msg = client_soc.recv(1024)
print(msg.decode("utf-8"))
