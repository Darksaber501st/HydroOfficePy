import RPi.GPIO as GPIO
import getopt, sys, time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
def main(argv):
   runTime = None
   relayGPIO = None
   try:
      opts, args = getopt.getopt(argv,"hp:t:",["help=","pin=","time="])
   except getopt.GetoptError:
      print('relay_test.py -r <relay GPIO ID> -o <on/off>')
      sys.exit(2)
   for opt, arg in opts:
      if opt in ('-h','--help'):
         print('relay_test.py -r <relay GPIO ID> -o <on/off>')
         sys.exit()
      elif opt in ("-p", "--pin"):
         relayGPIO = int(arg)
      elif opt in ("-t", "--time"):
         runTime = int(arg)
         if runTime < 0 or runTime > 30:
            print("Error! Time is limited to 1-30 seconds")
            sys.exit(2)
      else:
         print("Invalid paramater passed, valid paramters are -t (time in seconds) or -p (GPIO pin#)")
         sys.exit(2)

   if runTime is None:
      print("Error! Run time not defined, use '-t' or '--time' to specify, 1-30 seconds")
      sys.exit(2)
   if relayGPIO is None:
      print("Error! Relay pin not defined, use '-p' or '--pin' to specify")
      sys.exit(2)
   if relayGPIO not in [4,17,18,27,22,23,24,25,5,6,12,13,16,26]:
      print("Error, invalid GPIO pin# specified!")
      sys.exit(2)

   GPIO.setup(relayGPIO, GPIO.OUT)
   GPIO.output(relayGPIO, GPIO.LOW)
   time.sleep(runTime)
   GPIO.output(relayGPIO, GPIO.HIGH)
   GPIO.cleanup()

if __name__ == "__main__":
   try:
     main(sys.argv[1:])
   except Exception as e:
     print ("Exception!: "+str(e))
   finally:
#     GPIO.cleanup()
     sys.exit(0)
