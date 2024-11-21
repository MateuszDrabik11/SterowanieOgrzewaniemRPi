from connect import Connector
from dbManager import dbManager, Sensor,Measurement
import threading
import requests
import time
import statistics
from gpiozero import LED

def updateSensors(connector,dbManager):
    sensors = connector.scanLan()
    dbSensors = dbManager.getSensors()
    dbSet = {dbSensor[1] for dbSensor in dbSensors}
    for sensor in sensors:
        if sensor not in dbSet:
            dbManager.createSensor(Sensor(ip=sensor,room=sensors[sensor]))
        dbManager.SensorOn(sensor)
    dbSensors = dbManager.getSensors()
    sensors = {dbSensor["ip"]:dbSensor["room"] for dbSensor in dbSensors}
    print(sensors)
    return sensors

def SensorHandler(sensors,stop_event):
    dbMan = dbManager()
    sensorsToCheck = [s for s in sensors]
    while not stop_event.is_set():
        if len(sensorsToCheck) == 0:
            connector = Connector()
            sensors = updateSensors(connector,dbMan)
            sensorsToCheck = [s for s in sensors]
        for ip in sensorsToCheck:
            try:
                r = requests.get("http://" + ip + ":3000/",timeout=5)
                if r.status_code == 200:
                    result = r.json()
                    print(result)
                    m = Measurement(temp = result["current_temperature"],target = result["target_temperature"],hum = result["humidity"])
                    if m.temp == 0.0 and m.hum == 0.0:
                        continue
                    dbMan.createMeasurement(ip,m)
            except requests.exceptions.RequestException as e:
                print(f"{ip} off")
                db.SensorOff(ip)
                sensorsToCheck.remove(ip)
                continue
        time.sleep(5)

def ValveHandler(stop_event):
    db = dbManager()
    valves = db.getValves()
    sensors = {s['id']:s['room'] for s in db.getSensors()}
    pins = {v['pin']:LED(v['pin']) for v in valves}
    while not stop_event.is_set():
        temps = db.getRecentTemps()
        for valve in valves:
            sensorTemps = [t['temp'] for t in temps[sensors[valve['s_id']]]]
            avgTemp = statistics.mean(sensorTemps)
            lastTargetTemp = temps[sensors[valve['s_id']]][0]['target_temp']
            print(f"{valve['v_id']}:avg={avgTemp},target={lastTargetTemp}")
            if avgTemp < lastTargetTemp:
                pins[valve['pin']].on()
            else:
                pins[valve['pin']].off()
        time.sleep(5)



connector = Connector()
#turn on ap with panel to login to network

#connector.initDiode()

#wait for connection, wifi or ethernet

connector.waitForConnection()

#if connected light diode
#if ap on blink diode




#when connected

#scan for device on port 3000

db = dbManager()

sensors = updateSensors(connector,db)

#t1:    every minute request data from sensors, current_temp,target_temp, store in db

stop_event1 = threading.Event()
stop_event3 = threading.Event()
t1 = threading.Thread(target=SensorHandler, args = (sensors,stop_event1))
t1.start()

t3 = threading.Thread(target=ValveHandler, args=(stop_event3,))
t3.start()

#t2:    every 15 minutes check water temp
#       if water_temp < 50 -> furnace on, triger relay

#t3:    every 15 minutes check 
#       for device:
#           if device.current_temp < device.target_temp -> valve on

#separe process:    host panel
#       - map ip of device to the valve
#       - display data
#       
