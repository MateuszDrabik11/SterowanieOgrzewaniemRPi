from connect import Connector
from dbManager import dbManager, Sensor,Measurement
import threading
import requests
import time
import statistics
from gpiozero import LED,MCP3008

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

def SensorHandler(sensors):
    dbMan = dbManager()
    sensorsToCheck = [s for s in sensors]
    timing = dbMan.GetTimings()[0][0]
    while True:
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
        time.sleep(timing)

def ValveHandler():
    db = dbManager()
    valves = db.getValves()
    sensors = {s['id']:s['room'] for s in db.getSensors()}
    pins = {v['pin']:LED(v['pin']) for v in valves}
    timing = db.GetTimings()[0][2]
    while True:
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
        time.sleep(timing)

def HeaterHandler():
    waterSensor = MCP3008(0)
    furnace = LED(14)
    db = dbManager()
    timing = db.GetTimings()[0][1]
    #0.0, 0V -> -40 C
    #1.0, 3.3V -> 120 C
    #y[C], x[1]
    #y=ax-40
    #120=a-40
    #a=160
    #50=160x-40
    #x=90/160=9/16
    #x=0.5625
    temperature = lambda x: 160*x - 40
    while True:
        if waterSensor.value < 0.5625:
            furnace.on()
        else:
            furnace.off()
        db.UpdateWaterTemp(temperature(waterSensor.value))
        time.sleep(timing)

connector = Connector()

connector.waitForConnection()

db = dbManager()

sensors = updateSensors(connector,db)

#t1:    every minute request data from sensors, current_temp,target_temp, store in db

t1 = threading.Thread(target=SensorHandler, args = (sensors,))
t1.start()

#t2:    every 15 minutes check water temp
#       if water_temp < 50 -> furnace on, triger relay

t2 = threading.Thread(target=HeaterHandler)
t2.start()

#t3:    every 15 minutes check 
#       for device:
#           if device.current_temp < device.target_temp -> valve on

t3 = threading.Thread(target=ValveHandler)
t3.start()


#separe process:    host panel
#       - map ip of device to the valve
#       - display data
#       
