#Socket client example in python
from Tkinter import *
import tkinter as tk
import tkinter.scrolledtext as tkst
import thread


import socket   #for sockets
import sys  #for exit
from time import sleep 
#create an INET, STREAMing socket
open=False
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def send_message(msg):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
        port = 10101 
        s.connect(("127.0.0.1", port))
    except socket.error:
        print(socket.error)
        sys.exit()
    msg = x.contents.get()
    msg = msg.strip()
    x.contents.set("")
    if msg=="":
        pass
    print("-"+msg+"-")
    if msg=="\\exit":
        x.escape()
    messagefragments = break_message(msg)

    print(messagefragments)

    for fragment in messagefragments:
        s.send(fragment.encode('utf-8'))
        sleep(0.1)

    s.close()

    x.append_chat("You",msg+"\n")

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
    

class GUI(Frame):

    def createWidgets(self):

        # self.input["label"] = "Hello"
        self.contents = StringVar()
        self.chat_contents = StringVar()
        self.chat_contents = []
        
        self.input = Entry(self)
        self.input.pack({"side": "bottom","fill":"both","padx":"2","pady":"2"})
        self.input["textvariable"] = self.contents
        self.input.bind('<Key-Return>',send_message)
        self.input.bind('<Key-Escape>',self.escape)

        self.chat = Text(self)
        self.chat.pack({"side": "top","padx":"2","pady":"2"})
        self.chat.config(state=DISABLED)

    def get_chat():
        return self.chat_contents

    def append_chat(self,sender, msg):
        self.chat_contents.append((sender,msg))
        self.chat.config(state=NORMAL)
        self.chat.insert(END, sender+": "+msg)
        self.chat.config(state=DISABLED)

    def clear_chat():
        self.chat.delete(1,END)


    def __init__(self):
        root = Tk()
        Frame.__init__(self, root)
        self.root = root
        self.pack()
        self.createWidgets()


    def escape(self, event=None):
        self.root.destroy()
        exit(0)

x = GUI()

# def listen():
def listen():
    while(1):
        msg = raw_input()
        if msg=="":
            continue        
        # def task():
        if msg=="\\exit":
            x.escape()
            break
        x.append_chat("Random",msg+"\n")
        x.update()

x.after(0,listen)
x.mainloop()
