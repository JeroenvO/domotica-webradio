#!/usr/bin/python3

__author__ = 'JvO'
# Python Raspberry Pi Domotica
#Jeroen van Oorschot 2013-2015
#Server side script to receive, apply and send changed settings. Uses sockets

from time import sleep
import subprocess  # to call various commands, for instance music
# for websockets
import json  # these websockets talk with JSON
import hashlib
import base64
# general libraries
import GFunc  # general functions like logging and websocket (de)coding
import IOFunc  # for general IO functions, like i2c, includes wiringpi
import PyDatabase  # for database, script made by williewonka to easy access databases from python
# for sockets and connections:
import socketserver
import threading
import argparse  # to supply a custom port for the sockets
import colorsys  # for colorconversion between hsl and rgb, used for leds

print("Raspberry PI Domotica JvO")


# global array to store all the connected clients
connection = []

# after 192.168.1. the last numbers of the IP of users that always have full access.
allowedIPs = ['101', '102', '103']

# commands which are allowed in the function to send OS-commands
allowedComs = ["poweroff", "reboot"]

#time between updates,
writeUpdateTime = 3  # every x seconds the radiotext is send to the clients and to the display

#settings-dictionary to cache the settings-database. Contains all settings as name, value, type and extra.
settings = {}

# Initialize all used ports and the display.
IOF = IOFunc.IOFunc()
# open the db functions and get the database login values
GF = GFunc.GFunc()
# give the system some time to boot
sleep(0.5)
# Write init message to the connected display
IOF.displayWrite("Raspberry PI JvODomotica initing")
# Wait 5s so MySQL has some extra time to boot when this script runs directly after boot.
GF.log("Starting in 5 seconds...", "N")
sleep(5)
GF.log("Starting!", "N")

##////////////////////////////////##
##||||main update function||||||||##
##\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\##

# Function to apply a changed setting.
# name= name of the setting
# value= value that the setting with 'name' should have
# sendTo= To who the changed setting is sended after it has changed.
#    sendTo='all': send to everyone; sendTo='none': send to no-one; sendTo=self: all but sender
def applySetting(name, value, sendTo):
    # GF.log('applySetting: setting "'+name+'" to "' +str(value)+'"','N')
    # write value in the settings dict
    if type(name) == str and value is not None and name != '':
        # value = str(value)  # fix for in case the supplied value is not in string format
        oldval = settings[name][1]  # store the old value, used to stop processes that were turned on before.
        try:
            settings[name][1] = value  # update settings dictionary
        except:  # setting not found
            GF.log('applySetting: name of setting: ' + str(name) + ' not found', 'E')
            return False
    else:  # invalid arguments
        GF.log('applySetting: invalid arguments: [ name: ' + str(name) + ' ; value: ' + str(value) + ' ] supplied', 'E')
        return False

    # just to prevent much typing later on
    tp = settings[name][0]  # row[2]  # type of the setting
    xt = settings[name][2]  # row[3]  # extra info belonging to the setting, for instance pin nr for IO

    # apply the changed setting, ordered by type.
    if tp == "button":  # a button, usually this is a command.
        if sendTo != 'none':  # don't apply commands on the init (init has sendTo='none' (to prevent reboot loop)
            command(name)

    elif tp == "tf":  # true-false switch, usually an IO pin, set an output pin (xt) to the given value
        if xt is not None and xt.isdigit():  # if the pin has a valid value
            try:
                pn = int(xt)  # make an integer from the pin nr
                # convert true/false to 1 or 0
                if value:
                    vl = 1
                else:
                    vl = 0
                IOF.setOutput(pn, vl)  # Apply the output setting
            except:
                GF.log("applySetting: not possible to set " + str(pn) + " to " + str(value), 'E')
        # the toggle to skip adds of radio. If true, store the radiostation name that has to resume after the add break.
        elif name == "skipAds" and value == True and settings["radiostation"] != "538nonstop40":
            applySetting("radiostationTemp", settings["radiostation"][1], 'all')

    # drop down list items
    elif tp == "list":
        # get the value of the selected item in the list,
        # the name of the selected element is stored as the value of the name of the list
        listItemValue = settings[value][1]

        if name == "radiostation":  # radio station changed
            applySetting('geluidbron', 'Raspberry', 'all')  # Set amplifier input to radio
            playRadio(listItemValue)
        elif name == "geluidbron":  # sound source changed
            switchSound(listItemValue)  # choose sound source and play that source
            IOF.displayWrite("src= " + str(value))  # show the chosen source on the display
            if oldval == "Raspberry" and value != "Raspberry":  # disable radio if the old value was radio
                smoothVolume(0)
                pauseRadio()  # stop music playing
                setVolume(settings['volume'][1])
            elif oldval == "bluetooth":  # stop bluetooth connection if bluetooth is no longer the selected option
                stopBluetooth()

            # apply the new settings
            if value == "Raspberry": # raspberry sound input chosen
                setVolume(0)
                resumeRadio()
                smoothVolume(settings['volume'][1])
            elif value == "bluetooth": # start the bluetooth connection
                startBluetooth()

    # slider input.
    elif tp == "slider":
        if name == "volume":  # change volume
            smoothVolume(value)
        if name == "llksunrise": # leds sunrise simulator. Color value dependent on slider
            sunrise(value)
        elif xt is not None and xt.isdigit(): # if the extra-field has a number, the slider is a pwm output controller
            #print('slider:'+str(xt)+'to:'+str(value))
            IOF.setPWM(int(xt), value / 100.0)

    # color input, colorwheel with hsl output. See jeroenvo -> html5-colorpicker
    elif tp == "color":
        setColor(value, 'hsl')

    # color input RGB, three sliders for r g and b
    elif tp == "colorRGB":
        setColor(value, 'rgb')

    # Send the changed setting to connected clients, so their settings-panel is also up-to-date
    try:
        data = 'S' + json.dumps({name: ( tp, value)})  # { name : [ type, value] }
        if sendTo == 'all':  # send to all connected clients
            sendRound(data, False)
        elif sendTo != 'none':
            sendRound(data, sendTo)  # send to all connected clients except for the 'sendTo'
    except:
        GF.log("applySetting: Unable to send setting to others", 'E')


##//////////////////////////////////////////##
##||||helper functions to apply settings||||##
##\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\##

# Apply a system command
def command(com):
    if com == "reinit":  # re-initialize the whole cached database stored in settings{}
        initDomo()
    elif com in allowedComs:  # only execute commands listed in allowedComs
        GF.log("Executing command: " + str(com), 'N')
        try:
            subprocess.call(["sudo", com])  # at this moment, all commands need sudo, so it is always used
        except:
            GF.log("Unable to execute command", 'E')
    else:
        GF.log("Command " + com + " is not allowed",'E')

# switch amplifier audio input to the given channel
def switchSound(channel):
    GF.log("change soundinput to " + str(channel), 'S')
    IOF.setSoundInput(int(channel))  # this function also sets amplifier off if needed

# set radio (mpc) volume
def setVolume(volume):
    GF.log("change volume to " + str(volume), 'S')
    subprocess.call(["mpc", "volume", str(volume)])

# change the volume in a few steps for smooth transition
# in the future this should become a parallel (threaded) function
def smoothVolume(reachVolume):
    reachVolume = int(reachVolume)  # make sure that volume is supplied as int
    try:
        volume = int(settings['volume'][1])  # the current volume
    except:  # current volume could not be read.
        GF.log("Current volume could not be read, using 0", 'N')
        volume = 0  # assume the current volume to be zero
    while True:  # loop until the reachVolume is reached
        try:
            if reachVolume > (volume + 10):  # increase volume
                volume += 10
            elif reachVolume < (volume - 10):  # decrease volume
                volume -= 10
            else:  # small volume difference
                volume = reachVolume
                setVolume(str(volume))
                break
            setVolume(str(volume))
            sleep(0.1)
        except:
            GF.log("Failed to change volume", 'E')

# stop the radio (mpc)
def stopRadio():
    subprocess.call(["mpc", "clear"])  # clear mpc to stop radio playing, and to delete the chosen list

# play radio from supplied stream stream
def playRadio(stream):
    GF.log("radio started: " + stream, 'S')
    subprocess.call(["mpc", "clear"])  # stop and clear (delete) current stream
    if stream[-4:] == '.m3u':  # if the stream is supplied as a playlist, load the playlist
        subprocess.call(["mpc", "load", stream])
    else:  # otherwise add the stream to the default list
        subprocess.call(["mpc", "add", stream])
    resumeRadio()  # play the radio

# resume a paused radio
def resumeRadio():
    subprocess.call(["mpc", "play"])  # this only works if there already is a stream, so not after a 'clear' command
    sleep(0.1)  # wait for the radiotext to become available
    radioText = getRadioText()  # directly update the radiotext, to prevent a lag of writeUpdateTime
    applySetting('radioText', radioText, 'all')  # force send radiotext update to everyone.

# pause the radio
def pauseRadio():
    GF.log("mpc paused", 'S')
    subprocess.call(["mpc", "stop"])  # pause radio (mpc)

# connect the bluetooth decoder (pulseaudio) to the sound output (alsa)
def startBluetooth():
    try:
        temp = str(subprocess.check_output(
            ["sudo", "pactl", "load-module", "module-loopback", "source=bluez_source.C8_D1_0B_E0_1D_B2", "sink=0"],
            universal_newlines=True, stderr=subprocess.STDOUT))  # hardcoded on my phones MAC address for simplicity
        GF.log(temp, "D")
        settings["bluetooth"][2] = temp
        GF.log("Bluetooth started no: " + str(settings["bluetooth"][2]), 'S')
    except:  # if it didn't work, directly disable bluetooth input, because there is no input.
        GF.log("bt connect failed", "E")
        applySetting("geluidbron", "versterkerUit", 'all')

# disconnect bluetooth decoder from speakers
def stopBluetooth():
    GF.log("stopping bluetooth " + str(settings["bluetooth"][2]), "S")
    try:
        subprocess.check_output(["sudo", "pactl", "unload-module", str(settings["bluetooth"][2])],
                                universal_newlines=True, stderr=subprocess.STDOUT)
    except:
        GF.log("bt disconnect failed", "E")

# set the color of the leds, color supplied as hsl or rgb array.
def setColor(color, tp='hsl'):
    if tp == 'hsl':
        r, g, b = colorsys.hsv_to_rgb(color[0], color[1], color[2])
    else:
        r, g, b = color
    # use a parabolic approximation for the color to pwm conversion
    a = 0.9
    g = a * g * g + (1 - a) * g
    r = a * r * r + (1 - a) * r
    b = a * b * b + (1 - a) * b
    # set the PWM values
    IOF.setPWM(0, g)  #g
    IOF.setPWM(1, r)  #r
    IOF.setPWM(2, b)  #b

# set the color of the leds using a sunrise approximation. The value (0-100) is how far the sunrise is.
# from red via orange to full white
def sunrise(value):
    if value < 20:
        h = .25 * (value / 100.0)
    else:
        h = 0.05
    s = 1 - value / 100
    x = (value / 50) - 1
    if value < 50:
        l = 1 - x * x
    else:
        l = 1
    color = [h, s, l]
    setColor(color)  # apply the calculated color


##//////////////////////////////////////////##
##||||functions for periodic updates||||||||##
##\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\##

# get radio text, firs line of mpc output, get text from radio, not supported by all stations
def getRadioText():
    try:
        txt = str(subprocess.check_output("mpc", universal_newlines=True, stderr=subprocess.STDOUT))
        if len(txt) > 90:  #if the radio is playing
            return str(txt.split("\n")[0])
        else:
            return 'Radio tekst is niet beschikbaar'
    except:
        return "MPC is niet beschibaar"

#Write updates to the users, called by main()
def writeUpdates():
    radioText = getRadioText()
    if radioText != settings['radioText'][1]:
        applySetting('radioText', radioText, 'all')  # send radio update to everyone
        IOF.displayWrite(radioText)  #write radiotext to the display


##///////////////////////////////////////////////##
##||||functions for data request from clients||||##
##\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\##

# give a user the datapoints from 'log' and 'field' (a table with measurement data) from 'start' time to 'end' time
def getDataPoints(log, start, end, field="value"):
    qryEnd = ''  # string containing the end of the SQL query used to get the data
    if start <= 1389123003:  # start must be older than the very first logging date, January 2014
        GF.log('getDataPoints: invalid start time', 'E')

    if end is not None and end != '' and end is not False and end >= 1389123003:  # if a valid end time is supplied
        qryEnd = ' and UNIX_TIMESTAMP(timestamp)<='.str(end)  # append the end time to the query

    qry = 'Select UNIX_TIMESTAMP(timestamp) as ts, ' + field + ' from log_' + log + ' where UNIX_TIMESTAMP(timestamp)>=' + str(start) + qryEnd

    data = '['  # start building an array (as string) to store the datapoints
    db = PyDatabase.PyDatabase(host=GF.DBLogin["host"], user=GF.DBLogin["user"], passwd=GF.DBLogin["passwd"],
                               db=GF.DBLogin["db"])
    result = db.Execute(qry, True)

    if result is not None and len(result) > 3:  # if valid result is obtained from the database
        for row in result:  # build the array row by row
            data += '[' + str(row[0]) + ',' + str(row[1]) + '],'

        data = data[:-1] + ']'  # finish the array
        #GF.log("getDataPoints: " + data,'D')
        return data  # and finally return the requested data
    return False


##///////////////////////////////##
##||||socket server functions||||##
##\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\##

# init class for threaded tcp server
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

# init class for the server handler
class ThreadedServerHandler(socketserver.BaseRequestHandler):
    # the handler for the server, this handles the receiving and distributing of messages
    # called when a client tries to connect
    def handle(self):
        self.websocket = False  # wheter a user uses websockets to communicate with the server. Default False
        # websocket=False, normal sockets
        # websocket='web', normal websockets
        # websocket='python', my implementation of websockets in Python. Uses masks in both directions.
        data = self.request.recv(1024)  # receive the request for a connection from the client
        addr = self.request.getpeername()[0]  # the IP address of the client that tries to connect
        db = PyDatabase.PyDatabase(host=GF.DBLogin["host"], user=GF.DBLogin["user"], passwd=GF.DBLogin["passwd"],
                                   db=GF.DBLogin["db"])  # connect to the db to check validity of users

        # check if the client wants to use websockets, if so then send a websocket-handshake
        if "upgrade: websocket" in str(data, "utf-8").lower():
            try:
                self.HandShake(str(data, "utf-8"))
                self.websocket = 'web'
            except:
                GF.log("server: Websocket Upgrade Request from " + str(addr), 'E')
                return

        if self.websocket == 'web':
            data = GF.parse_frame(self.request)  # parse the incoming websocket packet containing the login parameters
        loginData = ""
        # load the logindata from the client, packet in json
        try:
            loginData = json.loads(str(data, "utf-8"))
        except:
            self.sendClient("E: wrong format login package")
            GF.log("server: client from " + str(addr) + " sent wrong login request: " + str(loginData), 'E')
            return

        #check the username and password of the client
        username = str(loginData["username"])
        password = str(loginData["password"])
        GF.log('server: User: ' + username + ' trying to login from: ' + str(addr), 'N')

        # check validity of user
        if addr[0:9] == '192.168.1': #local user,
        # phone, laptop, or ethernet
            if addr[10:13] in allowedIPs:
                if username == 'amblone':  # special user for amblone, the opensource ambilight client
                    self.websocket = 'python'
                    GF.log("local amblone connecting")
                user = [username, 2, 'Lokale gebruiker', None, addr, self]
                GF.log('server: Local user accepted', "N")
                self.sendClient("A:local user")
                #user's color
                user[3] = db.Select(table='users', columns=['value'], condition_and={'usernm': user[0]})[0][0]
                if username != 'amblone':
                    self.sendClient("C" + user[3])
            # IP addres from the raspberry itself. For instance the minute-script user
            elif addr[0:13] == '192.168.1.104':
                # print('minute logging in, switching to websocket protocol')
                user = [username, 2, 'rpi user', None, addr, self]
                self.websocket = 'python'  # switch to websockets here for minute.py
                self.sendClient("A rpi user")
                self.sendClient(json.dumps(settings))  #send the values to minute.py
            #local guest
            else:
                user = ['localguest', 1, 'Lokale gast', None, addr, self]
                GF.log('server: Local guest user accepted', "N")
                self.sendClient("A Local guest user")
                # user's color
                user[3] = db.Select(table='users', columns=['value'], condition_and={'usernm': user[0]})[0][0]
                self.sendClient("C" + user[3])  # get color of local user

        elif username != '' and password != '':  # remote user
            # check user validity here via database
            condition_and = {
                'usernm': username,
                'pwdhash': password
            }
            results = db.Select(table='users', columns=['level', 'fullname', 'value'], condition_and=condition_and)
            if results is False:
                GF.log("server: Failed to execute query: " + db.query, 'E')
                return False
            if results is not None:  # The user exists. name, level, fullname, value
                user = [username, results[0][0], results[0][1], results[0][2], addr, self]
                self.sendClient("A Remote user")
                GF.log('server: Remote user accepted', "N")
                # user's color
                self.sendClient("C" + user[3])
            else:
                GF.log('server: Invalid remote user. Connection stopped', 'N')
                self.sendClient("E invalid user or password send. Stopping connection now")
                return False
        else:  # not valid user
            GF.log('server: Empty login request. Connection stopped ', 'N')
            self.sendClient("E username and password empty. Stopping connection now")
            return False

        # users is [name, level, fullname, value, connectionClassID]; value==color
        connection.append(user)

        # loop to receive messages from client
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
                #GF.log("server: user "+str(user[0])+" send message: "+self.data, 'N')

                #decode data
                type = self.data[0:1]
                data = json.loads(self.data[1:])  # all data is in json format
                if user[1] >= 0:  # if user has enough rights
                    if type == 'M':  # message
                        GF.log("server: client " + str(user[0]) + " send a message: " + str(data), 'N')

                    elif type == "R":  # resend all values
                        GF.log("server: client " + str(user[0]) + " requested value update", 'N')
                        self.sendClient('S' + json.dumps(settings))

                    elif type == "D" and user[1] >= 1:  # download graph
                        print(data)
                        d = data.get('d')
                        s = data.get('s')
                        e = data.get('e')
                        try:
                            points = getDataPoints(d, s, e)
                            GF.log("server: DataPoints for table: " + d)
                        except:
                            GF.log("server: Not possible to get dataPoints", "E")
                        if points:
                            self.sendClient('D{"d":"' + data.get('d') + '","p":' + points + '}')
                        else:
                            self.sendClient('MGeen datapunten gevonden voor dit tijdspan')

                    elif type == 'S' and user[1] == 2:  # setting
                        try:
                            for key, value in data.items():
                                #GF.log(key + ' val: '+str(value), "D")
                                if value is not None and key != '':
                                    applySetting(key, value, self)  # apply setting and put in dictionary
                                else:
                                    self.sendClient("W Empty setting")
                                    GF.log("server: empty message received", 'E')
                        except:  # wrong assumption
                            GF.log('server: Message: ' + self.data + ' is not a command or invalid name or type', 'E')
                            self.sendClient("W Not a command or invalid name or type")

                    elif type == 'P':  # load a page
                        src = '/var/www/' + data.get('p') + '.txt'
                        if data.get('c') == 'True':
                            self.sendClient("W not yet possible to refresh cache via websocket")
                            GF.log("server: Not yet possible to refresh cache via websocket", 'E')

                        self.sendClient('P' + open(src, 'r').read())
                    elif type == 'U':  # Something with a user, like a change of color. For now only color changes
                        color = data.get('c')
                        GF.log("server: User " + user[2] + " updating its color to " + color)
                        if not db.Execute("Update users set value='" + color + "' where usernm='" + user[0] + "'",
                                          fetchall=False):
                            GF.log("server: Failed to execute query: " + db.query, 'E')
                            self.sendClient("W Color change failed")
                        else:
                            sendRound("C" + color, self, username);
                    else:
                        GF.log('server: User ' + user[0] + ' send invalid message', 'E')
                        self.sendClient("W Invalid message send")
                else:
                    GF.log('server: User ' + user[0] + ' tried to send but has not enough rights', 'E')
                    self.sendClient("W Not enough rights for this action")
            except:
                GF.log("server: client " + username + " from " + addr + " disconnected", 'N')
                try:
                    connection.remove(user)
                except:
                    GF.log("Failed to remove user: " + user[0] + " from connected users list", 'E')
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
        fullKey = hashlib.sha1(websocketkey.encode("utf-8") + specificationGUID.encode("utf-8")).digest()
        acceptKey = base64.b64encode(fullKey)
        if protocol != "":
            handshake = "HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Protocol: " + protocol + "\r\nSec-WebSocket-Accept: " + str(
                acceptKey, "utf-8") + "\r\n\r\n"
        else:
            handshake = "HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: " + str(
                acceptKey, "utf-8") + "\r\n\r\n"
        self.request.send(bytes(handshake, "utf-8"))

    #send a message to this client
    def sendClient(self, message):
        print(message)
        if self.websocket:
            self.request.sendall(GF.create_frame(message))
        else:
            self.request.sendall(bytes(message, "utf-8"))


#send a message to all connected clients, except the sender himself. Send a message to all connected clients with the same username
def sendRound(data, sender=False, username=True):
    for u in connection:
        userClass = u[5]
        if userClass != sender and u[0] != 'minute':  # don't send back to sender
            if username == True or username == u[0]:  # to everyone logged in with same account
                try:
                    GF.log("sendRound: sending change: " + data + 'to ' + u[2], "N")
                    userClass.sendClient(data)
                except:
                    GF.log("sendRound: failed to send message to user: " + u[2], "E")
    else:
        return False


def disconnect():
    GF.log("disconnect: Now closing all socket connections", "N")
    for u in connection:
        userClass = u[5]
        try:
            if userClass.websocket:
                userClass.request.sendall(userClass.create_frame("", 8))
            else:
                userClass.request.shutdown(1)
                userClass.request.close()
        except:
            GF.log("disconnect: failed to close socket for user: " + u[0], "E")


##///////////////////////////////////////////////////////##
##||||functions to control and initialize this script||||##
##\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\##

#Init the program. If something went wrong, this will run again to restart
def initDomo():
    GF.log('init: Starting', 'N')

    # fill the settings{} caching dictionary from database
    db = PyDatabase.PyDatabase(host=GF.DBLogin["host"], user=GF.DBLogin["user"], passwd=GF.DBLogin["passwd"],
                               db=GF.DBLogin["db"])
    #  make the query
    columns = ['name', 'type', 'value', 'extra']
    condition = {'settings.type': 'IS NOT NULL'}
    results = None
    # make settings dict, to use instead of database for faster operation
    global settings  # use the global settings
    settings = {}
    # fill settings from the database
    results = db.Select(table='settings', columns=columns, condition_and=condition)
    if results is False:
        GF.log("init: could not execute query: " + db.query, 'E')

    if results is not None:
        for row in results:
            # row[0]#name
            # row[1]#type
            # row[2]#value
            # row[3]#extra
            GF.log("init: " + str(row), 'N')
            # row[2], the value, can be a JSON-array, in that case it has to be parsed first.
            try:
                if row[2] is None:
                    r2 = None
                else:
                    try:
                        r2 = json.loads((row[2].strip('"')))
                    except:
                        r2 = json.loads(row[2])
            except:
                GF.log("init: " + str(row[2]) + " could not be decoded", 'E')

            settings[row[0]] = [row[1], r2, row[3]]  # list(row[1:4])  # add setting to dictionary

    GF.log('init: dictionary: ' + str(settings), 'D')

    # apply all settings cached in the settings{} dict. This way everything is restored to its database-values
    for key, value in settings.items():
        applySetting(str(key), value[1], 'none')  # apply setting, sending key, value. Don't send to clients

    GF.log('init: completed, starting now!', 'N')

# main init function for tcp server
ThreadedServerHandler.SendRound = sendRound

# initialize the settings{} dict and the settings themselves
initDomo()

# main func, start the socketserver and keep looping to write updates
if __name__ == "__main__":
    GF.log("Jeroen van Oorschot, domotica-webradio 2013-2015", "N")
    parser = argparse.ArgumentParser(description='Jeroen van Oorschot, Domotica system and webradio')
    # parser.add_argument('--ip', nargs='?', const=1, type=str, default="localhost", help='specify the ip adress wich the server will bind to, defaults to localhost')
    parser.add_argument('--port', nargs='?', const=1, type=int, default=600, help='socketserver port nr, default 600')
    #PORT = 600 #
    PORT = parser.parse_args().port
    HOST = '192.168.1.104'  # hardcoded IP of my raspberry pi

    GF.log("host: " + str(HOST) + ":" + str(PORT), "N")
    GF.log("main: starting server ...", "N")
    sleep(1)

    server = ThreadedTCPServer((HOST, PORT), ThreadedServerHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    GF.log("main: Server loop running, waiting for connections ...", 'N')

    # loop to write periodical updates.
    while True:
        sleep(writeUpdateTime)
        try:
            writeUpdates()
        except:
            GF.log("main: Error in writeUpdates", "E")


# code that can be used to supply commands directly to the script when it is running
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
