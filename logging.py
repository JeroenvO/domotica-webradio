#!/usr/bin/python


#Python Raspberry Pi Logging
#Jeroen van Oorschot 2014
#Server side script write logs to database


import subprocess
import PyDatabase
import wiringpi2 as wp
import GFunc
import serial

GF = GFunc.GFunc()
wp.wiringPiSetup()
wp.mcp23017Setup(64,0x20)#initialize expander, needed for output pin 66 for smart meter
wp.pinMode(66,1)
wp.digitalWrite(66,0)

#####GPIO Functions
#set output
def setOutput(pin, value):
    print ("set " + pin + " to " + value)
    #set gpio


########LOG FUNCTIONS
#write a value in a log
def writeLog(table,values):
    db = PyDatabase.PyDatabase(host=GF.DBLogin["host"], user=GF.DBLogin["user"], passwd=GF.DBLogin["passwd"], db=GF.DBLogin["db"])
    #create connection and cursor
    # cursor.execute("INSERT INTO "+table+" (value, timestamp) VALUES ('"+value+"', NOW())")

    if not db.Insert(table=table, values=values):
        print("Could not execute query: " + db.query)

    db.Close()

#cpu temp logger
def logCPUTemp():
    proc = str(subprocess.check_output(["/opt/vc/bin/vcgencmd", "measure_temp"], universal_newlines=True, stderr=subprocess.STDOUT))
    temp = proc[5:7]
    writeLog("log_hwrpi", {"cpu_temp": temp})
#    writeLog("log_CPUTemp",temp)

#dht11 temp/hum logger
def logDHT11():
    proc = str(subprocess.check_output(["sudo", "/home/pi/dht11"], universal_newlines=True, stderr=subprocess.STDOUT))
    hum = proc[2:6]
    temp = proc[9:13]
    writeLog("log_environment", {'home_temp': temp, 'home_hum': hum})
    #overbodig nu.
 #   writeLog("log_home_temp", temp)
 #   writeLog("log_home_hum", hum)

#read slimme meter: credits to http://gejanssen.com/howto/Slimme-meter-uitlezen/index.html
def logSmartMeter():
    wp.digitalWrite(66,1)
    #Set COM port config
    ser = serial.Serial()
    ser.baudrate = 9600
    ser.bytesize=serial.SEVENBITS
    ser.parity=serial.PARITY_EVEN
    ser.stopbits=serial.STOPBITS_ONE
    ser.xonxoff=0
    ser.rtscts=0
    ser.timeout=20
    ser.port="/dev/ttyAMA0"
    try:
        GF.log("poort open",'D')
        GF.log("poort open",'D')
        ser.open()
    except:
        GF.log("ser open gefaald",'E')
    for i in range(0,20):
        line=''
        #Read 1 line van de seriele poort
        try:
            line = ser.readline()
            GF.log(line+'\n','D')
        except:
            GF.log("Seriële poort kan niet gelezen worden",'e')
        line=str(line).strip()[2:]

#        GF.log(line,'d')

        if line[0:9] == "1-0:1.8.1":
            elec_low = str(int(line[10:15]))
            print("daldag     ", elec_low , "kWh")
        elif line[0:9] == "1-0:1.8.2":
            elec_high = str(int(line[10:15]))
            print("piekdag    ", elec_high , "kWh")
        # Daltarief, teruggeleverd vermogen 1-0:2.8.1
        #elif stack[stack_teller][0:9] == "1-0:2.8.1":
         #   print "dalterug   ", stack[stack_teller][10:15]
        # Piek tarief, teruggeleverd vermogen 1-0:2.8.2
        #elif stack[stack_teller][0:9] == "1-0:2.8.2":
            #print "piekterug  ", stack[stack_teller][10:15]
        # Huidige stroomafname: 1-0:1.7.0
        elif line[0:9] == "1-0:1.7.0":
            elec_cur = str(int(float(line[10:17])*1000))
            print("afgenomen vermogen      ", elec_cur , " W")
        # Huidig teruggeleverd vermogen: 1-0:1.7.0
        #elif stack[stack_teller][0:9] == "1-0:2.7.0":
         #   print "teruggeleverd vermogen  ", int(float(stack[stack_teller][10:17])*1000), " W"
        # Gasmeter: 0-1:24.3.0
        elif line[0:1] == "(":
            gas = str(int(float(line[1:10])*1000))
            print("Gas                     ", gas, " dm3")
        else:
            pass

    #Close port and show status
    try:
        ser.close()
    except:
        GF.log("Seriële poort kon niet gesloten worden",'e')

    writeLog("log_energy", {'elec_high': elec_high, 'elec_low': elec_low, 'elec_cur': elec_cur, 'gas': gas})
    wp.digitalWrite(66,0)





#called by scheduler, calls logging functions
def fillLogs():
    logCPUTemp()
    logDHT11()
    logSmartMeter()
    print("logging finished")

	
	
######DB
# def connectDB():
# 	while True:
# 		try:
# 			con = MySQLdb.connect(host="localhost", # your host, usually localhost
# 								 user="root", # your username
# 								  passwd="RPIJvO262SADF", # your password
# 								  db="RPi") # name of the data base
# 			#autocommit changes and so autorefresh db
# 			print "db connected"
# 			con.autocommit(True)
# 			print "autocommit enabled"
# 			break
# 		except:
# 			print "Error connecting to MYSQL, retrying"
# 			sleep(2)
# 	return con
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
# file_path = '/var/lock/logging'
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
#call for logs
fillLogs()
