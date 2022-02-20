from pyfirmata import Arduino, util
from time import sleep

board = Arduino('/dev/ttyUSB0')

loop = util.Iterator(board)
loop.start()
board.analog[0].enable_reporting()

while True:
    value = board.analog[0].read()
    print(value)