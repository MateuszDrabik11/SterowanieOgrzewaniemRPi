import re
from gpiozero import LED
import socket
import json
import time
import ipaddress

class Connector:
    def get_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            s.connect(('10.254.254.254', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP
    
    def GetDataFromSensors(self):
        sensorData = {}
        ip = str(ipaddress.IPv4Network(f"{self.get_ip()}/24",strict=False).broadcast_address)
        addr = ("0.0.0.0",5000)
        target = (ip,3000)
        message = "aaaa".encode()
        s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind(addr)
        s.settimeout(0.9)
        for _ in range(8):
            try:
                s.sendto(message, target)
                data, add = s.recvfrom(1024)
                sensorData[add] = json.loads(data.decode().rstrip('\x00'))
                break
            except socket.timeout:
                print("no response")
        return sensorData

    def waitForConnection(self):
        while not self.isConnected():
            time.sleep(5)
        return

    def isConnected(self):
        return self.get_ip() != "127.0.0.1"
