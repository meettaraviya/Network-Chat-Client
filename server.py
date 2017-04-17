import socket,time
# import thread
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

MTU = 16

# print(host)
# print(type(host))
port = 10101

s.bind(("",port))
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.listen(1000)

msg=""

client,addr=s.accept()
print("Connection %s"% str(addr))
while True:
	# curr=time.ctime(time.time())+"\r\n"
	# client.send(curr.encode('ascii'))
	pkt = client.recv(MTU)
	if pkt.decode("ascii")=="":
		continue
	else:
		print(pkt.decode("ascii"))
	msg = msg + pkt.decode("ascii")[1:]
	# print(pkt)
	if pkt.decode("ascii")[0]=='0':
		print(msg)
		msg=""
		client,addr=s.accept()
		print("Connection %s"% str(addr))

print(msg)

