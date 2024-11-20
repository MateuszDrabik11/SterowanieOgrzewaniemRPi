from gpiozero import PWMLED
import socket
import netifaces
import time
import nmap


class Connector:
    def __init__(self):
        self.led = PWMLED(pin=12,frequency=1)

    def startAp(self):
        #todo
        return

    def waitForConnection(self):
        self.led.value = 0.5
        self.startAp()
        while not self.isConnected():
            time.sleep(5)
        self.led.value = 1
        return

    def isConnected(self):
        gateWayAddress = netifaces.gateways().get("default",{}).get(netifaces.AF_INET, [None])[0]
        if not gateWayAddress:
            return False
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect((gateWayAddress, 80))
                s.close()
                return True
        except (socket.timeout, socket.error):
            s.close()
            return False
    
    def scanLan(self):
        sensors = {}
        nm = nmap.PortScanner()
        nm.scan("192.168.0.0/24","3000","-sT")
        for host in nm.all_hosts():
            if nm[host]["tcp"][3000]["state"] == "open":
                sensors[host] = host
        return sensors