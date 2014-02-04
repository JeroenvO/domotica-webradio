#!/usr/bin/python


#Python Raspberry Pi Domotica
#Jeroen van Oorschot 2013
#Server side script to read the mysql db and execute all commands and save logs
#v 0.9
#changelog
#* logging moved to logging.py
#* alarm moved to alarm.py
#* using subprocess ipv os


from time import sleep
import RPi.GPIO as GPIO
import subprocess
import json
import argparse

import hashlib
import base64

import GFunc

import PyDatabase  # for database

#for sockets and connections:
import socketserver
import threading
import struct
#users = []
connection = []
connectedClients= []
#bannedips = []
MAXCHARS = 124
allowedIPs = ['100','101','102','103']

#####
#some constants
checkUpdateTime = 0.1   # every x seconds the database is checked for updates
writeUpdateFactor = 40  # every x updates of checkUpdateTime updates are written

#open the db functions and get the database login values
GF = GFunc.GFunc()



######main update function
#Apply a changed setting
def applySetting(name, value):
        # read arguments
    if type(name) == str and value is not None and name != '':
        nm = name
        vl = str(value)  # value
        #settings: {key : [type, value, extra] }
        #update settings dictionary
        try:
            tp = settings[nm][0]  # row[2]  # type
            xt = settings[nm][2]  # str(row[3])  # extra info, pin nr
            settings[nm][1] = vl
        except:
            # setting not found, so settings is not complete or arguments not correct, assuming first. Re-init and restart now
            GF.log('name of setting: ' + str(nm) + ' not found', 'E')
            return False
        GF.log('applySetting setting "'+name+'" to "' +value+'"','N')
        # toggling button
        #if tp == "toggle":
            #do something
        # true-false switch for a port
        if tp == "tf" and xt is not None and xt.isdigit():
            try:
                pn = int(xt)  # pin
                #value should be 'True' or 'False'
                if vl == "true":
                    vl = True
                else:
                    vl = False
                setOutput(pn, vl)
            except:
                GF.log("Error, not possible to set " + str(pn) + " to " + str(vl),'E')
        #drop down list items
        elif tp == "list":
            listItemValue = settings[vl][1]  # get value of selected item in list. Value of list is the name of the selected item
            if nm == "radiostation":  # radio station changed
                GF.update('geluidbron', 'Raspberry')  # Set amplifier input to radio
                playRadio(listItemValue)
            elif nm == "geluidbron":  # sound source changed
                switchSound(listItemValue)  # choose sound source and play that source
                if vl == "Raspberry":
                    #raspberry sound source chosen
                    setVolume(0)
                    resumeRadio()
                    smoothVolume(settings['volume'][1])
                else:
                    smoothVolume(0)
                    pauseRadio()  # stop music playing
                    setVolume(settings['volume'][1])
        elif tp == "slider":      # slider input
            if nm == "volume":    # change volume
                smoothVolume(vl)
    else:
        GF.log('invalid arguments: [ name: ' + str(name) + ' ; value: ' + str(value) + ' ] supplied to applysetting()', 'E')



##write new values to database
def writeUpdates():
    radioText = getRadioText()
    GF.log("radiotext: " + radioText,'N')
    #GF.update('radioText', radioText)



#####GPIO Functions
#set output
def setOutput(pin, value):
    GF.log("tf switch " + pin + " to " + value, 'S')
    #set gpio


#####Sound Functions
#switch audio inputs
def switchSound(channel):
    GF.log("change soundinput to " + channel, 'S')
    #switch the amplifier input to channel
    #some gpio actions


##radio functions
#set radio volume
def setVolume(volume):
    #change value
    GF.log("change volume to " + str(volume), 'S')
    subprocess.call(["mpc",  "volume", str(volume)])


#change the volume in a few steps for smooth transition
def smoothVolume(reachVolume):
    reachVolume = int(reachVolume)
    try:
        volume = int(settings['volume'][1])
    except:
        GF.log("Current volume could not be read, using 0",'N')
        volume = 0
    while True:
        try:
            if reachVolume > (volume+10):  # increase volume
                volume += 10
            elif reachVolume < (volume-10):  # decrease volume
                volume -= 10
            else:  # small volume difference
                volume = reachVolume
                setVolume(str(volume))
                break
            setVolume(str(volume))
            sleep(0.1)
        except:
            GF.log("Failed to change volume",'E')


#stop radio
def stopRadio():
    #clear mpc to stop radio playing
    GF.log("mpc stopped",'S')
    subprocess.call(["mpc", "clear"])


#play radio from stream
def playRadio(stream):
    GF.log("radio started: " + stream, 'S')
    #stop and clear current stream
    subprocess.call(["mpc", "clear"])
    #make playlist
    subprocess.call(["mpc", "add", stream])
    #play
    resumeRadio()


#resume a paused radio
def resumeRadio():
    GF.log("mpc resumed", 'S')
    #play list
    subprocess.call(["mpc", "play"])


#pause the radio
def pauseRadio():
    GF.log("mpc paused", 'S')
    #pause radio
    subprocess.call(["mpc", "pause"])


#Get radio text, firs line of mpc output, get text from radio, not supported by all stations
def getRadioText():
    txt = subprocess.check_output("mpc").split('\n')[0]
    a = ['volume:','repeat:','random:','single:','consume:']
    if all(x in txt for x in a):
        #if the radio is not playing
        return 'Radio tekst is niet beschikbaar'
    #otherwise return the radio text
    return txt

#radio functions


########GPIO

#initialize all ports
def setPorts():
    GPIO.setmode(GPIO.BCM)
    inputs = [4]
    outputs = [5, 8, 28]  # get these from db in the future
    for input in inputs:
        GPIO.setup(input, GPIO.IN)

    for output in outputs:
        GPIO.setup(output, GPIO.OUT)

######MAIN
#check instance, quit if already running
# """
# file_handle = None
# def file_is_locked(file_path):
#     global file_handle
#     file_handle= open(file_path, 'w')
#     try:
#         fcntl.lockf(file_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
#         return False
#     except IOError:
#         return True
#
# file_path = '/var/lock/domotica'
#
# if file_is_locked(file_path):
#     print 'another instance is running exiting now'
#     sys.exit(0)
# else:
#     print 'no other instance is running'
#     for i in range(5):
#         time.sleep(1)
#         print i + 1
# 		"""
##INIT
#setPorts()

#Init the program. If something went wrong, this will run again to restart
def initDomo():
    GF.log('Starting init','N')
    #clear mpc audio for a clean start
    #subprocess.call(["mpc", "clear"])
    #make dictionary from database
    db = PyDatabase.PyDatabase(host=GF.DBLogin["host"], user=GF.DBLogin["user"], passwd=GF.DBLogin["passwd"], db=GF.DBLogin["db"])
    #  make query
    columns = ['name', 'type', 'value', 'extra']
    condition = {'settings.type' : 'IS NOT NULL'}
    results = None
    # make settings dict, to use in stead of database
    global settings
    settings = {}
    # fill settings from the database
    results = db.Select(table='settings', columns=columns, condition_and=condition)
    if results is False:
        GF.log("could not execute query: " + db.query,'E')

    if results is not None:
        for row in results:
            settings[row[0]] = list(row[1:4])  # add setting to dictionary

    GF.log('dict: ' + str(settings), 'D')
    #apply loaded settings for init
    for key, value in settings.items():
        applySetting(key, value[1])  # apply setting, sending key, value

    GF.log('Init complete, starting now!','N')

#some inits
writeUpdateCount = 0
settings = {}
initDomo()

#while True:
 #   try:
   #     writeUpdateCount += 1
        #check only updated settings
        #try:
            #checkUpdates(False)
        #except:
            #GF.log("error in checkupdates, trying again", 'E')

        #wait for next round
    #    sleep(checkUpdateTime)

    #    if writeUpdateCount == writeUpdateFactor:
   #         try:
  #              writeUpdates()
   #             writeUpdateCount = 0
   #             GF.log("updates written","N")
   #         except:
    #            GF.log("error in write, trying again", 'E')
   #             sleep(5)

  #  except:
  #      GF.log("error in main loop, restarting in 10 secs", 'E')
   #     sleep(10)


############################### Socketservers tuff
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class ThreadedServerHandler(socketserver.BaseRequestHandler):

#    def remove_html_tags(self, data):
#        p = re.compile(r'<.*?>')
#        return p.sub('', data)

    def handle(self): #the handler for the server, this handles the receiving and distributing of messages
        self.websocket = False
        data = self.request.recv(1024)
        addr = self.request.getpeername()[0]
        if "upgrade: websocket" in str(data, "utf-8").lower():
            try:
                self.HandShake(str(data, "utf-8"))
                self.websocket = True
            except:
                GF.log("Incorrect Websocket Upgrade Request from " + str(addr) , 'E')
                return
        if self.websocket:
            data = self.parse_frame()
        loginData = ""
        try:
            loginData = json.loads(str(data, "utf-8"))
        except:
            self.sendClient("ERROR: wrong format login package")
            GF.log("ERROR: client from "+str(addr)+" sent wrong loginrequest: " + str(loginData))
            return

        username = str(loginData["username"])
        password = str(loginData["password"])
        GF.log('User: ' + username + ' trying to login from: ' + str(addr) ,'N')
        #GF.log('addr0-9: ' +addr[0:9], "D" )
        validUser = False
        if addr[0:9] == '192.168.1':
            if addr[10:13] in allowedIPs:  # local user
                user = ['local', 2, 'Lokale gebruiker', None, addr, self]
                validUser = True
                GF.log('Local user accepted', "N")
                self.sendClient("OK, valid login as local user")
            else:
                user = ['localguest', 1, 'Lokale gast', None, addr, self]
                validUser = True
                GF.log('Local guest user accepted', "N")
                self.sendClient("OK, valid login as local guest user")
        elif username != '' and password != '':  # remote user
            #check user validity here via database
            db = PyDatabase.PyDatabase(host=GF.DBLogin["host"], user=GF.DBLogin["user"], passwd=GF.DBLogin["passwd"], db=GF.DBLogin["db"])
            # make query
            # qry = "select level, fullname, value from RPi.users WHERE usernm='"+username+"' AND pwdhash='"+password+"'"
            condition_and = {
                'usernm' : username,
                'pwdhash' : password
            }
            results = db.Select(table='users', columns=['level', 'fullname', 'value'], condition_and=condition_and)
            #GF.log("results: "+str(results),'D')
            if results is False:
                GF.log("failed to execute query: " + db.query, 'E')
                return False
            if results is not None:  # The user exists. name, level, fullname, value
                user = [username, results[0][0], results[0][1], results[0][2], addr, self]
                validUser = True
                self.sendClient("OK, valid login as remote user")
                GF.log('OK, valid login as remote user',"N")
            else:
                GF.log('This is an invalid user, stopping now', 'N')
                self.sendClient("ERROR invalid user or password send. Stopping connection now")
                return False
        else:  # not valid user
            GF.log('This is an empty request, stopping now', 'N')
            self.sendClient("ERROR username and password empty. Stopping connection now")
            return False

        connection.append(user)
        connectedClients.append(user)

        # send all settings values to the connected user:
        self.sendClient(json.dumps(settings))

        while True:
            try:
                data = ""
                if self.websocket:
                    data = self.parse_frame()
                else:
                    data = self.request.recv(1024)
                self.data = str(data, "utf-8")
                if self.data == "":  # skip if empty data
                    continue
                GF.log("user "+str(user[2])+" send message: "+self.data, 'N')
                if self.data == "testresponse":
                    self.sendClient("RESPONSE: Test complete!")
                    GF.log("client "+ str(user[2]) +" requested test response", 'N')
                    continue
                global MAXCHARS
                if len(self.data) > MAXCHARS:
                    self.sendClient("WARNING: message is too long")
                    GF.log("client " + str(user[2]) + " tried sending a too long message")
                else: # normal data received. Not a command
                    #self.sendClient("OK")  # send receive confirmation
                    if user[1] == 2:  # if user has enough rights
                        try:  # assuming json
                            data = json.loads(self.data)
                            for key, value in data.items():
                                #GF.log(key + ' val: '+value, "D")
                                if value is not None and key != '':
                                    applySetting(key, value)  # apply setting and put in dictionary
                                    try:
                                        sendValueRound(key,settings[key][0],value,self)
                                    except:
                                        GF.log("Error in sending the setting round to others" ,'E')
                                    self.sendClient("OK")
                                else:
                                    self.sendClient("WARNING: empty request")
                                    GF.log("empty message received",'E')
                        except:  # wrong assumption
                            GF.log('Received message: ' + self.data + '  not a command or invalid name or type','E')
                            self.sendClient("WARNING: Not a command or invalid name or type")
                    else:
                        GF.log('User '+user[0]+' tried to send but has not enough rights','U')
                        self.sendClient("WARNING: Not enough rights for this action")

            except:
                GF.log("INFO: client "+username+" from "+addr+" disconnected",'N')
                try:
                    connection.remove(user)
                    connectedClients.remove(user)
                except:
                    GF.log("Failed to remove user: "+user[2]+" from connected users list", 'E')
                return


    def HandShake(self, request):
        specificationGUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        websocketkey = ""
        protocol = ""
        for line in request.split("\r\n"):
            if "Sec-WebSocket-Key:" in line:
                websocketkey = line.split(" ")[1]
            elif "Sec-WebSocket-Protocol" in line:
                protocol = line.split(":")[1].strip().split(",")[0].strip()
            elif "Origin" in line:
                self.origin = line.split(":")[0]

        # print("websocketkey: " + websocketkey + "\n")
        fullKey = hashlib.sha1(websocketkey.encode("utf-8") + specificationGUID.encode("utf-8")).digest()
        acceptKey = base64.b64encode(fullKey)
        # print("acceptKey: " + str(acceptKey, "utf-8") + "\n")
        if protocol != "":
            handshake = "HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Protocol: " + protocol + "\r\nSec-WebSocket-Accept: " + str(acceptKey, "utf-8") + "\r\n\r\n"
        else:
            handshake = "HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: " + str(acceptKey, "utf-8") + "\r\n\r\n"
        # print(handshake.strip("\n"))
        self.request.send(bytes(handshake, "utf-8"))

    def sendClient(self, message):
        if self.websocket:
            self.request.sendall(self.create_frame(message))
        else:
            self.request.sendall(bytes(message, "utf-8"))

#new code inserted to handle data larger than 125
        # Stolen from http://www.cs.rpi.edu/~goldsd/docs/spring2012-csci4220/websocket-py.txt
    def create_frame(self, data, Opcode=1):
        # first byte, always send an entire message as one frame (fin)
        b1 = 0x80  # '0b10000000'

        # type of data
        b1 += Opcode  # if Opcode=1, b1 = '0b10000001'

        # make data
        if type(data) == str:
            payload = data.encode("UTF8")
        elif type(data) == bytes:
            payload = data
        else:
            return 'ERROR, data type not supported'

        # make first byte
        message = struct.pack(">B", b1)  # chr makes a ascii char from the byte. Sending this is equal to sending the bits

        # b2 starts with zero, because server>client is never masked
        # make mask and payload-length
        length = len(payload)
        if length < 126:
            b2 = length
            message += struct.pack(">B",b2)
        elif length < (2 ** 16) - 1:
            b2 = 126
            message += struct.pack(">B",b2)
            message += struct.pack(">H", length)
        elif length < (2 ** 64) - 1:
            b2 = 127
            message += struct.pack(">B",b2)
            message += struct.pack(">Q", length)
        else:
            return "ERROR, too long message"

        # add the message to the header
        message += payload

        # Send to the client
        return message


  #receive data from client
    def parse_frame(self):
        s = self.request
        # read the first two bytes
        frame_head = s.recv(2)

        # very first bit indicates if this is the final fragment
        # print("final fragment: ", self.is_bit_set(frame_head[0], 7))

        # bits 4-7 are the opcode (0x01 -> text)
        # print("opcode: ", frame_head[0] & 0x0f)

        # mask bit, from client will ALWAYS be 1
        assert self.is_bit_set(frame_head[1], 7)

        # length of payload
        # 7 bits, or 7 bits + 16 bits, or 7 bits + 64 bits
        payload_length = frame_head[1] & 0x7F
        if payload_length == 126:
            raw = s.recv(2)
            payload_length = self.bytes_to_int(raw)
        elif payload_length == 127:
            raw = s.recv(8)
            payload_length = self.bytes_to_int(raw)
        # print('Payload is {} bytes'.format(payload_length))

        #masking key
        #All frames sent from the client to the server are masked by a
        #32-bit nounce value that is contained within the frame

        masking_key = s.recv(4)
        # print("mask: ", masking_key, self.bytes_to_int(masking_key))

        # finally get the payload data:
        masked_data_in = s.recv(payload_length)
        data = bytearray(payload_length)

        # The ith byte is the XOR of byte i of the data with
        # masking_key[i % 4]
        for i, b in enumerate(masked_data_in):
            data[i] = b ^ masking_key[i%4]
        return data

    def is_bit_set(self, int_type, offset):
        mask = 1 << offset
        return not 0 == (int_type & mask)

    def set_bit(self, int_type, offset):
        return int_type | (1 << offset)

    def bytes_to_int(self, data):
        # note big-endian is the standard network byte order
        return int.from_bytes(data, byteorder='big')


"""old code


    def create_frame(self, data):
        # pack bytes for sending to client
        frame_head = bytearray(2)  # 16 bits for header

        # set final fragment
        frame_head[0] = self.set_bit(frame_head[0], 7)

        # set opcode 1 = text
        frame_head[0] = self.set_bit(frame_head[0], 0)  # bits 4-7 opcode

        # frame_head[0] == 129 in decimal. 10000001 in bin

        print("head: " + str(bin(frame_head[0])))
        # payload length
        l = len(data)
        #if l < 126:
        frame_head[1] = len(data)  # bits 9-15 are data (payload) length
        #elif l >= 126 && l<=

        # add data
        frame = frame_head + data.encode('utf-8')
        # print("frame crafted for message " + data + ":")
        # print(list(hex(b) for b in frame))
        return frame


#def remove_html_tags(data):
#    p = re.compile(r'<.*?>')
#   return p.sub('', data)
"""

# send a value round to all users except the user who send the source message
def sendValueRound(name, type, value, sender):
    name = str(name)
    type = str(type)
    value = str(value)
    if value != '' and name != '' and type != '':
        data = json.dumps({name : ( type, value) })  # { name : [ type, value] }
        sendRound(data,sender)
        
#send data to all connected users, except optionally given sender
def sendRound(data,sender=False):
    for u in connection:
        if u[5] != sender:  # don't send back to sender
            userClass = u[5]
            try:
                GF.log("sendround, sending change: " + data + 'to ' + u[2], "N")
                if userClass.websocket:
                    userClass.request.sendall(userClass.create_frame(data))
                else:
                    userClass.request.sendall(bytes(data, "utf-8"))
            except:
                GF.log("ERROR: failed to send message to user: "+u[2])

    else:
        return False
def disconnect():
    GF.log("STOP, now closing all sockets", "N")
    for u in connection:
        Class = u[5]
        try:
            Class.request.sendall(Class.create_frame("stop",8))
            Class.request.close()
        except:
            GF.log("ERROR: failed to close socket for user: "+u[0])

#def hash_password(password):
#    # uuid is used to generate a random number
#    salt = uuid.uuid4().hex
#    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

def check_password(hashed_password, user_password):
    password, salt = hashed_password.split(':')
    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()

ThreadedServerHandler.SendRound = sendRound
#ThreadedServerHandler.IsAdmin = IsAdmin
#ThreadedServerHandler.FindUser = FindUser
#ThreadedServerHandler.hash_password = hash_password
#ThreadedServerHandler.check_password = check_password


# main init function for tcp server

if __name__ == "__main__":
    GF.log("Jeroen van Oorschot, domotica-webradio","N")
    parser = argparse.ArgumentParser(description='the server component of kolibri chat')
    #parser.add_argument('--ip', nargs='?', const=1, type=str, default="localhost", help='specify the ip adress wich the server will bind to, defaults to localhost')
    #parser.add_argument('--port', nargs='?', const=1, type=int, default=6000, help='specify the port number, defaults to 9999')

    PORT = 600 #parser.parse_args().port
    HOST = '192.168.1.104'

    GF.log("host: " + str(HOST) + ":" + str(PORT), "N")
    GF.log("starting server ...","N")
    sleep(1)
    server = ThreadedTCPServer((HOST, PORT), ThreadedServerHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    GF.log("Server loop running, waiting for connections ...",'N')

    print("Typ 'help' for available commands")
    while True:
        command = input()
        try:
            if command == "help":
                print("Using port 600"
                    "\navailable commands:\n"
                    "\thelp : this help message"
                    "\tstop : close sockets")
            elif command == "stop":
               disconnect()
        except:
            GF.log("Exception, now closing all sockets", "E")
            disconnect()
