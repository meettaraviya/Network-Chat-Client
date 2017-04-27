port = 10111
import socket,time,threading, select
import message
# import thread
import csv

MTU = 16

allthechats = {}

def break_message(msg):
	frags = []
	MTU = 16
	flag = "1"
	while(MTU-1 < len(msg)):
		frags.append(flag + msg[0 : (MTU-1)])
		msg = msg[MTU-1:]

	flag = "0"
	frags.append(flag + msg)		
	return frags

def send_message(sock, msg):
	messagefragments = break_message(msg.toJSON())
	sock.sendall(''.join(str(elem) for elem in messagefragments))


def is_valid_user(username,passwd):
	return username in user_data and user_data[username]["password"] == passwd	


def add_user(username,passwd):
	df1 = pd.read_csv('credentials.csv',header = 0)
	if not is_valid_user(username,passwd):
		a=pd.DataFrame({'Username':[username],'Password':[passwd]})
		b = df1.append(a,ignore_index = True)
		b.to_csv('credentials.csv')

fragments = {}

def recvmessage(sock):
	print "receiving"
	pkt = sock.recv(MTU)
	print "46"
	if sock not in fragments:
		fragments[sock] = ""
	if pkt.decode("ascii")=="":
		msg = Message()
		msg.type = "disconnected"
		print "received"
		return msg
	else:
		print(pkt.decode("ascii"))
	# print(pkt)
	if pkt.decode("ascii")[0]=='1':
		fragments[sock] = fragments[sock] + pkt.decode("ascii")[1:]
		return None
	else:
		fragments[sock] = fragments[sock] + pkt.decode("ascii")[1:]
		m = Message(fragments[sock])
		fragments[sock] = ""
		print m.toJSON()
		return m



from message import Message

user_sock = {}

def process(m, sock):
	print "1"
	if m.type == "login_request" :
		print "2"
		if is_valid_user(m.username, m.password) :
			print "3"
			msg = Message()
			msg.type = "login_success"
			Online_friends = []
			for x in user_data[m.username]["friends"]:
				if x in OnlineUsers:
					Online_friends.append(x)
			msg.otherusers = Online_friends
			#Now we need to send only this user's friend list
			
			print "Login success, sending"
			send_message(sock, msg)
			OnlineUsers.append(m.username)
			user_sock[m.username] = sock
			print "Login success, sent"
			msg2 = Message()
			msg2.type = "new_login"
			msg2.new_user = m.username
			for user in OnlineUsers:
				if (user!=m.username) and (user in user_data[m.username]["friends"]):
					send_message(user_sock[user],msg2)
					print user

		else:
			msg.type = "login_failure"
			print "Login fail"
			send_message(sock, msg)

	if m.type == "chat" :
		failmsg = Message()
		failmsg.content = m.destination + " is offline"
		failmsg.type = "fail_msg"
		print
		if m.sender < m.destination :
			print "part1"
			temptuple = allthechats[m.sender+","+m.destination] 
			temptuple.append((m.sender,m.content))
			allthechats[m.sender+","+m.destination] = temptuple 
		else:
			print "part2"
			temptuple = allthechats[m.destination+","+m.sender] 
			temptuple.append((m.sender,m.content))
			allthechats[m.destination+","+m.sender] = temptuple

		print allthechats

		if m.destination in OnlineUsers :
			send_message(user_sock[m.destination], m)
		else:
		 	send_message(sock,failmsg)

	if m.type == "chat_history" :
		if ((m.sender+","+m.content) not in allthechats) and ((m.content+","+m.sender) not in allthechats) :
			print "convo not present yet"
			if m.sender < m.content :
				print "exex"
				temptuple = [] 
				allthechats[m.sender+","+m.content] = temptuple 
			else:
				print "fdfd"
				temptuple = [] 
				allthechats[m.content+","+m.sender] = temptuple
		print "power"
		msgf = Message()
		msgf.type = "chat_history_resp"
		if m.sender < m.content :
			msgf.content = allthechats[m.sender+","+m.content]
			
		else: 
			msgf.content = allthechats[m.content+","+m.sender]

		print msgf.content

		send_message(sock, msgf)


	if m.type == "disconnected" :
		for ppl in user_sock:
			if user_sock[ppl] == sock:
				OnlineUsers.remove(ppl)
				CONNECTION_LIST.remove(sock)
				usertobedeleted = ppl
		user_sock.pop(usertobedeleted, None)
	# send notification to friends of this offline user that user has gone offline
		msgx = Message()
		msgx.type = "user_offline"
		msgx.content = usertobedeleted
		for userx in OnlineUsers:
			if userx in user_data[usertobedeleted]["friends"]:
				send_message(user_sock[userx], msgx)
	pass

import json

user_data = {}

with open('data.json') as data_file:	
	data = json.load(data_file)
	for user in data:
		user_data[user["username"]] = user


# print(msg)

OnlineUsers = []

server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

MTU = 16

# print(host)
# print(type(host))

server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(("",port))
server_socket.listen(1000)


# List to keep track of socket descriptors
CONNECTION_LIST = []


CONNECTION_LIST.append(server_socket)

print ("Chat server started on port " + str(port))

while True:
# Get the list sockets which are ready to be read through select
	try:
		read_sockets = select.select(CONNECTION_LIST,[],[])[0]

		for sock in read_sockets:
		#New connection 
			if sock == server_socket:
				sockfd,addr = server_socket.accept()
				CONNECTION_LIST.append(sockfd)
				print ("Client (%s, %s) connected" % addr)
			
			else:
			# Data recieved from client, process it
				# try:	   
				print sock
				data = recvmessage(sock)
				if data!=None:
					print data.toJSON()
					process(data, sock)
				else:
					print "More fragments to come"
				# except:
				# 	print "error in receiving"
	except:
		server_socket.close()

# print("Connection %s"% str(addr))
# while True:
# 	# curr=time.ctime(time.time())+"\r\n"
# 	# client.send(curr.encode('ascii'))
# 	pkt = client.recv(MTU)
# 	if pkt.decode("ascii")=="":
# 		continue
# 	else:
# 		print(pkt.decode("ascii"))
# 	msg = msg + pkt.decode("ascii")[1:]
# 	# print(pkt)
# 	if pkt.decode("ascii")[0]=='0':
# 		print(msg)
# 		msg=""
# 		client,addr=s.accept()
# 		print("Connection %s"% str(addr))
# print(msg)
