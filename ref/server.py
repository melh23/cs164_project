import socket
import sys
import select
#from check import ip_checksum

HOST = ''
PORT = 8888

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
	checksum = ip_checksum(data)
	to_send = str(checksum) + str(ack) + data
	sock.sendto(to_send.encode(), addr)


try :
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	print ("Socket created")
except socket.error as msg :
	print ("Failed to create socket. Error Code : " + str(msg[0]) + " Message " + msg[1])
	sys.exit()


try:
	s.bind((HOST, PORT))
except socket.error as msg:
	print ("Bind failed. Error Code : " + str(msg[0]) + " Message " + msg[1])
	sys.exit()
	
print ("Socket bind complete")
ack_val = 0

while 1:
	d = s.recvfrom(1024)
	data = d[0].decode()
	addr = d[1]

	checksum = data[:5]
	sequence = data[5]
	message = data[6:]

	if not data: 
		break

	print(message)

	calcSum = ip_checksum(message)
	# print("calc vs check")
	# print(calcSum)
	# print(checksum)
	# print(int(calcSum) == int(checksum))
	if int(calcSum) == int(checksum):
		# rdt_send(message, ack_val, s,  addr)
		# print("sequence and ack")
		# print(sequence)
		# print(ack_val) 
		if int(sequence) == ack_val:
			print("Sending ACK")
			msg = "ACK"
			rdt_send(msg, sequence, s, addr)
			ack_val = 0 if int(sequence) == 1 else 1
	else:
		print("Something went wrong! Sending NAK")
		nak = 0 if ack_val == 1 else 1
		rdt_send("NAK", nak, s, addr)
	
	# reply = 'OK...' + data.decode()
	
	# s.sendto(reply.encode() , addr)
	# print ("Message[" + (addr[0]) + ":" + str(addr[1]) + "] - " + data.strip().decode())
	
s.close()
