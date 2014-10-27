#!/usr/bin/python3

__author__ = 'JvO'
#Python Raspberry Pi Domotica
#Jeroen van Oorschot 2013
#Server side script to receive, apply and send changed settings. Uses sockets



from time import sleep

import subprocess
import json

import hashlib
import base64
#import sys
#import wiringpi2
import GFunc
import IOFunc
import PyDatabase  # for database
#for sockets and connections:
import socketserver
import threading
import argparse

#Initialize all used ports and the display.
IOF = IOFunc.IOFunc()


#import sys
#print(sys.path)

sleep(0.5)

IOF.displayWrite("Raspberry PI JvODomotica initing")
print("Starting in 5 seconds...")
sleep(5)

connection = []
#connectedClients= []
#bannedips = []
#MAXCHARS = 124
allowedIPs = ['101','102','103']
allowedComs = ["poweroff", "reboot"]
#####
#some constants
writeUpdateTime = 3   # every x seconds the database is checked for updates

#open the db functions and get the database login values
GF = GFunc.GFunc()




######main update function
#Apply a changed setting
def applySetting(name, value, sendTo): #sender='all': send to everyone; sender='none': send to no-one; sender=self: all but sender
    #GF.log("applysetting: "+name+':'+str(value)+' send to: '+str(sendTo),"D")
    tp = settings[name][0]  # row[2]  # type

    #write value in the settings dict
    if type(name) == str and value is not None and name != '':
        #value = str(value)  # value
        #settings: {key : [type, value, extra] }
        #update settings dictionary
        oldval = settings[name][1]
        try:
            settings[name][1] = value
        except:
            # setting not found, so settings is not complete or arguments not correct, assuming first. Re-init and restart now
            GF.log('name of setting: ' + str(name) + ' not found', 'E')
            return False
    else:
        GF.log('invalid arguments: [ name: ' + str(name) + ' ; value: ' + str(value) + ' ] supplied to applysetting()', 'E')
        return False

    # read arguments

    xt = settings[name][2]  # str(row[3])  # extra info, pin nr
    #value = str(value)
    GF.log('applySetting setting "'+name+'" to "' +str(value)+'"','N')

    #set the setting

    #execute a command
    if tp == "button":
        if sendTo != 'none': #don't do this on the init (to prevent reboot loop) Only if it comes from a user
            if name == "reinit":
                initDomo()
            else:
                command(name)
    # true-false switch for a port, set an output pin (xt) to the given value
    elif tp == "tf":
        #an output pin
        if xt is not None and xt.isdigit():
            try:
                pn = int(xt)  # pin
                #value should be 'true' or 'false' for a tf, but 0 or 1 for setOutput
                if value:
                    vl = 1
                else:
                    vl = 0
                IOF.setOutput(pn, vl)
            except:
                GF.log("Error, not possible to set " + str(pn) + " to " + str(value),'E')
        elif name == "skipAds" and value == True and settings["radiostation"] != "538nonstop40":
            applySetting("radiostationTemp",settings["radiostation"][1],'all')
    #drop down list items
    elif tp == "list":
        listItemValue = settings[value][1]  # get value of selected item in list. Value of list is the name of the selected item
        if name == "radiostation":  # radio station changed
            applySetting('geluidbron', 'Raspberry','all')  # Set amplifier input to radio
            playRadio(listItemValue)
        elif name == "geluidbron":  # sound source changed
            switchSound(listItemValue)  # choose sound source and play that source
            IOF.displayWrite("src= " + str(value))
            if oldval == "Raspberry" and value != "Raspberry":#disable radio
                smoothVolume(0)
                pauseRadio()  # stop music playing
                setVolume(settings['volume'][1])
            elif oldval == "bluetooth":
                stopBluetooth()
            #set new:
            if value == "Raspberry":
                #raspberry sound source chosen
                setVolume(0)
                resumeRadio()
                smoothVolume(settings['volume'][1])
            elif value == "bluetooth":
                GF.log("bluetooth starting.....",'D')
                startBluetooth()
    elif tp == "slider":      # slider input
        if name == "volume":    # change volume
            smoothVolume(value)

    #update the change to others
    try:
        data = 'S'+json.dumps({name : ( tp, value) })  # { name : [ type, value] }
        if sendTo == 'all':
            sendRound(data, False)
        elif sendTo != 'none':
            sendRound(data, sendTo)
    except:
        GF.log("Error in sending the setting round to others" ,'E')

#def setSetting(name, value, sender=False):


##write new values to database
def writeUpdates():
    radioText = getRadioText()
    #GF.log("radiotext: " + radioText,'N')
    if radioText != settings['radioText'][1]:
        applySetting('radioText', radioText, 'all')  # send radio update to everyone
        IOF.displayWrite(radioText)
    #GF.update('radioText', radioText)


def command(com):
    if(com in allowedComs):
        GF.log("Executing command: " + str(com), 'N')
        try:
            subprocess.call(["sudo", com])
        except:
            GF.log("Unable to execute command", 'E')
    else:
        GF.log("Command not allowed", 'N')
#####Radio Functions



#####Sound Functions
#switch audio inputs
def switchSound(channel):
    GF.log("change soundinput to " + str(channel), 'S')
    #switch the amplifier input to channel
    IOF.setSoundInput(int(channel)) #this also sets amplifier off if needed

##radio functions
#set radio volume
def setVolume(volume):
    #change value
    GF.log("change volume to " + str(volume), 'S')
    subprocess.call(["mpc",  "volume", str(volume)])

#change the volume in a few steps for smooth transition
def smoothVolume(reachVolume):
    reachVolume = int(reachVolume) #no longer necessary
    try:
        volume = int(settings['volume'][1]) #no longer necessary
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
    if stream[-4:] == '.m3u': #playlist
        subprocess.call(["mpc", "load", stream])
    subprocess.call(["mpc", "add", stream])
    #play
    resumeRadio()


#resume a paused radio
def resumeRadio():
    GF.log("mpc resumed", 'S')
    #play list
    subprocess.call(["mpc", "play"])
    sleep(0.1)
    radioText = getRadioText()
    applySetting('radioText', radioText,'all')  # send radio update to everyone


#pause the radio
def pauseRadio():
    GF.log("mpc paused", 'S')
    #pause radio
    subprocess.call(["mpc", "stop"])


#Get radio text, firs line of mpc output, get text from radio, not supported by all stations
def getRadioText():
    try:
        txt = str(subprocess.check_output("mpc", universal_newlines=True, stderr=subprocess.STDOUT))
        if len(txt) > 90:   #if the radio is playing
            return str(txt.split("\n")[0])
        else:
            return 'Radio tekst is niet beschikbaar'
    except:
        return "MPC is niet beschibaar"

def startBluetooth():
    try:
        temp = str(subprocess.check_output(["sudo", "pactl", "load-module", "module-loopback", "source=bluez_source.C8_D1_0B_E0_1D_B2", "sink=0"], universal_newlines=True, stderr=subprocess.STDOUT)) #hardcoded on my phoneaddress
        GF.log(temp, "D")
        settings["bluetooth"][2] = temp
        GF.log("Bluetooth started no: " + str(settings["bluetooth"][2]),'N')
    except:
        GF.log("bt failed","E")
        applySetting("geluidbron","versterkerUit",'all')

def stopBluetooth():
    GF.log("killing bluetooth " +str(settings["bluetooth"][2]),"N")
    try:
        subprocess.check_output(["sudo", "pactl", "unload-module", str(settings["bluetooth"][2])], universal_newlines=True, stderr=subprocess.STDOUT)
    except:
        GF.log("Bluetooth kapot :<","E")
############################### Data requests for clients
def getDataPoints(log,start,end):
    qryEnd = ''
    if start <= 1389123003:
        GF.log('invalid start time for getDataPoints','E')

    if end != None and end != '' and end != False and end >= 1389123003:
        qryEnd = ' and UNIX_TIMESTAMP(timestamp)<='.str(end);

    qry = 'Select UNIX_TIMESTAMP(timestamp) as ts, value from log_'+log+' where UNIX_TIMESTAMP(timestamp)>='+str(start) + qryEnd

    data = '['
    db = PyDatabase.PyDatabase(host=GF.DBLogin["host"], user=GF.DBLogin["user"], passwd=GF.DBLogin["passwd"], db=GF.DBLogin["db"])
    result = db.Execute(qry,True)
    if result is not None:
        for row in result:
            data += '[' + str(row[0]) + ',' + str(row[1]) + '],'

        data = data[:-1] + ']'
        GF.log(data,'D')
        return data
    return False

##########################################some inits
writeUpdateCount = 0
settings = {}

#All functions for control

#Init the program. If something went wrong, this will run again to restart
def initDomo():
    GF.log('Starting init','N')
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
            #row[1]#type
            #row[2]#value
            #row[3]#extra
            GF.log(row, 'N')
            #if row[2] is not None:
            #    if (row[2][0] == '[' or row[2][0] == '{'):
            #        r2 = json.loads(str(row[2]))
            #    else:
            #        r2 = json.loads(str(row[2].replace('"',"")))
            #else:
            #    r2 = row[2]
            try:
                if row[2] is None:
                    r2 = None
                else:
                    try:
                        r2 = json.loads((row[2].strip('"')))
                    except:
                        r2 = json.loads(row[2])
            except:
                GF.log(str(row[2])+" could not be decoded",'E')

            settings[row[0]] = [row[1], r2, row[3]] #list(row[1:4])  # add setting to dictionary

    GF.log('dict: ' + str(settings), 'D')
    #apply loaded settings for init
    for key, value in settings.items():
        applySetting(str(key), value[1], 'none')  # apply setting, sending key, value. Dont send to clients

    GF.log('Init complete, starting now!','N')


initDomo()
###############################  Socket server stuff
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
                self.websocket = 'web'
            except:
                GF.log("Incorrect Websocket Upgrade Request from " + str(addr) , 'E')
                return
        if self.websocket == 'web':
            data = GF.parse_frame(self.request)
        loginData = ""
        try:
            loginData = json.loads(str(data, "utf-8"))
        except:
            self.sendClient("E: wrong format login package")
            GF.log("ERROR: client from "+str(addr)+" sent wrong loginrequest: " + str(loginData))
            return
        #login procedure
        username = str(loginData["username"])
        password = str(loginData["password"])
        GF.log('User: ' + username + ' trying to login from: ' + str(addr) ,'N')

        # local user
        if addr[0:9] == '192.168.1':
            #phone, laptop, or ethernet
            if addr[10:13] in allowedIPs:
                user = [username, 2, 'Lokale gebruiker', None, addr, self]
                GF.log('Local user accepted', "N")
                self.sendClient("A:local user")
            #minute user, self
            elif addr[0:13] == '192.168.1.104':
                #print('minute logging in, switching to websocket protocol')
                user = [username, 2, 'rpi user', None, addr, self]
                self.websocket = 'python'   # switch to websockets here for minute.py
                self.sendClient("A rpi user")
                self.sendClient(json.dumps(settings)) #send the values to minute.py
            #local guest
            else:
                user = ['localguest', 1, 'Lokale gast', None, addr, self]
                GF.log('Local guest user accepted', "N")
                self.sendClient("A Local guest user")
        elif username != '' and password != '':  # remote user
            #check user validity here via database
            db = PyDatabase.PyDatabase(host=GF.DBLogin["host"], user=GF.DBLogin["user"], passwd=GF.DBLogin["passwd"], db=GF.DBLogin["db"])
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
                self.sendClient("A Remote user")
                GF.log('OK, valid login as remote user',"N")
            else:
                GF.log('This is an invalid user, stopping now', 'N')
                self.sendClient("E invalid user or password send. Stopping connection now")
                return False
        else:  # not valid user
            GF.log('This is an empty request, stopping now', 'N')
            self.sendClient("E username and password empty. Stopping connection now")
            return False

        connection.append(user)
        #connectedClients.append(user)


        while True:
            try:
                data = ""
                if self.websocket == 'web':
                    data = GF.parse_frame(self.request)
                elif self.websocket == 'python':
                    data = GF.parse_frame(self.request, False)  # request from a local python script
                self.data = str(data, "utf-8")
                if self.data == "":  # skip if empty data
                    continue
                GF.log("user "+str(user[0])+" send message: "+self.data, 'N')

                #decode data
                type = self.data[0:1]
                data = json.loads(self.data[1:])  # all data is in json format
                if user[1] >= 0:  # if user has enough rights
                    if type == 'M':  # message
                        GF.log("client "+ str(user[0]) +" send a message: " + str(data), 'N')

                    elif type == "R":  # resend all values
                        GF.log("client "+ str(user[0]) +" requested value update", 'N')
                        self.sendClient('S'+json.dumps(settings))

                    elif type == "D" and user[1] >= 1: #download graph
                        print(data)
                        d = data.get('d')
                        s = data.get('s')
                        e = data.get('e')
                        try:
                            points = getDataPoints(d,s,e)
                        except:
                            print('points ERROR')
                        print(points)
                        self.sendClient('D:'+data.get('d')+'P:'+points)

                    elif type == 'S' and user[1] == 2: #setting
                        #3try: debug
                        for key, value in data.items():
                            GF.log(key + ' val: '+str(value), "D")
                            if value is not None and key != '':
                                #self.sendClient("OK")  # message is received, so confirm
                                #print('now going to apply:',value,key)
                                applySetting(key, value, self)  # apply setting and put in dictionary
                            else:
                                self.sendClient("W Empty setting")
                                GF.log("empty message received",'E')
                      #  except:  # wrong assumption
                     #       GF.log('Received message: ' + self.data + '  not a command or invalid name or type','E')
                     #       self.sendClient("W Not a command or invalid name or type")

                    elif type == 'P': #load a page
                        src = '/var/www/'+ data.get('p') + '.txt'
                        if data.get('c')=='True':
                            self.sendClient("W not yet possible to refresh cache via websocket")
                            GF.log("W not yet possible to refresh cache via websocket",'E')

                        self.sendClient('P'+open(src ,'r').read())

                    else:
                        GF.log('User '+user[0]+' send invalid message','E')
                        self.sendClient("W Invalid message send")
                else:
                    GF.log('User '+user[0]+' tried to send but has not enough rights','U')
                    self.sendClient("W Not enough rights for this action")
            except:
                GF.log("INFO: client "+username+" from "+addr+" disconnected",'N')
                try:
                    connection.remove(user)
                    #connectedClients.remove(user)
                except:
                    GF.log("Failed to remove user: "+user[0]+" from connected users list", 'E')
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
        #print('sending: '+message)
        if self.websocket:
            self.request.sendall(GF.create_frame(message))
        else:
            self.request.sendall(bytes(message, "utf-8"))


def sendRound(data, sender=False):
    for u in connection:
        userClass = u[5]
        if userClass != sender and u[0] != 'minute':  # don't send back to sender
            try:
                GF.log("sendround, sending change: " + data + 'to ' + u[2], "N")
                userClass.sendClient(data)
            except:
                GF.log("ERROR: failed to send message to user: "+u[2])
    else:
        return False

def disconnect():
    GF.log("STOP, now closing all sockets", "N")
    for u in connection:
        userClass = u[5]
        try:
            if userClass.websocket:
                userClass.request.sendall(userClass.create_frame("", 8))
            else:
                userClass.request.shutdown(1)
                userClass.request.close()
        except:
            GF.log("ERROR: failed to close socket for user: "+u[0])


# main init function for tcp server
ThreadedServerHandler.SendRound = sendRound
#ThreadedServerHandler.IsAdmin = IsAdmin
#ThreadedServerHandler.FindUser = FindUser
#ThreadedServerHandler.hash_password = hash_password
#ThreadedServerHandler.check_password = check_password
#send data to all connected users, except optionally given sender

if __name__ == "__main__":
    GF.log("Jeroen van Oorschot, domotica-webradio","N")
    parser = argparse.ArgumentParser(description='Jeroen van Oorschot, Domotica system and webradio')
    #parser.add_argument('--ip', nargs='?', const=1, type=str, default="localhost", help='specify the ip adress wich the server will bind to, defaults to localhost')
    parser.add_argument('--port', nargs='?', const=1, type=int, default=600, help='specify the port number, defaults to 600')

    #PORT = 600 #
    PORT = parser.parse_args().port
    HOST = '192.168.1.104'

    GF.log("host: " + str(HOST) + ":" + str(PORT), "N")
    GF.log("starting server ...","N")
    sleep(1)

    server = ThreadedTCPServer((HOST, PORT), ThreadedServerHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    GF.log("Server loop running, waiting for connections ...",'N')

    while True:
        sleep(writeUpdateTime)
        try:
            writeUpdates()
        except:
            print("Error in writeUpdates")






        """command = input()
        try:
            if command == "help":
                print("Using port 600"
                    "\navailable commands:\n"
                    "\nhelp : this help message"
                    "\nclose : close sockets"
    #                "\nstop : close sockets and stop server"
                    "\nusers : show users"
                    "\ncontrols : show all controls"
                )
            elif command == "close":
                disconnect()
#            elif command == "stop":
 #               disconnect()
#                server_thread.shutdown()
 #               exit()
            elif command == "controls":
                print(str(settings))
        except:
            GF.log("Exception in command, now closing all sockets", "E")
            disconnect()
"""
