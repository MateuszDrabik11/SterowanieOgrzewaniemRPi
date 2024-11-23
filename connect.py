from gpiozero import LED
import socket
import netifaces
import time
import nmap


class Connector:
    def __init__(self):
        self.led = LED(14)

    def waitForConnection(self):
        self.led.off()
        while not self.isConnected():
            time.sleep(5)
        self.led.on()
        self.led.close()
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