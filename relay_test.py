import RPi.GPIO as GPIO
import getopt, sys
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
def main(argv):
   mode = None
   relayGPIO = None
   try:
      opts, args = getopt.getopt(argv,"hp:o:",["help=","pin=","option="])
   except getopt.GetoptError:
      print('relay_test.py -r <relay GPIO ID> -o <on/off>')
      sys.exit(2)
   for opt, arg in opts:
      if opt in ('-h','--help'):
         print('relay_test.py -r <relay GPIO ID> -o <on/off>')
         sys.exit()
      elif opt in ("-p", "--pin"):
         relayGPIO = int(arg)
      elif opt in ("-o", "--option"):
         if arg in ("on","ON"):
            mode = GPIO.LOW
         elif arg in ("off","OFF"):
            mode = GPIO.HIGH
         else:
            print("Invalid option, either 'on' or 'off' (without quotes)!")
            sys.exit(2)
      else:
         print("Invalid paramater passed, valid paramters are -o (option 'on'/'off') or -p (GPIO pin#)")
         sys.exit(2)

   if mode is None:
      print("Error! Option not defined, use '-o or '--option' to specify")
      sys.exit(2)
   if relayGPIO is None:
      print("Error! Relay pin not defined, use '-p' or '--pin' to specify")
      sys.exit(2)
   if relayGPIO not in [4,17,18,27,22,23,24,25,5,6,12,13,16,26]:
      print("Error, invalid GPIO pin# specified!")
      sys.exit(2)

   GPIO.setup(relayGPIO, GPIO.OUT)
   GPIO.output(relayGPIO, mode)
   if mode == GPIO.HIGH:
      GPIO.cleanup()

if __name__ == "__main__":
   try:
     main(sys.argv[1:])
   except Exception as e:
     print ("Exception!: "+str(e))
   finally:
#     GPIO.cleanup()
     sys.exit(0)
