"""
Client side script. Originally based on sentdex's code.

This program starts a client that connects to a server, "server_1.py".

This client handles various functions including connecting to the server and uploading files.

Author: Joseph Grecco II
Date: November 22nd, 2020

"""

from os.path import *
import socket
import select
import errno
import threading
from threading import Thread
import sys

# The header size. This lets the server/client know how long each message is.
HEADERSIZE = 10

# Global variables needed throughout.
global message
global prompt_string
global isConn
global exitCond
global exitMsg
helpMsg = "List of commands:\
\n!read <filename> - reads a filename from the serverside.\
\n!upload <filename> - not implemented yet.\
\n!filelist - prints a list of files on the server.\
\n!exit - closes your connection with the server and exits."
exitCond = False
isConn = False # Set to false until the socket has sent it's username to the server.
prompt_string = "" # Prompt string is blank, but can be changed if wanted.

# Connection info.
IP = "127.0.0.1"
PORT = 1060

# Connecting the socket.
message = input("Username: ")
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.settimeout(1)
client_socket.setblocking(True)

# Sending username info to the server.
username = message.encode('utf-8')
username_header = f"{len(username):<{HEADERSIZE}}".encode('utf-8')
client_socket.send(username_header + username)


def getFileContent(fileName):
    # This function simply gets the data held within a text file.
    # Returns -1 if the file is empty.
    fileObj = open(fileName, "r")
    fileListStr = fileObj.readlines()
    if (len(fileListStr) != 0 and fileListStr[0].strip(" ") != ""):
        tmpStr = ""
        for line in fileListStr:
            tmpStr += line
        return tmpStr
    else:
        return -1

def send():
    global exitCond
    global exitMsg
    # This function handles the sending of messages from the client to the server.
    while (True):
        global message
        fileTxt = ""
        while (len(message) > 0):
            # First if/elif statements check for commands that are handled client side.
            if (message.split(" ")[0].startswith("!")):
                if (message.split(" ")[0] == "!upload"):
                    # This section handles uploading .txt files to the server.
                    if (isfile(message.split(" ")[1]) and len(message.split(" ")) > 1):
                        # If the file is empty or the file is the wrong type,
                        # it sends that error to the server.
                        tmp = message.split(" ")[1]
                        if (tmp[-4:] == ".txt" and getFileContent(message.split(" ")[1]) != -1):
                            fileTxt = getFileContent(message.split(" ")[1])
                            fileTxtToSend = "!upload " + message.split(" ")[1] + " " + fileTxt
                        elif (tmp[-4:] != ".txt"):
                            fileTxt = "!wrongtype"
                            fileTxtToSend = "!upload " + fileTxt
                        else: 
                            fileTxt = "!emptyfile"
                            fileTxtToSend = "!upload " + fileTxt
                    else:
                        # If the file isn't found on the clients side.
                        fileTxt = "!notfound"
                        fileTxtToSend = "!upload " + fileTxt
                elif (message.split(" ")[0] == "!filelist"):
                    # Sets the message to only "!filelist" to make it consistent.
                    message = "!filelist"
                elif (message.split(" ")[0] == "!exit"): 
                    # This one shuts down the client side and exits gracefully.
                    print("Shutting down client...")
                    exitCond = True
                    message = "!exit"
                    exitMsg = message.encode("utf-8")
                    exitHeader = f"{len(exitMsg):<{HEADERSIZE}}".encode('utf-8')
                    client_socket.send(exitHeader + exitMsg)
                    break
                elif (message.split(" ")[0] == "!help"):
                    # Prints the helpMsg
                    print(helpMsg)
                elif (message.split(" ")[0] == "!read"):
                    # Simply prints a new line so that the message sent from 
                    # the server is more readable.
                    print("")
                else:
                    # The command entered doesn't exist!
                    print("Invalid command!")
            # Sends the message to the server.
            try:
                # Encodes and sends the header and message to the server.
                if (fileTxt != ""):
                    fileBytesToSend = fileTxtToSend.encode('utf-8')
                    fileByteHeader = f"{len(fileTxtToSend):<{HEADERSIZE}}".encode('utf-8')
                    client_socket.send(fileByteHeader + fileBytesToSend)
                    fileTxt = ""
                else:
                    message = message.encode('utf-8')
                    message_header = f"{len(message):<{HEADERSIZE}}".encode('utf-8')
                    client_socket.send(message_header + message)
                message = input(prompt_string)
            except:
                break
        # If the user didn't enter anything, it grabs input.
        if (len(message) == 0): message = input(prompt_string)
        elif (message == "!exit"): break
        #@ close sock

def receive():
    # This function reveives input from the server and outputs it as needed.
    global isConn
    global message
    while True:
        if (isConn == True):
            # Grabs input first to ensure that each message is received properly.
            tmpHeader = client_socket.recv(HEADERSIZE)
            tmpLen = int(tmpHeader.decode('utf-8').strip())
            tmp = client_socket.recv(tmpLen).decode('utf-8')
            if (tmp.startswith("!")):
                # If the message received it related to a command.
                if (tmp == "!exit"):
                    # Servers sends the exit message back and the function breaks.
                    break
                print(tmp[1:])
            else:
                # This handles the general chat messages.
                username = tmp
                message_header = client_socket.recv(HEADERSIZE)
                message_length = int(message_header.decode('utf-8').strip())
                messageR = client_socket.recv(message_length).decode('utf-8')

                print(f"{username} >> {messageR}")
            
        else:
            # Receives a welcome message from the server.
            welcomeMsgHeader = client_socket.recv(HEADERSIZE)
            welcomeMsgLen = int(welcomeMsgHeader.decode('utf-8').strip())
            welcomeMsg = client_socket.recv(welcomeMsgLen).decode('utf-8')
            print(welcomeMsg)
            isConn = True #WOAH

while (exitCond == False):
    # Sets up and runs the threads to receive and send messages.
    receiving_thread = threading.Thread(target=receive)
    sending_thread = threading.Thread(target=send)
    receiving_thread.start()
    sending_thread.start()
    receiving_thread.join()
    sending_thread.join()

client_socket.close()
sys.exit()

    
    
