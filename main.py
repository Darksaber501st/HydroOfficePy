# This Python file uses the following encoding: utf-8
# Generic imports
import os, sys
#import mariadb
from datetime import datetime
import time
import getopt  # for command-line options
import traceback

# Setup logging
import logging
from logging.handlers import RotatingFileHandler
import http.client, urllib #For pushover emergency messages

# Application-specific inports
from RPi import GPIO
import PyQt5
#import QtCharts 2.15
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
#import pyqtgraph as pg
#from pyqtgraph import PlotWidget, plot
#import mainwindow_auto
from pathlib import Path
import Adafruit_DHT

# Global variables to be assigned/called
sqlConn = None
sqlCursor = None
curLog = None
widget = None
prevLoopEndTime = None

#sensorList = {
#    'at1':'lcdAirTemp',
#    'ah1':'lcdAirHumidity',
#    'wu1':'lcdTodayPower',
#    'eu1':'lcdTodayWater',
#    'wu2':'lcdTotalWater',
#    'eu2':'lcdTotalPower',
#    'ao1':'lcdAirO2',
#    'rdw':'lcdRDW',
#    'rwl':'lcdRWL'
#}

# PIN DEFS
wlFloatPin = 22
dhtPin = 6
reservoirFlowPin = 27
plantFlowPin = 17
nutrientFlowPin = 18
#trigPin = 23
#echoPin = 24
trigPin = 24
echoPin = 23

class HydroOffice(QMainWindow):
    global sensorList
    def __init__(self):
        super(HydroOffice, self).__init__()
        self.ui = loadUi(os.path.dirname(os.path.realpath(__file__)),baseinstance=self)
        self.setWindowTitle("Hydroponics HMI")
        self.show()
        self.mainLoop()

    #@pyqtSlot()
    def setPumpState(self,pin,flow):
        # TODO re-enable
        #if flow:
        #    mode = GPIO.LOW
        #else:
        #    mode = GPIO.HIGH
        #GPIO.output(relayGPIO, mode)
        pass

    def connectMariaDB(self):
        # TODO re-enable
        #global sqlConn
        #global sqlCursor
        # Connect to MariaDB Platform
        #try:
        #    sqlConn =+ mariadb.connect(
        #        host="localhost",
        #        port=3306,
        #        database="hydroponics"
        #    )
        #    sqlConn.autocommit = True
        #    # Get cursor
        #    sqlCursor = sqlConn.cursor()
        #except mariadb.Error as e:
        #    print("Error connecting to MariaDB Platform: "+str(e))
        #    sys.exit(1)
        pass

    def insertRecord(self,sensor,data,comment):
        # TODO re-enable
        #global sqlConn
        #global sqlCursor
        # Get sensor DB name
            # not done, we're going to feed it directly
        # Set up insert
        #sql = "INSERT INTO sensor_data VALUES ({},{},{},{});".format(datetime.now(),sensor,data,comment)
        # Execute
        #sqlCursor.execute(sql)
        pass

    def getRecord(self,sensor):
        # TODO re-enable
        #global sqlConn
        #global sqlConn
        # set up select

        #sql = "SELECT * FROM hydroponics WHERE sensor = '"+str(sensor)+"' ORDER BY record_dt ASCENDING"
        results = sqlCursor.execute(sqlConn)
        return results

    def getUltransonicDistance(self,trigPin,echoPin):
        GPIO.output(trigPin, False)
        time.sleep(1) #Wait for sensor to settle
        GPIO.output(trigPin, True)
        time.sleep(0.00001)
        GPIO.output(trigPin, False)

        pulse_start = time.time()
        while GPIO.input(echoPin) == 0:
            pulse_start = time.time()

        while GPIO.input(echoPin) == 1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        distance = round(distance, 2)
        return distance

    def sendEmergencyAlert(self,message):
        # TODO re-enable
        #log.info("Sending emergency message: '"+message+"'")
        #pushoverConn = httplib.HTTPSConnection("api.pushover.net:443")
        #pushoverConn.request("POST", "/1/messages.json",
        #     urllib.urlencode({
        #         "token": pushoverToken,
        #         "user": pushoverUserKey,
        #         "message": message,
        #     }),
        #    {"Content-type": "application/x-www-form-urlencoded"}
        #)
        #response = pushoverConn.getresponse()
        #log.debug("Pushover response: "+str(response))
        pass

    def mainLoop(self):
        global widget
        global prevLoopEndTime
        global trigPin
        global echoPin
        global dhtPin
        global wlFloatPin
        global plantFlowPin
        global reservoirFlowPin
        global nutrientFlowPin
        global curLog
        global debugMode

        curLog.info("Started main loop")
        # Initialize Sensors
        GPIO.setmode(GPIO.BCM)
        # AM2302
            #nothing required
        # Ultrasonic Distance/Reservoir WL
        GPIO.setup(trigPin, GPIO.OUT)
        GPIO.setup(echoPin, GPIO.IN)
        # Water level float
        GPIO.setup(wlFloatPin, GPIO.IN)
        # Pumps and Valves
        GPIO.setup(reservoirFlowPin, GPIO.OUT)
        GPIO.setup(nutrientFlowPin, GPIO.OUT)
        GPIO.setup(plantFlowPin, GPIO.OUT)

        # Setup other variables
        plantFlowDelayTimer = False #Controls whether we're waiting for plant for to kick back on
        disablePlantFlow = False #Emergency override for plant flow
        reservoirFlowDelayTimer = False #Controls whether we're waiting for reservoir flow to kick back on
        disableReservoirFlow = False #Emergency override for reservoir flow
        #nutrientFlowDelayTimer = False #Controls whether we're waiting for nutrient flow to kick back on
        #disableNutrientFlow = False #Emergency ovewrride for nutrient flow

        waterFlowingToPlants = False #Status variable for flow to plants
        waterFlowingToReservoir = False #Status variable for flow to reservoir
        #nutrientsFlowing = False #Status variable for nutrient flow
        plantFlowTime = 0 #Time elapsed for flow to plants
        reservoirFlowTime = 0 #Time elapsed for flow to reservoir
        #nutrientFlowTime = 0 #Time elapsed for nutrient flow
        plantFlowStartTime = 0
        reservoirFlowStartTime = 0
        #nutrientFlowStartTime = 0

        curLog.debug("Main loop setup compelte, moving into repeat")
        prevLoopEndTime = datetime.now()
        while True: #Loop until interrupted
            # AM2032 Temp/Humudity
            humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, dhtPin)
            self.insertRecord("at1",temperature,"degC")
            if debugMode: print("Temperature: "+str(temperature)+"*C")
            #widget.findChild(QLCDNumber,"lcdAirTemp").value = temperature
            curLog.info("Air Temp Reading: "+str(temperature)+"deg C")
            self.insertRecord("ah1",humidity,"%")
            #widget.findChild(QLCDNumber,"lcdAirRH").value = humidity
            curLog.info("Air Humidity Reading: "+str(humidity)+"%")

            # WL Float
            # Check value
            if debugMode: print("Checking WL Float")
            # if level has changed, flip operation
            currentPlantFlowState = GPIO.input(wlFloatPin)
            if waterFlowingToPlants:
                plantFlowTime = datetime.now() - plantFlowStartTime
            if currentPlantFlowState == GPIO.HIGH and waterFlowingToPlants == True: #sensor is off, water is flowing
                self.setPumpState(plantFlowPin,False) #turn water off
                plantFlowDelayStartTime = datetime.now()
                waterFlowingToPlants = False
                curLog.info("Turning plant flow off")
            elif currentPlantFlowState == GPIO.LOW and waterFlowingToPlants == False and plantFlowDelayTimer == False and disablePlantFlow == False: #sensor is on, water needs to flow
                self.setPumpState(plantFlowPin,True) #turn water on
                plantFlowStartTime = datetime.now()
                waterFlowingToPlants = True
                curLog.info("Turning plant flow on,adding nutrients")
                self.setPumpState(nutrientFlowPin,True) #turn nutrients on, hold here for 1 second just to make sure we don't overfeed
                time.sleep(1) #1 second
                self.setPumpState(nutrientFlowPin,False)
                curLog.info("Nutrient addition finished")
            elif waterFlowingToPlants  and plantFlowTime > maxFlowSeconds: #emergency shutoff, we're running too long_options
                self.setPumpState(plantFlowPin,False)
                disablePlantFlow = True
                self.sendEmergencyAlert("Emergency! Water flow to plants disabled due to flow time exceedance")
                curLog.error("Turning plant flow off, disabling, and sending alert")

            # O2
            # TODO once we get this figured out
            if debugMode: print("Checking O2")
            #insertRecord("ao1",curValue,"%")
            #curLog.info("Air Oxygen Reading: "+str(curValue)+"%")

            # pH
            # TBD if sensor is installed
            if debugMode: print("Checking pH")
            #insertRecord("pH1",curValue,"")
            #curLog.info("Air Humidity Reading: "+str(curValue))

            # Reservoir level (ultrasonic distance)
            if debugMode: print("Checking US Distance")
            curDistance = self.getUltransonicDistance(trigPin,echoPin)
            curLog.info("Level Reading: "+str(curDistance)+"cm")
            if debugMode: print("Current Distance: "+str(curDistance)+"cm")


            if waterFlowingToReservoir:
                reservoirFlowTime = datetime.now() - reservoirFlowStartTime
            if curReservoirDistance > minReservoirDistance and waterFlowingToReservoir == True: #sensor < min distance, water is flowing
                self.setPumpState(reservoirFlowPin,False) #turn water off
                reservoirFlowDelayStartTime = datetime.now()
                waterFlowingToReservoir = False
            elif currentPlantFlowState == GPIO.LOW and waterFlowingToReservoir == False and plantFlowDelayTimer == False and disableReservoirFlow == False: #sensor is on, water needs to flow
                self.setPumpState(reservoirFlowPin,True) #turn water on
                reservoirFlowStartTime = datetime.now()
                waterFlowingToReservoir = True
            elif waterFlowingToReservoir == True and reservoirFlowTime > maxFlowSeconds: #emergency shutoff, we're running too long_options
                self.setPumpState(reservoirFlowPin,False)
                disableReservoirFlow = True
                self.sendEmergencyAlert("Emergency! Water flow to reservoir disabled due to flow time exceedance")

            # Nutrient flow
            # Theory: add 1 ml of nutrients whenever water is added to plants
            # So this is handled in plant flow above

            # loop management - check timers, resets, etc.
            # check update increment for external variables like power
            curTime = dateTime.now()
            if prevLoopEndTime - curTime > externalUpdateIncrement:
                self.doExternalUpdates()
            if plantFlowDelayTimer: #Reset flow to plants
                plantFlowDelayTime = datetime.now() - plantFlowDelayStartTime
                if plantFlowDelayTime > restartDelay:
                    plantFlowDelayTimer = False
                    log.info("Plant flow delay timer exceeded, resetting...")
            if reservoirFlowDelayTimer: #Reset flow to reservoir
                reservoirFlowDelayTime = datetime.now() - reservoirFlowDelayStartTime
                if reservoirFlowDelayTime > restartDelay:
                    reservoitrFlowDelayTimer = False
                    log.info("Reservoir flow delay timer exceeded, resetting...")
            # finalCheck
            prevLoopEndTime = dateTime.now()
            if debugMode: print("Completed loop at "+prevLoopEndTime.strftime("%Y%m%d_%H%M%S"))

def setupLogging(inMode):
	global curLog
	startTime = datetime.now()
	#logFile = '/home/pi/Desktop/iHydroOfficePy/LOG_'+str(startTime.strftime("%Y%m%d_%H%M%S"))+".txt"
	logFile = '/home/pi/Desktop/HydroOfficePy/LOG_'+str(startTime.strftime("%Y%m%d"))+".txt"
	log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
	handler = RotatingFileHandler(logFile, mode='a', maxBytes=5*1024*1024, backupCount=2, encoding=None, delay=0)
	handler.setFormatter(log_formatter)
	curLog = logging.getLogger('root')
	if inMode == "INFO":
	    handler.setLevel(logging.INFO)
	    curLog.setLevel(logging.INFO)
	if inMode == "DEBUG":
	    handler.setLevel(logging.DEBUG)
	    curLog.setLevel(logging.DEBUG)
	curLog.addHandler(handler)
	curLog.info("Initialized log")

if __name__ == "__main__":
    #global widget
    debugMode = False
    # Process command-line args and handle appropriately
    logLevel = "INFO"
    argumentList = sys.argv[1:]
    options = "d"
    long_options = ["debug"]
    try:
        arguments, values = getopt.getopt(argumentList, options, long_options)
        for currentArgument, currentValue in arguments:
            if currentArgument in ("-d", "--debug"):
                logLevel = "DEBUG"
                debugMode = True
            else:
                assert False, "Unhandled command-line option, please try again."
    except getopt.error as e:
        print("Getopt Exception: "+str(e))
    except Exception as e:
        print("Generic exception during command-line processing: "+str(e))

    try:
        # Start logging
        setupLogging(logLevel)
        # Start UI
        app = QApplication([])
        widget = HydroOffice()
        sys.exit(app.exec_())

    except Exception as e:
        print("Generic Exception: "+str(e))
        curLog.critical("Generic Exception: "+str(e))
        traceback.print_exc()
    finally:
        #close connect
        #sqlConn.close()
        curLog.debug("Connection Closed")
        GPIO.cleanup()