import socket
import sys
from _thread import *
import getpass
import os
import time

'''
Function Definition
'''
def receiveThread(s):
	while True:
		try:
			reply = s.recv(4096) # receive msg from server
			
			# You can add operations below once you receive msg
			# from the server

		except:
			print("Connection closed")
			break
	

def tupleToString(t):
	s = ""
	for item in t:
		s = s + str(item) + "<>"
	return s[:-2]

def stringToTuple(s):
	t = s.split("<>")
	return t

'''
Create Socket
'''
try:
	# create an AF_INET, STREAM socket (TCP)
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as msg:
	print("Failed to create socket. Error code: " + str(msg[0]) + " , Error message : " + msg[1])
	sys.exit();
print ("Socket Created")

'''
Resolve Hostname
'''
host = '10.0.0.4'
port = 9486
try:
	remote_ip = socket.gethostbyname(host)
except socket.gaierror:
	print("Hostname could not be resolved. Exiting")
	sys.exit()
print("Ip address of " + host + " is " + remote_ip)

'''
Connect to remote server
'''
s.connect((remote_ip , port))
print("Socket Connected to " + host + " on ip " + remote_ip)


def recv(s):
	while True:
		try:
			msg = s.recv(4096)
			if msg:
				print(msg.decode())
				return stringToTuple(msg.decode())
		except:
			print("connection closed [recv]")
			break

'''
TODO: Part-1.1, 1.2: 
Enter Username and Passwd
'''
# Whenever a user connects to the server, they should be asked for their username and password.
# Username should be entered as clear text but passwords should not (should be either obscured or hidden). 
# get username from input. HINT: raw_input(); get passwd from input. HINT: getpass()

# Send username && passwd to server


# print("Please login to interact with the server")
intro = s.recv(1024)
print(intro.decode())
uname = input("Username: ")
passwd = getpass.getpass("Password: ")

logininfo = uname + "<>" + passwd
s.send(logininfo.encode())

'''
TODO: Part-1.3: User should log in successfully if username and password are entered correctly. A set of username/password pairs are hardcoded on the server side. 
'''
reply = s.recv(1024)
print(reply)
if reply.decode() == 'valid': # TODO: use the correct string to replace xxx here!

	# Start the receiving thread
	start_new_thread(receiveThread ,(s,))

	message = ""
	while True :

		# TODO: Part-1.4: User should be provided with a menu. Complete the missing options in the menu!
		message = input("Choose an option (type the number): \n 1. Logout \n 2. Change Password \n 3. Post a message \n messages to get messages\n")
		
		try :
			if message == "messages":
				s.recv(1024)
			if message == str(1):
				print("Logout")
				s.send("1".encode())
				s.recv(1024)
				break
			if message == str(2):
				print("change password")
				s.send("2".encode())
			if message == str(3):
				print("Post a message")
				s.send("3".encode())
			# Add other operations, e.g. change password
			while True:
				prompt = recv(s)
				if not prompt:
					print("MessageError")
					break
				if prompt[1] == "break":
					break
				if prompt[0] == "True":
					msg = input(prompt[1])
					s.sendall(msg.encode())
				else:
					print(prompt[1])
		except socket.error:
			print("Send failed")
			sys.exit()
else:
	print("Invalid username or passwword")

s.close()
