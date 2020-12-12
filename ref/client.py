import socket	#for sockets
import sys	#for exit
import select
#from check import ip_checksum

def carry_around_add(a, b):
    c = a + b
    return (c & 0xffff) + (c >> 16)

def ip_checksum(msg):
    s = 0
    for i in range(0, len(msg) - 1, 2):
        w = ord(msg[i]) + (ord(msg[i+1]) << 8)
        s = carry_around_add(s, w)
    return ~s & 0xffff


def rdt_send(data, ack, sock, addr):
	checksum = ip_checksum(str(data))
	to_send = str(checksum) + str(ack) + data
	sock.sendto(to_send.encode(), addr)


try:
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
	print("Failed to create socket")
	sys.exit()

host = 'localhost';
port = 8888;

ack_seq = 0

inputs = [s]
outputs = []

timeout = 10
ack_rcvd = True

# readbale, writeable, exceptional = select.select( inputs, outputs, inputs, timeout)

while(1) :
	if ack_rcvd:
		msg = input('Enter message to send : ')
		rdt_send(msg, ack_seq, inputs[0], (host, port))
	
	readable, writable, exceptional = select.select( inputs, outputs, inputs, timeout)
	
	for tempSock in readable:
		try:
			d = tempSock.recvfrom(1024)
			reply = d[0].decode()
			addr = d[1]
		
			checksum = reply[:5]
			ack = reply[5]
			message = reply[6:]

			calcSum = ip_checksum(message)
			if int(calcSum) == int(checksum) and ack_seq == int(ack):
				ack_rcvd = True
				print("Ack recieved")
				ack_seq = 0 if int(ack) == 1 else 1
			else:
				print("Ack not recieved. Resending..")
				rdt_send(message, ack_seq, inputs[0], (host, port))
				ack_rcvd = False
		
	
		except socket.error as msg:
				print ("Error Code : " + str(msg[0]) + " Message " + msg[1].decode())
				sys.exit()
