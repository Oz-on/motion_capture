# Code that deals with 10 gyroscope sensors, and sends rotation from them to pc

import threading
import smbus
import math
from udp import sendData

power_mgmt_1 = 0x6b
bus = smbus.SMBus(1) # bus = smbus.SMBus(0) fuer Revision 1
addresses = [0x68, 0, 0, 0, 0, 0, 0, 0, 0, 0]

def dist(a, b):
  return math.sqrt((a*a)+(b*b))

def get_y_rotation(x,y,z):
  radians = math.atan2(x, dist(y,z))
  return -math.degrees(radians)

def get_x_rotation(x,y,z):
  radians = math.atan2(y, dist(x,z))
  return math.degrees(radians)

def get_z_rotation(z):
  radians = math.acos(z, 9.80665)
  return math.degrees(radians)

class SensorHandler(threading.Thread):
  def __init__(self, address, id):
    threading.Thread.__init__(self)
    self.address = address
    self.id = id

  def read_word(self, reg):
    h = bus.read_byte_data(self.address, reg)
    l = bus.read_byte_data(self.address, reg+1)
    value = (h << 8) + l
    return value

  def read_word_2c(self, reg):
    val = self.read_word(reg)
    if val >= 0x8000:
      return -((65535 - val) + 1)
    else:
      return val

  def run(self):
    scale = 16384.0
    bus.write_byte_data(self.address, power_mgmt_1, 0)
    while True:
      acceleration_xout_scaled = self.read_word_2c(0x3b) / scale
      acceleration_yout_scaled = self.read_word_2c(0x3d) / scale
      acceleration_zout_scaled = self.read_word_2c(0x3f) / scale
      x_rotation = get_x_rotation(acceleration_xout_scaled, acceleration_yout_scaled, acceleration_zout_scaled)
      y_rotation = get_y_rotation(acceleration_xout_scaled, acceleration_yout_scaled, acceleration_zout_scaled)
      z_rotation = get_z_rotation(acceleration_zout_scaled)
      sendData({
        "id": self.id,
        "x": x_rotation,
        "y": y_rotation,
        "z": z_rotation,
      })


for id in range(len(addresses)):
  worker = SensorHandler(addresses[id], id)
  worker.start()
