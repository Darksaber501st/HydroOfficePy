# -*- coding: utf-8 -*

import time
import smbus
import os
           
ADDRESS_0                 = 0x70
ADDRESS_1                 = 0x71
ADDRESS_2                 = 0x72
ADDRESS_3                 = 0x73
OXYGEN_DATA_REGISTER      = 0x03
USER_SET_REGISTER         = 0x08
AUTUAL_SET_REGISTER       = 0x09
GET_KEY_REGISTER          = 0x0A

class DFRobot_Oxygen(object):
  ## oxygen key value
  __key      = 0.0
  __count    = 0
  __txbuf      = [0]
  __oxygendata = [0]*101
  def __init__(self, bus):
    self.i2cbus = smbus.SMBus(bus)

  def get_flash(self):
    rslt = self.read_reg(GET_KEY_REGISTER, 1)
    if rslt == 0:
      self.__key = (20.9 / 120.0)
    else:
      self.__key = (float(rslt[0]) / 1000.0)
    time.sleep(0.1)
  
  def calibrate(self, vol, mv):
    self.__txbuf[0] = int(vol * 10)
    if (mv < 0.000001) and (mv > (-0.000001)):
      self.write_reg(USER_SET_REGISTER, self.__txbuf)
    else:
      self.__txbuf[0] = int((vol / mv) * 1000)
      self.write_reg(AUTUAL_SET_REGISTER, self.__txbuf)

  def get_oxygen_data(self, collect_num):
    self.get_flash()
    if collect_num > 0:
      for num in range(collect_num, 1, -1):
        self.__oxygendata[num-1] = self.__oxygendata[num-2]
      rslt = self.read_reg(OXYGEN_DATA_REGISTER, 3)
      self.__oxygendata[0] = self.__key * (float(rslt[0]) + float(rslt[1]) / 10.0 + float(rslt[2]) / 100.0)
      if self.__count < collect_num:
        self.__count += 1
      return self.get_average_num(self.__oxygendata, self.__count)
    elif (collect_num > 100) or (collect_num <= 0):
      return -1

  def get_average_num(self, barry, Len):
    temp = 0.0
    for num in range (0, Len):
      temp += barry[num]
    return (temp / float(Len))

class DFRobot_Oxygen_IIC(DFRobot_Oxygen): 
  def __init__(self, bus, addr):
    self.__addr = addr
    super(DFRobot_Oxygen_IIC, self).__init__(bus)

  def write_reg(self, reg, data):
    self.i2cbus.write_i2c_block_data(self.__addr, reg, data)

  def read_reg(self, reg, len):
    while 1:
      try:
        rslt = self.i2cbus.read_i2c_block_data(self.__addr, reg, len)
        return rslt
      except:
        os.system('i2cdetect -y 1')
        time.sleep(1)

COLLECT_NUMBER   = 10              # collect number, the collection range is 1-100
IIC_MODE         = 0x01            # default use IIC1
oxygen = DFRobot_Oxygen_IIC(IIC_MODE ,ADDRESS_3)
def loop():
  oxygen_data = oxygen.get_oxygen_data(COLLECT_NUMBER)
  print("oxygen concentration is %4.2f %%vol"%oxygen_data)
  time.sleep(1)

if __name__ == "__main__":
  while True:
    loop()
