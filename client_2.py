#Socket client example in python
from Tkinter import *
import Tkinter as tk
import threading
from message import Message
import select


import socket   #for sockets
import sys  #for exit
from time import sleep 
#create an INET, STREAMing socket
open=False

MTU = 16

partial_msg = ""
def recvmessage(sock):
    global partial_msg
    print "1"
    pkt = sock.recv(MTU)
    print "2"
    if pkt.decode("ascii")=="":
        msg = Message()
        msg.type = "disconnected"
        return msg
    else:
        print(pkt.decode("ascii"))
    partial_msg = partial_msg + pkt.decode("ascii")[1:]
    
    # print(pkt)
    if pkt.decode("ascii")[0]=='0':
        full_msg = Message(partial_msg)
        partial_msg = ""
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
    print "sent"
        # sleep(0.5)


def process(data=None):
    global state, username, password, server_sock, port, online_friends, current_dst
    print "State = "+state
    if state=="waiting_for_username":
        username = ui.entry_text.get()
        print "Username = "+username
        ui.entry_text.set("")

        ui.clear_chat()
        # ui.input.config(show="*")
        ui.append_chat(None, "Enter password: ")
        state = "waiting_for_password"
    elif state=="waiting_for_password" or state=="failed_connecting":
        if state=="waiting_for_password":
            password = ui.entry_text.get()
            ui.entry_text.set("")
            ui.clear_chat()
            # ui.input.config(show="")
            ui.append_chat(None, "Connecting... ")

        try:
            server_sock.connect(("127.0.0.1", port))
            print "Connected to server"
        except socket.error:
            print(socket.error)
            state="failed_connecting"
            ui.clear_chat()
            ui.append_chat(None, "Failed to connect. Press Enter to retry.")
            return

        msg = Message()
        msg.type = "login_request"
        msg.username = username
        msg.password = password

        send_message(server_sock,msg)
        state = "connecting"
        listen_thread = threading.Thread(target=listen)
        listen_thread.daemon = True
        listen_thread.start()

    elif state=="conversing":
        print "conversing"
        txt = ui.entry_text.get()

        if txt == "\\clear":
            ui.clear_chat()
        elif txt.split()[0] == "\\connect":
            us = txt.split()[1]
            if us not in online_friends:
                ui.append_chat("Please select a friend from list")
            else:
                current_dst = us
                msghistory = Message()
                msghistory.type = "chat_history"
                msghistory.content = user
                msghistory.sender = username
                send_message(server_sock, msghistory)

        else:
            msg = Message()
            ui.append_chat("You",txt)
            msg.content = txt
            msg.type = "chat"
            msg.sender = username
            msg.destination = current_dst
            ui.entry_text.set("")
            send_message(server_sock,msg)

    elif state=="select_user":
        print "select_user"
        user = ui.entry_text.get()
        ui.entry_text.set("")
        print online_friends
        ui.append_chat(None,"Select a friend from List to chat with")
        if user not in online_friends:
            ui.append_chat(None, "Please select a friend from list")
        else:
            current_dst = user
            print " current dest  = " + current_dst
            state = "conversing"
            ui.clear_chat()
            msghistory = Message()
            msghistory.type = "chat_history"
            msghistory.content = user
            msghistory.sender = username
            send_message(server_sock, msghistory)

        #send_message(server_sock,msg)
    

def escape(event=None):
    ui.root.destroy()
    exit(0)

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
        self.append_chat(None, "Enter username: ")

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
        print "Cleared screen"


    def __init__(self):
        root = Tk()
        Frame.__init__(self, root)
        self.root = root
        self.pack()
        self.createWidgets()

state = "waiting_for_username"
username = None
password = None
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 10111


ui = UI()

client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


clear = False
online_friends = set()
current_dst = None
# def listen():
def listen():
    global state
    while(1):
        print "1"
        if server_sock in select.select([server_sock],[],[])[0]:
            msg = recvmessage(server_sock)
            if not msg:
                continue
            if msg.type=="login_success" and state == "connecting":
                ui.clear_chat()
                print msg.toJSON()
                state = "select_user"
                if len(msg.otherusers)==0:
                    ui.append_chat(None,"Waiting for other users to come online...")
                else:
                    ui.append_chat(None,"Following friends are online:-")
                    for user in msg.otherusers:
                        ui.append_chat(None,user)
                        online_friends.add(user)
            elif msg.type == "chat":
                if state=="conversing" and current_dst==msg.sender:
                    ui.append_chat(msg.sender, msg.content)
                else:
                    ui.append_chat("("+msg.sender+" sent a message",msg.content+")")
            elif msg.type == "new_login":
                if not online_friends:
                    ui.clear_chat()
                    ui.append_chat(None,"Following friends are online:-")
                online_friends.add(msg.new_user)
                ui.append_chat(None,msg.new_user)
            elif msg.type == "user_offline":
                ui.append_chat(None, msg.content + " has gone offline ")
                online_friends.remove(msg.content)

            elif msg.type == "chat_history_resp" :
                ui.clear_chat()
                ui.entry_text.set("")
                conversation = msg.content
                for parts in conversation:
                    if parts[0] == username :
                        ui.append_chat("You", parts[1])
                    else :
                        ui.append_chat(parts[0], parts[1])
                
ui.mainloop()
