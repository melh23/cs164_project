import socket
import sys
from _thread import *
import time

'''
Function Definition
'''
def tupleToString(t):
	s=""
	for item in t:
		s = s + str(item) + "<>"
	return s[:-2]

def stringToTuple(s):
	t = s.split("<>".encode())
	return t

'''
Create Socket
'''
HOST = ''	# Symbolic name meaning all available interfaces
PORT = 9486	# Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print("Socket created")

'''
Bind socket to local host and port
'''
try:
	s.bind((HOST, PORT))
except socket.error as msg:
	print("Bind failed. Error Code : " + str(msg[0]) + " Message " + msg[1])
	sys.exit()
print("Socket bind complete")

'''
Start listening on socket
'''
s.listen(10)
print("Socket now listening")

def recv(s):
	while True:
		try:
			msg = s.recv(1024)
			if msg:
				return msg.decode()
		except:
			print("connection error [recv]")
			break


def send(s, data, response):
	msg = response + "<>" + data
	s.setblocking(False)
	while True:
		s.sendall(msg.encode())
		try:
			ack = s.recv(1024)
			if ack:
				s.setblocking(True)
				return
		except:
			time.sleep(1)

'''
Define variables:
username && passwd
message queue for each user
'''
clients = []
online = {}
# TODO: Part-1 : create a var to store username && password. NOTE: A set of username/password pairs are hardcoded here. 
# e.g. userpass = [......]
messages = []
count = 0
userpass = [[b'mel', b'pass'], [b'alice', b'pass'], [b'bob', b'pass']]

groups = [b'room 1', b'room 2', b'room 3']
participants = [[b'mel'], [], [b'alice', b'bob']]	# users in each chatroom



'''
Function for handling connections. This will be used to create threads
'''
def clientThread(conn):
	global clients
	global count
	global online
	# Tips: Sending message to connected client
	conn.send("Welcome to the server. Please login to access the server\n".encode()) #send only takes string
	rcv_msg = conn.recv(1024)
	rcv_msg = stringToTuple(rcv_msg)
	# print(rcv_msg)
	# clients.push(rcv_msg[0])
	if rcv_msg in userpass:
		user = userpass.index(rcv_msg)
		online[userpass[user][0].decode()] = conn
		print(online)

		try :
			conn.sendall("valid".encode())
		except socket.error:
			print("Send failed")
			sys.exit()
			
		# Tips: Infinite loop so that function do not terminate and thread do not end.
		while True:
			try :
				option = conn.recv(1024).decode()
				print(option)
				
			except:
				break
			if option == str(1):
				print("user logout")
				send(conn, "Logging you out!", "False")
				try:
					conn.sendall("nalid".encode())
				except socket.error:
					print("nalid Send falied")
				print("user logged out")
				break
			elif option == str(2):
				print("change password")
				send(conn, "What is your old password? ", "True")
				msg = recv(conn)
				if userpass[user][1].decode() != msg:
					send(conn, "Invalid password. Aborting reset", "False")
					break
				send(conn, "What is your new password? ", "True")
				msg = recv(conn)
				userpass[user][1] = msg.encode()
				send(conn, "Password updted", "False")
				send(conn, "break", "False")
			elif option == str(3):
				print("Get all messages")
				name = userpass[user][0].decode()
				msglist = ""
				for msg in messages:
					if name == msg[0]:
						msglist += msg[1]
						msglist += "\n"
						msg[0] = "rcvd"
						# messages.remove([name, msg[1]])
				send(conn, msglist, "False")
				send(conn, "break", "False")
			elif option == str(4):
				print("Post a message")
				send(conn, "Which user do you want to send to? ", "True")
				sendto = recv(conn)
				if not online[sendto]:
					send(conn, "User not available", "False")
					print("user not in client list")
					break
				send(conn, "What is your message? ", "True")
				msg = recv(conn)
				messages.append([sendto, msg])
				print(messages)
				send(conn, "break", "False")
			elif option == str(5):
				print("Broadcast")
				send(conn, "What is your message to broadcast? ", "True")
				msg = recv(conn)
				print(msg)
				send(conn, "break", "False")
				# broadcast
				for people in online:
					messages.append([people, msg])
				print(messages)
				send(conn, "break", "False")
			elif option == str(6):
				print("Print groups")
				grouplist = ""
				for g in groups:
					grouplist += g.decode()
					if g != groups[-1]:
						grouplist += ", "
				send(conn, grouplist, "False")
				send(conn, "break", "False")
			elif option == str(7):
				print("Join group")
				send(conn, "Which group do you want to join? ", "True")
				msg = recv(conn)
				if msg.encode() not in groups:
					print("invalid group name " + msg)
					send(conn, "That is not a valid group", "False")
					send(conn, "break", "False")
					break
				room = groups.index(msg.encode())
				participants[room].append(userpass[user][0])
				print(participants)
				send(conn, "break", "False")
			elif option == str(8):
				print("Group message")
				send(conn, "What group would you like to send to? ", "True")
				group = recv(conn)
				send(conn, "What message would you like to send? ", "True")
				msg = recv(conn)
				room = groups.index(group.encode())
				for person in participants[room]:
					messages.append([person.decode(), msg])
				print(messages)
				send(conn, "break", "False")
			elif option == str(9):
				print("Leave group")
				send(conn, "What group do you want to leave? ", "True")
				group = recv(conn)
				if group.encode() not in groups:
					print("invalid group name " + msg)
					send(conn, "That is not a valid group", "false")
					send(conn, "break", "False")
					break
				room = groups.index(msg.encode())
				participants[room].remove(userpass[user][0])
				print(participants)
				send(conn, "break", "False")
			else:
				try :
					conn.sendall("Option not valid".encode())
				except socket.error:
					print("option not valid Send failed")
					conn.close()
					clients.remove(conn)
			for msg in messages:
				if msg[0] == userpass[user][0].decode():
					conn.send(msg[1].encode())

	else:
		try :
			conn.sendall("nalid".encode())
		except socket.error:
			print("nalid Send failed")
	print("Logged out")
	conn.close()
	if conn in clients:
		clients.remove(conn)

def receiveClients(s):
	global clients
	while 1:
		# Tips: Wait to accept a new connection (client) - blocking call
		conn, addr = s.accept()
		print("Connected with " + addr[0] + ":" + str(addr[1]))
		clients.append(conn)
		# Tips: start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
		start_new_thread(clientThread ,(conn,))

start_new_thread(receiveClients ,(s,))

'''
main thread of the server
print out the stats
'''
while 1:
	message = input()
	if message == 'messagecount':
		print("Since the server was opened " + str(count) + " messages have been sent")
	elif message == 'usercount':
		print("There are " + str(len(clients)) + " current users connected")
	elif message == 'storedcount':
		print("There are " + str(sum(len(m) for m in messages)) + " unread messages by users")
	elif message == 'newuser':
		user = raw_input('User:\n')
		password = raw_input('Password:')
		userpass.append([user, password])
		messages.append([])
		subscriptions.append([])
		print("User created")
s.close()

