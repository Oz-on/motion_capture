import threading
import smbus
import math
from udp import sendData

bus = smbus.SMBus(1)
addresses = [0x53]

class SensorHandler(threading.Thread):
  def __init__(self, address, id):
    threading.Thread.__init__(self)
    self.address = address
    self.id = id

  def get_acc(self, reg):
    h = bus.read_byte_data(self.address, reg)
    l = bus.read_byte_data(self.address, reg+1)

    accl = ((l & 0x03) * 256) + h
    if accl > 511:
	    accl -= 1024

    normlized_accl = accl * 0.004 * 9.80665
    return normlized_accl

  def lowPassFilter(self, acc):
    alpha = 0.5
    return acc * alpha + ((acc * 1) - alpha)

  def dist(self, a, b):
    return math.sqrt((a*a)+(b*b))

  def get_y_rotation(self, x, y, z):
    radians = math.atan2(y, self.dist(y, z))
    return -math.degrees(radians)
  
  def get_x_rotation(self, x, y, z):
    radians = math.atan2(y, self.dist(x, z))
    return math.degrees(radians)

  def run(self):
    # bandwidth rate register
    bus.write_byte_data(self.address, 0x2C, 0x0A)
    # power control register
    bus.write_byte_data(self.address, 0x2D, 0x08)
    # format register
    bus.write_byte_data(self.address, 0x31, 0x08)

    x_accl = self.get_acc(0x32)
    y_accl = self.get_acc(0x34)
    z_accl = self.get_acc(0x36)

    filtered_x_accl = self.lowPassFilter(x_accl)
    filtered_y_accl = self.lowPassFilter(y_accl)
    filtered_z_accl = self.lowPassFilter(z_accl)

    x_rotation = self.get_x_rotation(filtered_x_accl, filtered_y_accl, filtered_z_accl)
    
    y_rotation = self.get_x_rotation(filtered_x_accl, filtered_y_accl, filtered_z_accl)

    sendData({
      "id": self.id,
      "x": x_rotation,
      "y": y_rotation,
      "z": z_accl,
    })

    for id in range(len(addresses)):
      worker = SensorHandler(addresses[id], id)
      worker.start()