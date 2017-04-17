#Socket client example in python
 
import socket   #for sockets
import sys  #for exit
from time import sleep 
#create an INET, STREAMing socket
def break_message(msg) :
	frags = []
	MTU = 16
	flag = "1"
	while(MTU-1 < len(msg)):
		frags.append(flag + msg[0 : (MTU-1)])
		msg = msg[MTU-1:]

	flag = "0"
	frags.append(flag + msg)	
	return frags


try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
    print('Failed to create socket')
    sys.exit()

print('Socket Created')
 
port = 10101 
s.connect(("127.0.0.1", port))
 

 
#Send some data to remote server
message = "01234567"*10

messagefragments = break_message(message)

print(messagefragments)

for fragment in messagefragments:
	s.send(fragment.encode('utf-8'))
	sleep(0.1)

# s.close()
#print('Message send successfully')
 
#Now receive data
#reply = s.recv(8008)
 
#print(reply)