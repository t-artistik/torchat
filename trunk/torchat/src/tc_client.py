# -*- coding: UTF-8 -*-

##############################################################################
#                                                                            #
# Copyright (c) 2007-2008 Bernd Kreuss <prof7bit@gmail.com>                  #
#                                                                            #
# This program is licensed under the GNU General Public License V3,          #
# the full source code is included in the binary distribution.               #
#                                                                            #
# Included in the distribution are files from other open source projects:    #
# - TOR Onion Router (c) The Tor Project, 3-clause-BSD                       #
# - SocksiPy (c) Dan Haim, BSD Style License                                 #
# - Gajim buddy status icons (c) The Gajim Team, GNU GPL                     #
#                                                                            #
##############################################################################

#change OWN_HOSTNAME to yours, or it will NOT work
#you find it in your hidden service dir in the file
#hostname. Leave the tld (.onion) away.
#(On windows in portable mode this is done automatically.)
OWN_HOSTNAME = "utvrla6mjdypbyw6" #.onion
TRY_PORTABLE_MODE = True

#configure the following if your Tor is running on a separate machine
TOR_SERVER = "127.0.0.1"
TOR_SERVER_SOCKS_PORT = 9050
TOR_SERVER_CONTROL_PORT = 9051

#configure where to listen for connections *from* the Tor server
LISTEN_INTERFACE = "127.0.0.1"
LISTEN_PORT = 11009

import SocksiPy.socks as socks
import socket
import threading
import random
import time
import sys
import os
import subprocess
import config

TORCHAT_PORT = 11009 #do NOT change this.
STATUS_OFFLINE = 0
STATUS_HANDSHAKE = 1
STATUS_ONLINE = 2
STATUS_AWAY = 3
STATUS_XA = 4

def isWindows():
    return "win" in sys.platform

def splitLine(text):
    sp = text.split(" ")
    try:
        a = sp[0]
        b = " ".join(sp[1:])
    except:
        a = text
        b = ""
    return a, b

def escape(text):
    text = text.replace("\\", "\\/") #replace \ with \/
    text = text.replace("\n", "\\n")  #replace linebreak with \n
    return text

def unescape(text):
    text = text.replace("\\n", "\n") #replace \n with linebreak
    text = text.replace("\\/", "\\") #replace \/ with \
    return text


class MProtocolMsg(type):
    #Meta-Class for ProtocolMsg. It automagically creates a hash for 
    #mapping protocol-commands and corresponding ProtocolMsg-subclasses
    subclasses = {}
    def __init__(cls, name, bases, dict):
        #this will be executed whenever a ProtocolMsg gets *defined*
        #(happens once at the time when this module is imported).
        #the commands and their classes will be stored in 
        #the static member MProtocolMsg.subclasses
        cls.subclasses[dict["command"]] = cls
        super(MProtocolMsg, cls).__init__(name, bases, dict)

        
class ProtocolMsg(object):
    __metaclass__ = MProtocolMsg
    command = ""
    #the base class for all ProtocolMsg-classes. All message classes
    #must inherit from this and declare the static member command
    #which is used (by the metaclass-magic-voodoo;-) to map between the
    #command-string and the corresponding message class

    def __init__(self, connection, command, text):
        self.connection = connection
        if connection:
            self.buddy = connection.buddy
            self.bl = connection.bl
        else:
            self.buddy = None
            self.bl = None
        self.command = command
        self.text = text

    def execute(self):
        #generic message does nothing
        pass

    def getLine(self):
        return self.command + " " + self.text

    def send(self, buddy):
        #FIXME: what if it is None?
        buddy.send(self.getLine())

    
def ProtocolMsgFromLine(conn, line):
    #this is the factory for producing instances of ProtocolMsg classes.
    #it separates the first word from the line, looks up the corresponding
    #ProtocolMsg subclass which can handle this kind of protocol message
    #and returns an instance. If no class matches the command string it
    #returns a ProtocolMsg instance which is generic and just does nothing.
    command, text = splitLine(line)
    try:
        return MProtocolMsg.subclasses[command](conn, command, text)
    except:
        return ProtocolMsg(conn, command, text)

 
class ProtocolMsg_ping(ProtocolMsg):
    command = "ping"
    def __init__(self, *args):
        ProtocolMsg.__init__(self, *args)
        #the sender address is in the text. we take it for granted.
        address, self.answer = splitLine(self.text)
        self.buddy = self.connection.bl.getBuddyFromAddress(address)

    def execute(self):
        if self.buddy:
            answer = ProtocolMsg(None, "pong", self.answer)
            answer.send(self.buddy)


class ProtocolMsg_pong(ProtocolMsg):
    command = "pong"
    def __init__(self, *args):
        ProtocolMsg.__init__(self, *args)
        #pong message is used to identify and authenticate the incoming 
        #connection. we search all our buddies for the corresponding random
        #string to identify which buddy is replying here.
        self.buddy = self.connection.bl.getBuddyFromRandom(self.text)

    def execute(self):
        #if the pong is found to belong to a known buddy we can now
        #safely assign this connection to this buddy and regard the
        #handshake as completed.
        if self.buddy:
            if self.buddy.conn_in == None:
                self.buddy.conn_in = self.connection
                self.buddy.status = STATUS_ONLINE
                self.connection.buddy = self.buddy

                
class ProtocolMsg_message(ProtocolMsg):
    command = "message"
    #this is a normal text chat message.
    def execute(self):
        #give buddy and text to bl. bl knows how to deal with it.
        if self.buddy:
            self.buddy.bl.onChatMessage(self.buddy, unescape(self.text))


class ProtocolMsg_status(ProtocolMsg):
    command = "status"
    #this is a status message.
    def execute(self):
        #set the status flag of the corresponding buddy
        if self.buddy:
            if self.text == "available":
                self.buddy.status = STATUS_ONLINE
            if self.text == "away":
                self.buddy.status = STATUS_AWAY
            if self.text == "xa":
                self.buddy.status = STATUS_XA
    
    
class Buddy(object):
    def __init__(self, address, buddy_list, name=""):
        self.bl = buddy_list
        self.address = address
        self.name = name
        self.random1 = str(random.getrandbits(256))
        self.random2 = str(random.getrandbits(256))
        self.conn_out = None
        self.conn_in = None
        self.status = STATUS_OFFLINE
    
    def connect(self):
        self.conn_out = OutConnection(self.address + ".onion", self.bl, self)
        self.ping()
        
    def disconnect(self):
        if self.conn_out != None:
            self.conn_out.close()
            self.conn_out = None
        if self.conn_in != None:
            self.conn_in.close()
            self.conn_in = None
        self.status = STATUS_OFFLINE
        
    def send(self, text):
        if self.conn_out == None:
            self.connect()
        self.conn_out.send(escape(text) + "\n")
        
    def processMessage(self, connection, text):
        self.bl.processMessage(connection, text)
    
    def getSendBufferSize(self):
        return self.conn_out.getSendBufferSize()
        
    def sendFile(self, filename, gui_callback):
        sender = FileSender(self, filename, gui_callback)
        return sender
    
    def ping(self):
        if self.conn_out == None:
            self.connect()
        else:
            self.send("ping %s %s" % (OWN_HOSTNAME, self.random1))
            self.sendStatus()
                
    def sendStatus(self):
        if self.conn_out != None:
            status = ""
            if self.bl.own_status == STATUS_ONLINE:
                status = "available"
            if self.bl.own_status == STATUS_AWAY:
                status = "away"
            if self.bl.own_status == STATUS_XA:
                status = "xa"
            if status != "":
                self.send("status %s" % status)
        
    def getDisplayName(self):
        if self.name != "":
            line = "%s (%s)" % (self.address, self.name)
        else:
            line = self.address
        return line
    

class BuddyList(object):
    #the buddy list object is somewhat like a central API.
    #All functionality and access to all other objects should
    #be possible with it's methods. Most other objects carry
    #a reference to the one and only BuddyList object around 
    #to be able to find and interact with other objects.
    def __init__(self, guiChatCallback):
        self.guiChatCallback = guiChatCallback
        
        if TRY_PORTABLE_MODE:
            startPortableTor()
        
        self.file_sender = {}
        self.file_receiver = {}
        
        self.listener = Listener(self)
        self.own_status = STATUS_ONLINE
        
        filename = os.path.join(config.getDataDir(), "buddy-list.txt")
        
        #create empty buddy list file if it does not already exist
        f = open(filename, "a")
        f.close()
        
        f = open(filename, "r")
        l = f.read().split("\n")
        f.close
        self.list = []
        for line in l:
            line = line.rstrip()
            if len(line) > 15:
                address = line[0:16]
                if len(line) > 17:
                    name = line[17:]
                else:
                    name = ""
                buddy = Buddy(address, self, name)
                buddy.connect()
                self.list.append(buddy)
        
        found = False
        for buddy in self.list:
            if buddy.address == OWN_HOSTNAME:
                found = True
        
        if not found:
            self.addBuddy(Buddy(OWN_HOSTNAME, self, "myself"))
        
        self.test()

    def save(self):
        f = open(os.path.join(config.getDataDir(), "buddy-list.txt"), "w")
        for buddy in self.list:
            line = "%s %s" % (buddy.address, buddy.name)
            f.write("%s\r\n" % line.rstrip())
        f.close()

    def test(self):
        for buddy in self.list:
            buddy.ping()
            
        self.timer = threading.Timer(15, self.test)
        self.timer.start()
        
    def addBuddy(self, buddy):
        if self.getBuddyFromAddress(buddy.address) == None:
            self.list.append(buddy)
            self.save()
            buddy.connect()
            return buddy
        else:
            return False
        
    def removeBuddy(self, buddy_to_remove):
        try:
            buddy_to_remove.disconnect()
            self.list.remove(buddy_to_remove)
            self.save()
            return True
        except:
            return False
        
    def removeBuddyWithAddress(self, address):
        buddy = self.getBuddyFromAddress(address)
        if buddy != None:
            self.removeBuddy(buddy)
        
    def getBuddyFromAddress(self, address):
        for buddy in self.list:
            if buddy.address == address:
                return buddy
        return None
    
    def getBuddyFromRandom(self, random):
        for buddy in self.list:
            if buddy.random1 == random:
                return buddy
        return None
    
    def setStatus(self, status):
        self.own_status = status
        for buddy in self.list:
            buddy.sendStatus()
    
    def onErrorIn(self, connection):
        for buddy in self.list:
            if buddy.conn_in == connection:
                buddy.disconnect()
                break
    
    def onErrorOut(self, connection):
        connection.buddy.disconnect()

    def onConnected(self, connection):
        connection.buddy.status = STATUS_HANDSHAKE

    def onChatMessage(self, buddy, message):
        self.guiChatCallback(buddy, message)
        

class Receiver(threading.Thread):
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.conn = conn
        self.socket = conn.socket
        self.running = True
        self.start()

    def run(self):
        readbuffer = ""
        while self.running:
            try:
                recv = self.socket.recv(1024)
                if recv != "":
                    readbuffer = readbuffer + recv
                    temp = readbuffer.split("\n")
                    readbuffer = temp.pop()
                
                    for line in temp:
                        line = line.rstrip()
                        if self.running:
                            message = ProtocolMsgFromLine(self.conn, line)
                            message.execute()
                else:
                    self.running = False
                    self.conn.onReceiverError()     
            
            except socket.timeout:
                pass
                           
            except:
                import traceback
                traceback.print_exc()
    
        
class InConnection:
    def __init__(self, socket, buddy_list):
        self.buddy = None
        self.bl = buddy_list
        self.socket = socket
        self.receiver = Receiver(self)
    
    def send(self, text):
        self.socket.sendall(text)
        
    def onReceiverError(self):
        self.bl.onErrorIn(self)
    
    def close(self):
        try:
            self.socket.close()
        except:
            pass
    

class OutConnection(threading.Thread):
    def __init__(self, address, buddy_list, buddy):
        threading.Thread.__init__(self)
        self.bl = buddy_list
        self.buddy = buddy
        self.address = address
        self.send_buffer = []
        self.start()
        
    def run(self):
        self.running = True
        try:
            self.socket = socks.socksocket()
            self.socket.settimeout(25)
            self.socket.setproxy(socks.PROXY_TYPE_SOCKS4, 
                               TOR_SERVER, 
                               TOR_SERVER_SOCKS_PORT)
            self.socket.connect((self.address, TORCHAT_PORT))
            self.bl.onConnected(self)
            self.receiver = Receiver(self)
            while self.running:
                if len(self.send_buffer) > 0:
                    text = self.send_buffer.pop(0)
                    self.socket.send(text)
                time.sleep(0.05)
                
        except:
            self.bl.onErrorOut(self)
            self.close()
            
    def send(self, text):
        self.send_buffer.append(text)
        
    def onReceiverError(self):
        self.bl.onErrorOut(self)
        self.close()
    
    def close(self):
        self.running = False
        try:
            self.socket.close()
        except:
            pass
        

class FileSender(threading.Thread):
    def __init__(self, buddy, filename, gui_callback):
        threading.Thread.__init__(self)
        self.buddy = buddy
        self.filename = filename
        self.filename_short = os.path.basename(self.filename)
        self.gui_callback = gui_callback
        self.id = random.getrandbits(32)
        self.buddy.bl.file_sender[self.buddy.address, self.id] = self
        self.start()
        
    def run(self):
        try:
            file_handle = open(self.filename)
            file_handle.seek(0, os.SEEK_END)
            filesize = file_handle.tell()
            self.gui_callback(filesize, 0)
            BLOCK_SIZE = 4096
            self.buddy.conn_in.send("filename %i %i %i %s\n" 
                % (self.id, filesize, BLOCK_SIZE, self.filename_short))
            blocks = int(filesize / BLOCK_SIZE) + 1
            for i in range(blocks):
                start = i * BLOCK_SIZE
                remaining = filesize - start
                if remaining > BLOCK_SIZE:
                    size = BLOCK_SIZE
                else:
                    size = remaining
                file_handle.seek(start)
                data = file_handle.read(size)
                send_line = "filedata %i %i %s\n" % (self.id, start, escape(data))
                
                self.buddy.conn_in.send(send_line)
                self.gui_callback(filesize, start + size)
                
        except:
            #FIXME: call gui and tell it about error
            print "error sending file %s" % self.filename
            

class FileReceiver:
    def __init__(self, buddy, filename, block_size):
        self.buddy = buddy
        self.filename = filename
        self.block_size = block_size
        
    def data(self, start, text):
        block = unescape(text)
        print "r %s %s %s" % (self.filename, start, len(block))
        
class Listener(threading.Thread):
    def __init__(self, buddy_list):
        threading.Thread.__init__(self)
        self.buddy_list = buddy_list
        self.conns = []
        self.start()

    def run(self):
        self.running = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((LISTEN_INTERFACE, LISTEN_PORT))
        self.socket.listen(1)
        try:
            while self.running:
                try:
                    conn, address = self.socket.accept()
                    self.conns.append(InConnection(conn, self.buddy_list))
                except:
                    self.running = False
                    
        except TypeError:
            pass

    def close(self):
        self.running = False
        try:
            self.socket.close()
        except:
            pass


def startPortableTor():
    global OWN_HOSTNAME
    global TOR_SERVER_SOCKS_PORT
    global TOR_SERVER_CONTROL_PORT
    global tor_in, tor_out
    old_dir = os.getcwd()
    try:
        os.chdir("tor")
        # completely remove all cache files from the previous run
        for root, dirs, files in os.walk("tor_data", topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        
        # now start tor with the supplied config file
        subprocess.Popen("tor -f torrc.txt".split(), creationflags=0x08000000)
        
        # we now assume the existence of our hostname file
        # it WILL be created after the first start
        # if not, something must be totally wrong.
        cnt = 0
        while cnt < 20:
            try:
                f = open("hidden_service\\hostname", "r")
                OWN_HOSTNAME = f.read().rstrip()[:-6]
                f.close()
                break
            except:
                # we wait 20 seconds for the file to appear
                time.sleep(1)
                cnt += 1

        #in portable mode we run Tor on some non-standard ports:
        TOR_SERVER_SOCKS_PORT = 11109
        TOR_SERVER_CONTROL_PORT = 11119
        os.chdir(old_dir)
    except:
        os.chdir(old_dir)
        