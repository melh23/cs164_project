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
	s.setblocking(False)
	while True:
		try:
			msg = s.recv(4096)
			if msg:
				# print(msg.decode())
				s.send("ACK<>".encode() + msg)
				s.setblocking(True)
				helpmeplz = s.recv(4069)
				return stringToTuple(msg.decode())
		except:
			time.sleep(0.1)

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
		message = input("Choose an option (type the number): \n 1. Toggle ECN \n 2. Logout \n 3. Change Password \n 4. Get messages \n 5. Post a message \n 6. Broadcast \n 7. Print groups \n 8. Join a group \n 9. Group message \n 10. Leave group \n")
		
		try :
			option = ""
			if message == str(1):
				print("Toggle ECN")
				option = "1"
			if message == str(2):
				print("Logout")
				s.send("2".encode())
				s.recv(1024)
				break
			if message == str(3):
				print("change password")
				option = "3"
			if message == str(4):
				print("Get messages")
				option = "4"
			if message == str(5):
				print("Post a message")
				option = "5"
			if message == str(6):
				print("Broadcast")
				option = "6"
			if message == str(7):
				print("Print groups")
				option = "7"
			if message == str(8):
				print("Join group")
				option = "8"
			if message == str(9):
				print("Group message")
				option = "9"
			if message == str(10):
				print("Leave group")
				option = "10"
			# Add other operations, e.g. change password
			s.send(option.encode())
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
