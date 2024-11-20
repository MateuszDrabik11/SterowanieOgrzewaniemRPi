from connect import Connector
from dbManager import dbManager, Sensor,Measurement
import threading
import requests
import time

def SensorHandler(sensors,stop_event):
    dbMan = dbManager()
    while not stop_event.is_set():
        for ip,name in sensors.items():
            try:
                r = requests.get("http://" + ip + ":3000/")
                if r.status_code == 200:
                    result = r.json()
                    m = Measurement(temp = result["current_temperature"],target = result["target_temperature"],hum = result["humidity"])
                    dbMan.createMeasurement(sensor,m)
            except requests.exceptions.RequestException as e:
                continue
        time.sleep(60)


#turn on ap with panel to login to network

#wait for connection, wifi or ethernet

#if connected light diode
#if ap on blink diode

connector = Connector()
connector.waitForConnection()



#when connected

#scan for device on port 3000

sensors = connector.scanLan()

db = dbManager()

dbSensors = db.getSensors()

dbSet = {dbSensor[1] for dbSensor in dbSensors}

for sensor in sensors:
    if sensor not in dbSet:
        db.createSensor(Sensor(ip=sensor,room=sensors[sensor]))

dbSensors = db.getSensors()

sensors = {dbSensor[1]:dbSensor[2] for dbSensor in dbSensors}

stop_event = threading.Event()
t1 = threading.Thread(target=SensorHandler, args = (sensors,stop_event))
t1.start()

#t1:    every minute request data from sensors, current_temp,target_temp, store in db

#t2:    every 5 minutes check water temp
#       if water_temp < max(target_temp) + 10 -> furnace on, triger relay

#t3:    every 5 minutes check 
#       for device:
#           if device.current_temp < device.target_temp -> valve on

#t4:    host panel
#       - map ip of device to the valve
#       - display data
#       
