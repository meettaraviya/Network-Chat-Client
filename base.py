#Socket client example in python
from Tkinter import *
import tkinter as tk
import tkinter.scrolledtext as tkst
import thread
from message import Message


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
    


class GUI(Frame):

    def createWidgets(self):

        # self.input["label"] = "Hello"
        self.entry_text = StringVar()
        self.chat_content = StringVar()
        self.chat_content = []
        
        self.input = Entry(self)
        self.input.pack({"side": "bottom","fill":"both","padx":"2","pady":"2"})
        self.input["textvariable"] = self.entry_text
        self.input.bind('<Key-Return>',self.process)
        self.input.bind('<Key-Escape>',self.escape)

        self.chat = Text(self)
        self.chat.pack({"side": "top","padx":"2","pady":"2"})
        self.chat.config(state=DISABLED)
        self.append_chat(None, "Enter username: ")
        self.state = "waiting_for_username"
        self.username = None
        self.password = None
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = 10111

    def get_chat(self):
        return self.chat_content

    def append_chat(self,sender, msg):
        self.chat_content.append((sender,msg))
        self.chat.config(state=NORMAL)
        if sender!=None:
            self.chat.insert(END, sender+": "+msg)
        else:
            self.chat.insert(END, msg)
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


    def process(self,data=None):
        print self.state
        if self.state=="waiting_for_username":
            self.username = self.entry_text.get()
            print self.username
            self.entry_text.set("")
            self.clear_chat()
            self.input.config(show="*")
            self.append_chat(None, "Enter password: ")
            self.state = "waiting_for_password"
        elif self.state=="waiting_for_password" or self.state=="failed_connecting":
            if self.state=="waiting_for_password":
                self.password = self.entry_text.get()
                self.entry_text.set("")
                self.clear_chat()
                self.input.config(show="")
                self.append_chat(None, "Connecting... ")

            try:
                self.server_sock.connect(("127.0.0.1", self.port))
                print "Connected to server"
            except socket.error:
                print(socket.error)
                self.state="failed_connecting"
                self.clear_chat()
                self.append_chat(None, "Failed to connect. Press Enter to retry.")
                return

            msg = Message()
            msg.type = "login_request"
            msg.username = self.username
            msg.password = self.password

            send_message(self.server_sock,msg)
            self.state = "connecting"
            self.after(0,listen)

        elif self.state=="conversing":
            if data==None:
                msg = Message()
                msg.content = self.entry_text.get()
                msg.type = "chat"
                msg.sender = username
                self.entry_text.set("")
            else:
                msg = Message()
                msg.content = data
                msg.type = "chat"
                msg.sender = username
                self.entry_text.set("")
            try:   
                self.server_sock.connect(("127.0.0.1", self.port))
            except socket.error:
                print(socket.error)
                sys.exit()
            if msg=="":
                pass
            if msg=="\\exit":
                self.server_sock.close()
                self.escape()

            send_message(server_sock,msg)



    def escape(self, event=None):
        self.root.destroy()
        exit(0)

x = GUI()

client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

import select
# def listen():
def listen():

    while(1):
        if x.server_sock in select.select([x.server_sock],[],[])[0]:
            msg = recvmessage(x.server_sock)
            if not msg:
                continue
            if msg.type=="login_success" and x.state == "connecting":
                x.state = "conversing"
                x.clear_chat()
                x.append_chat(None, "Connected.")
                print "conv"

x.mainloop()
