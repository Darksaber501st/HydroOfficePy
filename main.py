# This Python file uses the following encoding: utf-8
# Generic imports
import os, sys
import mariadb
import datetime import datetime
import getopt  # for command-line options

# Setup logging
from logging.handlers import RotatingFileHandler

# Application-specific inports
from RPi import GPIO
import PyQt5
import QtCharts 2.15
from PyQT5.QtWidgets import *
import mainwindow_auto
from pathlib import Path

# Global variables to be assigned
global conn  #MariaDB connection
global cursor  #MariaDB update cursor
global curLog
conn = None
cursor = None
curLog = None
global sensorList = {
    airTemp = {
        lcdName = 'lcdAirTemp'
    }
    'XXXSensorName':'lcdAirTemp'
    'XXXSensorName':'lcdWaterTemp'
    'XXXSensorName':'lcdWaterUse'
    'XXXSensorName':'lcdAirHumidity'
}

class HydroOffice(QMainWindow):
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

def connectMariaDB():
    # Connect to MariaDB Platform
    try:
        conn = mariadb.connect(
            host="localhost",
            port=3306,
            database="hydroponics"
        )
        conn.autocommit = True
        # Get cursor
        cursor = conn.cursor()
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

def insertRecord(sensor,data,comment):
    # Get sensor DB name

    # Set up insert
    sql = "INSERT INTO sensor_data VALUES ({},{},{},{});".format(datetime.now(),sensor,data,comment)
    # Execute
    cursor.execute(sql)

def getUltransonicDistance(trigPin,echoPin):
    GPIO.output(trigPin, False)
    # print("Waiting For Sensor To Settle")
    time.sleep(2)

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

def main():
    curLog.info("Started main loop")
    # Initialize Sensors
    GPIO.setmode(GPIO.BCM)
    # DHT 11

    # Ultrasonic Distance/Reservoir WL
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)

    while True:
        # DHT 11 Temp/Humudity

        insertRecord("at1",curValue,"")
        log.info("Air Temp Reading: "+str(curValue))


        insertRecord("wt1",curValue,"")
        log.info("Air Humidity Reading: "+str(curValue))


        # WL Float
        # Check value
        # if level has changed, flip operation
        flowTime = datetime.now() - flowStartTime
        currentState = GPIO.digitalRead(wlFloatPin)
        if currentState == GPIO.HIGH and waterFlowing == True: #sensor is off, water is flowing
            setPumpState(plantFlowPin,False) #turn water off
            delayTimer = delayTime # Set a sanity check, only start flowing again after timer runs
            delayStartTime = datetime.now()
        elif currrentState == GPIO.Low and waterFlowing == False and delayTimer = 0: #sensor is on, water needs to flow
            setPumpState(plantFlowPin,True) #turn water on
            flowStartTime = datetime.now()
        elif waterFlowing == True and flowTime > maxFlowSeconds: #emergency shutoff, we're running too long_options
            setPumpState(plantFlowPin,False)
            disablePlantFlow = True
            sendEmergencyAlert()

        # O2


        insertRecord("wt1",curValue,"")
        log.info("Air Oxygen Reading: "+str(curValue)+"%")

        # pH


        insertRecord("wt1",curValue,"")
        log.info("Air Humidity Reading: "+str(curValue))

        # loop management
        if delayTimer = True:
            delayTime = datetime.now() - delayStartTime
            if delayTime > restartDelay:
                delayTimer =

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
        conn.close()
        curLog.debug("Connection Closed")
