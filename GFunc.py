__author__ = 'jvo'

#General functions used in Raspberry pi webradio

import time
from time import sleep
import datetime
import PyDatabase

class GFunc():

    #read the db login file to get username and password for mysql login
    def __init__(self): #creates the database connection itself
        while True:
            try:
                DBLoginFile = open("/home/pi/DBLogin.txt",'r')
                DBLoginLines = DBLoginFile.readlines()
                DBLoginFile.close()
                self.DBLogin = {}
                for line in DBLoginLines:
                    if line[0] == "#" or line == "":
                        continue
                    line = line.split("=")
                    self.DBLogin[line[0]] = line[1].split('"')[1].strip()
                #print("Logging in with: " + str(self.DBLogin))
                break
            except:
                self.log("Error parsing db login parameters, retrying in 5s",'E')
                sleep(5)


    #time in 10*microseconds
    def time10(self):
        return str(int(round(time.time() * 100)))

    #write a changed setting to the database
    def update(self, name, value):
        db = PyDatabase.PyDatabase(host=self.DBLogin["host"], user=self.DBLogin["user"], passwd=self.DBLogin["passwd"], db=self.DBLogin["db"])
        values = {
            'value' : value,
            'changetime' : str(self.time10())
        }
        condition = {
            'name' : name
        }
        if not db.Update(table='settings', values=values, condition_and=condition):
            self.log("Could not execute query: " + db.query,'E')
        db.Close()


    #log
    #code: U unspeciefied, E error, N notice, S setting, D debug
    def log(self, txt, code="Unspecified"):
        ts = datetime.datetime.today().strftime("%Y-%m-%d %H:%M")
        print("["+str(ts)+"] ["+str(code[0])+"] "+str(txt))


