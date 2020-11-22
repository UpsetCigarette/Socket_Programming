"""
Server side script. Originally based on sentdex's code.

This program allows a user to connect to a host server and send chat messages
through the server to another user.

Author: Joseph Grecco II
Date: November 22nd, 2020

"""

import socket
import select

# The header size. This lets the client know how long the message will be.
HEADERSIZE = 10
ip_address = "127.0.0.1"
port = 1060

# Setting up and connecting the socket.
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((ip_address, port))
server_socket.listen()

#Initializing the sockets_list, clients, and file data to be stored on the server. 
sockets_list = [server_socket]
fileDict = {"test.txt":"test text!"}
clients = {}



def recieve_message(client_socket):
	# This function handles receiving data from the clients.
	try:
		message_header = client_socket.recv(HEADERSIZE)
		if not len(message_header):
			return False
		
		message_length = int(message_header.decode('utf-8').strip())
		return {'header': message_header, 'data': client_socket.recv(message_length)}
	except:
		return False
	
newUser = False # T/F to signal if there's a new user to be welcomed.
while True:
	read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
	for notified_socket in read_sockets:
		# Gets the socket to be notified.
		if notified_socket == server_socket:
			# If the user hasn't connected before.
			client_socket, client_address = server_socket.accept()

			user = recieve_message(client_socket)

			if user is False:
				continue

			sockets_list.append(client_socket)
			newUser = True # Sets the new user command to true, so the server sends a notification to other users.
			clients[client_socket] = user
			# Sending the welcome message to the new user.
			welcomeMsg = "Welcome " + user['data'].decode("utf-8") + "!"
			welcomeMsg += "\nType a message and press enter to send!\nType '!help' for a list of commands."
			welcomeMsgHead = f"{len(welcomeMsg):<{HEADERSIZE}}".encode('utf-8')
			client_socket.send(welcomeMsgHead + welcomeMsg.encode("utf-8"))
			print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))
		
		else:
			message = recieve_message(notified_socket) # Gets whatever text the user sent to the server.
			if message is False:
				print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))
				sockets_list.remove(notified_socket)
				del clients[notified_socket]
				continue

			user = clients[notified_socket]
			strMsg = message["data"].decode('utf-8')
			print(f'Received message from {user["data"].decode("utf-8")}: {strMsg}')


			if (newUser == True):
				# This sends a notification to all other users when someone joins the server.
				newUser = False
				for client_socket in clients:
					if client_socket != notified_socket:
						newUserMsg = (user['data']) + " has joined the server!".encode('utf-8')
						newUserHeader = (f"{len(newUserMsg):<{HEADERSIZE}}").encode('utf-8')
						client_socket.send(user['header'] + user['data'] + newUserHeader + newUserMsg)
						print("Welcome message sent.")
			
			# Here the server handles commands entered.
			elif (strMsg.startswith("!")):
				tmpList = strMsg.split(" ") # We split the string to make it easier to check the first command.
				print(tmpList)
				if (len(tmpList) > 1):
					# If the command has more than one item, it is either a read or upload command.
					if (tmpList[0] == "!read"):
						# When reading a file, it either exists or it doesn't. This handles that.
							if (tmpList[1] in fileDict and tmpList[1].strip() != ""):
								fileStrToSend = "!".encode('utf-8') + fileDict[tmpList[1]].encode('utf-8')
								print(fileStrToSend)
								fileStrHeader = f"{len(fileStrToSend):<{HEADERSIZE}}".encode('utf-8')
								notified_socket.send(fileStrHeader + fileStrToSend)
							else:
								print("hrere")
								tmpMsg = "!File not found on server! Try uploading it!".encode('utf-8')
								tmpMsgHeader = f"{len(tmpMsg):<{HEADERSIZE}}".encode('utf-8')
								notified_socket.send(tmpMsgHeader + tmpMsg)
						
					elif (tmpList[0] == "!upload"):
						# Uploads a file and stores it's file name and text within the fileDict.
						# The first few if statements check for errors.
						if (tmpList[1] == "!notfound"):
							fileNote = "!File not found!".encode('utf-8')
							fileNoteHeader = f"{len(fileNote):<{HEADERSIZE}}".encode('utf-8')
							notified_socket.send(fileNoteHeader + fileNote)
						elif (tmpList[1] == "!emptyfile"):
							fileNote = "!Cannot upload empty file!".encode('utf-8')
							fileNoteHeader = f"{len(fileNote):<{HEADERSIZE}}".encode('utf-8')
							notified_socket.send(fileNoteHeader + fileNote)
						elif (tmpList[1] == "!wrongtype"):
							fileNote = "!You can only upload .txt files!".encode('utf-8')
							fileNoteHeader = f"{len(fileNote):<{HEADERSIZE}}".encode('utf-8')
							notified_socket.send(fileNoteHeader + fileNote)
						else:
							# Adds the file to the dicitonary!
							fileText = ""
							for num in range(2, len(tmpList)):
								fileText += tmpList[num] + " "
							fileDict[tmpList[1]] = fileText
							print("File has been uploaded to server!")
							fileNote = "!" + tmpList[1]
							fileNote += " uploaded to server!"
							fileNote = fileNote.encode('utf-8')
							fileNoteHeader = f"{len(fileNote):<{HEADERSIZE}}".encode('utf-8')
							notified_socket.send(fileNoteHeader + fileNote)
				elif (tmpList[0] == "!filelist"):
					# Gets and sends a list of the files currently on the server.
					tmpStr = "!"
					for file in fileDict:
						tmpStr += "> " + file + " \n"
					tmpStr = tmpStr.encode('utf-8')
					tmpStrHeader = f"{len(tmpStr):<{HEADERSIZE}}".encode('utf-8')
					notified_socket.send(tmpStrHeader + tmpStr) 

				# Other commands.
				elif (tmpList[0] == "!exit"):
					# If a user is exiting, this removes their data from the server and sends a confirmation to the client.
						tmpMsg = "!exit".encode('utf-8')
						tmpMsgHeader = f"{len(tmpMsg):<{HEADERSIZE}}".encode('utf-8')
						notified_socket.send(tmpMsgHeader + tmpMsg)
						print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))
						for client_socket in clients:
							if client_socket != notified_socket:
								leaveUserMsg = (user['data']) + " has left the server!".encode('utf-8')
								leaveUserHeader = (f"{len(newUserMsg):<{HEADERSIZE}}").encode('utf-8')
								client_socket.send(user['header'] + user['data'] + leaveUserHeader + leaveUserMsg)
						print("Exit message sent.")
						sockets_list.remove(notified_socket)
						del clients[notified_socket]
				# Extra code for read command, in case the user simply typed "!read".
				elif (tmpList[0] == "!read"):
					tmpMsg = "!File not found on server! Try uploading it!".encode('utf-8')
					tmpMsgHeader = f"{len(tmpMsg):<{HEADERSIZE}}".encode('utf-8')
					client_socket.send(tmpMsgHeader + tmpMsg)
			else:
				# Handles regular chat messages sent to the server.
				for client_socket in clients:
					if client_socket != notified_socket:
						client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])
						print("msg sent")

	# If we have an exception, removes that socket from the list.
	for notified_socket in exception_sockets:
		sockets_list.remove(notified_socket)
		del clients[notified_socket]
