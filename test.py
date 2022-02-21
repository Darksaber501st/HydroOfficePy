# This Python file uses the following encoding: utf-8
# Generic imports
import os, sys
import mariadb
import datetime import datetime
import getopt  # for command-line options

# Setup logging
from logging.handlers import RotatingFileHandler

# Application inports
from RPi import GPIO
import PyQt5
import QtCharts 2.15
from PyQT5.QtWidgets import *
import mainwindow_auto
from pathlib import Path

# Special sensor packages as needed
import Adafruit_DHT

# Global variables to be assigned
global conn = None #MariaDB connection
global cursor = None #MariaDB update cursor
global curLog = None


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
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

def insertRecord(

def main():
    curLog.info("Started main loop")
    # Get command-line args and handle appropriately

    argumentList = sys.argv[1:]


    while True:
        # DHT 11 Temp/Humudity

        # WL Float


        # Get Cursor
        cur = conn.cursor()

        for dataType in dataTypes:
            # Get data
            cur.execute("SELECT record_dt, sensor_rd, sensor_id FROM data WHERE sensor_id='"+dataType+"' ORDER BY record_dt DESC LIMIT 1;")

            # Process results
            for (record_dt, sensor_rd, sensor_id) in cur:
                print(f"First Name: {first_name}, Last Name: {last_name}")
                getUpdate(functions[sensor_id], record_dt, sensor_rd)

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



