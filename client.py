#Socket client example in python
from Tkinter import *
import tkinter as tk
import tkinter.scrolledtext as tkst
import threading
from message import Message
import select


import socket   #for sockets
import sys  #for exit
from time import sleep 

MTU = 16

partial_msg = ""
def recv_message(sock):
    global partial_msg
    pkt = sock.recv(MTU)
    if pkt.decode("ascii")=="":
        msg = Message()
        msg.type = "disconnected"
        return msg
    partial_msg = partial_msg + pkt.decode("ascii")[1:]
    
    # print(pkt)
    if pkt.decode("ascii")[0]=='0':
        full_msg = Message(partial_msg)
        partial_msg = ""
        print "Recv : "+full_msg.toJSON()
        return full_msg

    

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

    # for fragment in messagefragments:
    sock.sendall(''.join(str(elem) for elem in messagefragments)) 
    print "Sent : "+msg.toJSON()
        # sleep(0.5)

#states
LOGIN_GET_USERNAME="LOGIN_GET_USERNAME"
LOGIN_GET_PASSWORD="LOGIN_GET_PASSWORD"
CONNECTING="CONNECTING"
AUTHENTICATING="AUTHENTICATING"
SELECT_USER="SELECT_USER"
CONVERSING="CONVERSING"
SIGNUP_GET_NAME="SIGNUP_GET_NAME"
SIGNUP_GET_USERNAME="SIGNUP_GET_USERNAME"
SIGNUP_GET_PASSWORD="SIGNUP_GET_PASSWORD"

import ldap

def login(username, password):

    try:
        ldap_con = ldap.open("cs252lab.cse.iitb.ac.in")
        print "Connected to LDAP server"
    except:
        print "Error connecting to LDAP server"
        sys.exit(1)

    opts = "cn="+username+",dc=cs252lab,dc=cse,dc=iitb,dc=ac,dc=in"

    try:
        ldap_con.simple_bind_s(opts,password)
        print "Authenticated by LDAP server"
        return True
    except:
        print "Invalid username or password"
        return False

def process(data=None):
    inp = ui.entry_text.get()
    ui.entry_text.set("")
    global state, client_name,client_username, client_password, server_sock, port, online_users, current_dst
    print "State = "+state
    if state==LOGIN_GET_USERNAME:
        if inp!="\\register":
            client_username = inp
            print "Got client's username: "+client_username
            ui.clear_chat()
            ui.input.config(show="*")
            ui.append_chat(None, "Enter password: ")
            state = LOGIN_GET_PASSWORD
        else:
            print "Client wants to register"
            ui.clear_chat()
            ui.append_chat(None,"Enter your name:")
            state = SIGNUP_GET_NAME
    elif state==SIGNUP_GET_NAME:
        print "Got new client's name"
        client_name = inp
        ui.clear_chat()
        ui.append_chat(None,"Enter username:")
        state = SIGNUP_GET_USERNAME

    elif state==SIGNUP_GET_USERNAME:
        print "Got new client's username"
        client_username = inp
        ui.clear_chat()
        ui.append_chat(None,"Enter password:")
        ui.input.config(show="*")
        state = SIGNUP_GET_PASSWORD
    elif state==SIGNUP_GET_PASSWORD:
        client_password = inp
        print "Got new client's password"
        ui.input.config(show="")
        success = login(client_username, client_password)

        if not success:
            state = SIGNUP_GET_USERNAME
            ui.clear_chat()
            ui.append_chat(None, "Invalid username or password")
            ui.append_chat(None, "Enter username: ")
        else:
            msg = Message()
            msg.type = "register"
            msg.username = client_username
            msg.password = client_password
            msg.name = client_name

            send_message(server_sock,msg)
            print "Sent authentification request to chat server"

            listen_thread = threading.Thread(target=listen)
            listen_thread.daemon = True
            listen_thread.start()
            state = AUTHENTICATING

    elif state==LOGIN_GET_PASSWORD:
        client_password = inp
        print "Got client's password: "+ client_password
        ui.input.config(show="")

        success = login(client_username, client_password)

        if not success:
            state = LOGIN_GET_USERNAME
            ui.clear_chat()
            ui.append_chat(None, "Invalid username or password")
            ui.append_chat(None, "Enter username: ")
        else:
            msg = Message()
            msg.type = "login_request"
            msg.username = client_username
            msg.password = client_password

            send_message(server_sock,msg)
            print "Sent authentification request to chat server"

            listen_thread = threading.Thread(target=listen)
            listen_thread.daemon = True
            listen_thread.start()
            state = AUTHENTICATING
    elif state==CONVERSING:

        if inp == "\\clear":
            ui.clear_chat()
        elif inp == "\\list":
            state = SELECT_USER
            ui.clear_chat()
            if len(online_users)==0:
                ui.append_chat(None,"Waiting for other users to come online...")
            else:
                ui.append_chat(None,"Following users are online:-")
                for user in online_users:
                    ui.append_chat(None,user)

        elif inp.split()[0] == '\\connect':
            next_dst = inp.split()[1]
            if next_dst not in online_users:
                ui.append_chat("(Please select a user from list)")
            else:
                current_dst = next_dst    
        else:
            msg = Message()
            ui.append_chat("You",inp)
            msg.content = inp
            msg.type = "chat"
            msg.sender = username
            msg.destination = current_dst
            ui.entry_text.set("")
            send_message(server_sock,msg)
    elif state==SELECT_USER:
        user = inp
        ui.entry_text.set("")
        print online_users
        if user not in online_users and len(online_users)>0:
            ui.append_chat(None, "Please select a user from list")
        elif len(online_users)>0:
            current_dst = user
            print "Second person set to "+current_dst
            state = CONVERSING
            ui.clear_chat()
            
        #send_message(server_sock,msg)
    

def escape(event=None):
    global server_sock
    server_sock.close()
    ui.root.destroy()
    sys.exit(0)

class UI(Frame):

    def createWidgets(self):

        # self.input["label"] = "Hello"
        self.entry_text = StringVar()
        self.chat_content = StringVar()
        self.chat_content = []
        
        self.input = Entry(self)
        self.input.pack({"side": "bottom","fill":"both","padx":"2","pady":"2"})
        self.input["textvariable"] = self.entry_text
        self.input.bind('<Key-Return>',process)
        self.input.bind('<Key-Escape>',escape)

        self.chat = Text(self)
        self.chat.pack({"side": "top","padx":"2","pady":"2"})
        self.chat.config(state=DISABLED)
        self.append_chat(None, "Enter username: (\\register to register to chat server)")

    def get_chat(self):
        return self.chat_content

    def append_chat(self,sender, msg):
        self.chat_content.append((sender,msg))
        self.chat.config(state=NORMAL)
        if sender!=None:
            self.chat.insert(END, sender+": "+msg+"\n")
        else:
            self.chat.insert(END, msg+"\n")
        self.chat.config(state=DISABLED)

    def clear_chat(self):
        self.chat.config(state=NORMAL)
        self.chat.delete('1.0',END)
        self.chat.config(state=DISABLED)


    def __init__(self):
        root = Tk()
        Frame.__init__(self, root)
        self.root = root
        self.pack()
        self.createWidgets()

state = CONNECTING
client_username = None
client_password = None
client_name = None
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 10111

def connect():
    global state
    while state==CONNECTING:
        try:
            print "Trying to connect to chat server"
            server_sock.settimeout(5)
            server_sock.connect(("127.0.0.1", port))
            print "Connected to chat server"
            state = LOGIN_GET_USERNAME
        except socket.error:
            ui.append_chat(None, "Connection to chat server timed out. Retrying in 5 seconds...")
            sleep(5000)
    
def listen():
    global state, client_name, ui
    while(1):
        if server_sock in select.select([server_sock],[],[])[0]:
            msg = recv_message(server_sock)
            if not msg:
                continue
            if state == AUTHENTICATING:
                if msg.type=="login_success" or msg.type=="register_success":
                    ui.clear_chat()
                    state = SELECT_USER
                    client_name = msg.name
                    if msg.type=="register_success" and msg.duplicate:
                        ui.append_chat("User was already registered")
                    ui.append_chat(None,"Welcome "+client_name+"!")
                    if len(msg.otherusers)==0:
                        ui.append_chat(None,"Waiting for other users to come online...")
                    else:
                        ui.append_chat(None,"Following users are online:-")
                        for user in msg.otherusers:
                            ui.append_chat(None,user)
                            online_users.add(user)
                    print "Logged in to chat server"
                elif msg.type=="login_failure":
                    ui.clear_chat()
                    ui.append_chat(None,"User not registered")
                    ui.append_chat(None, "Enter username: (\\register to register to chat server)")
                    state = LOGIN_GET_USERNAME
                    print "Failed to log in to chat server"

            elif msg.type == "chat":
                if state==CONVERSING and current_dst==msg.sender:
                    ui.append_chat(msg.sender, msg.content)
                else:
                    ui.append_chat("("+msg.sender+" sent a message",msg.content+")")
            elif msg.type == "new_login":
                online_users.add(msg.new_user)
                if state==SELECT_USER:
                    ui.clear_chat()
                    ui.append_chat(None,"Following users are online:-")
                    for user in online_users:
                        ui.append_chat(None,user)
                        online_users.add(user)
                else:
                    ui.append_chat(None,"(" + msg.new_user + " came online)")

            elif msg.type == "user_offline":
                ui.append_chat(None, "("+msg.data + " has gone offline)")
                online_users.remove(msg.data)


ui = UI()
connect()

clear = False
online_users = set()
current_dst = None

ui.mainloop()
