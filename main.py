# This Python file uses the following encoding: utf-8
# Generic imports
import os, sys
import mariadb
from datetime import datetime, time
import getopt  # for command-line options

# Setup logging
from logging.handlers import RotatingFileHandler
import http.client, urllib #For pushover emergency messages

# Application-specific inports
from RPi import GPIO
import PyQt5
import QtCharts 2.15
from PyQT5.QtWidgets import *
import mainwindow_auto
from pathlib import Path

# Sensor-specific imports
global pulse_start

# Global variables to be assigned/called
sqlConn = None
sqlCursor = None
curLog = None

sensorList = {
    'at1':'lcdAirTemp',
    'ah1':'lcdAirHumidity',
    'wu1':'lcdTodayPower',
    'eu1':'lcdTodayWater',
    'wu2':'lcdTotalWater',
    'eu2':'lcdTotalPower',
    'ao1':'lcdAirO2',
    'rdw':'lcdRDW',
    'rwl':'lcdRWL'
}

class HydroOffice(QMainWindow):
    global sensorList
    def __init__(self):
        super(HydroOffice, self).__init__()
        self.load_ui()

    def load_ui(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        loader.load(ui_file, self)
        ui_file.close()

    def updateLCD(inName):
        # Handle Numerical Display update
        pass
    def updateChart(inName):
        # Handle Chart update
        pass
    def btnPush():
        # Handle a button push
        pass

def setupLogging(inMode):
    global curLog
    startTime = datetime.now()
    logFile = '/home/pi/hydrponics/logs/LOG_'+str(startTime.strftime("%Y%m%d_%H%M%S"))
    log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
    handler = RotatingFileHandler(logFile, mode='a', maxBytes=5*1024*1024, backupCount=2, encoding=None, delay=0)
    handler.setFormatter(log_formatter)
    if inMode == "INFO":
        handler.setLevel(logging.INFO)
        curLog.setLevel(logging.INFO)
    if inMode == "DEBUG":
        handler.setLevel(logging.DEBUG)
        curLog.setLevel(logging.DEBUG)
    curLog = logging.getLogger('root')
    curLog.addHandler(handler)
    curLog.info("Initialized log")

def setPumpState(pin,flow):
    if flow:
        mode = GPIO.LOW
    else:
        mode = GPIO.HIGH
    GPIO.output(relayGPIO, mode)

def connectMariaDB():
    global sqlConn
    global sqlCursor
    # Connect to MariaDB Platform
    try:
        sqlConn = mariadb.connect(
            host="localhost",
            port=3306,
            database="hydroponics"
        )
        sqlConn.autocommit = True
        # Get cursor
        sqlCursor = sqlConn.cursor()
    except mariadb.Error as e:
        print("Error connecting to MariaDB Platform: "+str(e))
        sys.exit(1)

def insertRecord(sensor,data,comment):
    global sqlConn
    global sqlCursor
    # Get sensor DB name
        # not done, we're going to feed it directly
    # Set up insert
    sql = "INSERT INTO sensor_data VALUES ({},{},{},{});".format(datetime.now(),sensor,data,comment)
    # Execute
    sqlCursor.execute(sql)

def getUltransonicDistance(trigPin,echoPin):
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

def sendEmergencyAlert(message):
    log.info("Sending emergency message: '"+message+"'")
    pushoverConn = httplib.HTTPSConnection("api.pushover.net:443")
    pushoverConn.request("POST", "/1/messages.json",
         urllib.urlencode({
             "token": pushoverToken,
             "user": pushoverUserKey,
             "message": message,
         }),
        {"Content-type": "application/x-www-form-urlencoded"}
    )
    response = pushoverConn.getresponse()
    log.debug("Pushover response: "+str(response))

def main():
    curLog.info("Started main loop")
    # Initialize Sensors
    GPIO.setmode(GPIO.BCM)
    # DHT 11

    # Ultrasonic Distance/Reservoir WL
    GPIO.setup(trigPin, GPIO.OUT)
    GPIO.setup(echoPin, GPIO.IN)

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

    log.debug("Main loop setup compelte, moving into repeat")
    while True: #Loop until interrupted
        # AM2032 Temp/Humudity
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, dhtpin)
        insertRecord("at1",temperature,"degC")
        log.info("Air Temp Reading: "+str(temperature)+"deg C")
        insertRecord("ah1",humidity,"%")
        log.info("Air Humidity Reading: "+str(humidity)+"%")

        # WL Float
        # Check value
        # if level has changed, flip operation
        currentPlantFlowState = GPIO.input(wlFloatPin)
        if waterFlowingToPlants:
            plantFlowTime = datetime.now() - plantFlowStartTime
        if currentPlantFlowState == GPIO.HIGH and waterFlowingToPlants == True: #sensor is off, water is flowing
            setPumpState(plantFlowPin,False) #turn water off
            plantFlowDelayStartTime = datetime.now()
            waterFlowingToPlants = False
            log.info("Turning plant flow off")
        elif currentPlantFlowState == GPIO.Low and waterFlowingToPlants == False and plantFlowDelayTimer == False and disablePlantFlow == False: #sensor is on, water needs to flow
            setPumpState(plantFlowPin,True) #turn water on
            plantFlowStartTime = datetime.now()
            waterFlowingToPlants = True
            log.info("Turning plant flow on,adding nutrients")
            setPumpState(nutrientFlowPin,True) #turn nutrients on, hold here for 1 second just to make sure we don't overfeed
            time.sleep(1) #1 second
            setPumpState(nutrientFlowPin,False)
            log.info("Nutrient addition finished")

        elif waterFlowingToPlants  and plantFlowTime > maxFlowSeconds: #emergency shutoff, we're running too long_options
            setPumpState(plantFlowPin,False)
            disablePlantFlow = True
            sendEmergencyAlert("Emergency! Water flow to plants disabled due to flow time exceedance")
            log.error("Turning plant flow off, disabling, and sending alert")

        # O2
        # TODO once we get this figured out
        #insertRecord("ao1",curValue,"%")
        #log.info("Air Oxygen Reading: "+str(curValue)+"%")

        # pH
        # TBD if sensor is installed
        #insertRecord("pH1",curValue,"")
        #log.info("Air Humidity Reading: "+str(curValue))

        # Reservoir level (ultrasonic distance)
        curDistance = getUltransonicDistance(trigPin,echoPin)
        if waterFlowingToReservoir:
            reservoirFlowTime = datetime.now() - reservoirFlowStartTime
        if curReservoirDistance > minReservoirDistance and waterFlowingToReservoir == True: #sensor < min distance, water is flowing
            setPumpState(reservoirFlowPin,False) #turn water off
            reservoirFlowDelayStartTime = datetime.now()
            waterFlowingToReservoir = False
        elif currentPlantFlowState == GPIO.Low and waterFlowingToReservoir == False and plantFlowDelayTimer == False and disableReservoirFlow == False: #sensor is on, water needs to flow
            setPumpState(reservoirFlowPin,True) #turn water on
            reservoirFlowStartTime = datetime.now()
            waterFlowingToReservoir = True
        elif waterFlowingToReservoir == True and reservoirFlowTime > maxFlowSeconds: #emergency shutoff, we're running too long_options
            setPumpState(reservoirFlowPin,False)
            disableReservoirFlow = True
            sendEmergencyAlert("Emergency! Water flow to reservoir disabled due to flow time exceedance")

        # Nutrient flow
        # Theory: add 1 ml of nutrients whenever water is added to plants
        # So this is handled in plant flow above

        # loop management - check timers, resets, etc.
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

if __name__ == "__main__":
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
            else:
                assert False, "Unhandled command-line option, please try again."
    except getopt.error as e:
        log.error("Getopt Exception: "+str(e))
    except Exception as e:
        log.error("Generic exception during command-line processing: "+str(e))

    try:
        # Start logging
        setupLogging(logLevel)
        # Start UI
        app = QApplication([])
        widget = HydroOffice()
        widget.show()

        # Start main loop
        main()

    except Exception as e:
        curLog.critical("Generic Exception: "+str(e))
    finally:
        #close connect
        sqlConn.close()
        curLog.debug("Connection Closed")
        GPIO.cleanip
