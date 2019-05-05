import socket
import json

UDP_IP = '192.168.137.125'
UDP_PORT = 45454

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def sendData(data):
  jsonData = json.dumps(data)
  sock.sendto(bytes(jsonData, "utf-8"), (UDP_IP, UDP_PORT))