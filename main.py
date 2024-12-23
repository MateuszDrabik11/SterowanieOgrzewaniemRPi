from connect import Connector
from dbManager import dbManager, Sensor,Measurement
import threading
import requests
import time
import statistics
from gpiozero import LED,MCP3008

def updateSensors(connector,dbManager):
    sensors = connector.GetDataFromSensors()
    dbSensors = dbManager.getSensors()
    dpIp = [s["ip"] for s in dbSensors]
    for (ip, port), data in sensors.items():
        if ip not in dpIp:
            s = Sensor(ip=ip,room=ip)
            dbManager.createSensor(s)
    return sensors

def SensorHandler(sensors):
    dbMan = dbManager()
    timing = dbMan.GetTimings()[0][0]
    while True:
        connector = Connector()
        sensors = updateSensors(connector,dbMan)
        for ip,val in sensors.items():
            try:
                m = Measurement(temp = val["current_temperature"],target = val["target_temperature"],hum = val["humidity"])
                if m.temp <= 0.0 and m.hum <= 0.0:
                    continue
                dbMan.createMeasurement(ip[0],m)
            except requests.exceptions.RequestException as e:
                print(f"{ip[0]} off")
                db.SensorOff(ip[0])
                sensors.remove(ip)
                continue
        time.sleep(timing)

def ValveHandler():
    db = dbManager()
    valves = db.getValves()
    sensors = {s['id']:s['room'] for s in db.getSensors()}
    pins = {v['pin']:(LED(v['pin']),LED(v['led'])) for v in valves}
    timing = db.GetTimings()[0][2]
    while True:
        temps = db.getRecentTemps()
        for valve in valves:
            avgTemp = 0.0
            lastTargetTemp = 25.0
            try:
                sensorTemps = [t['temp'] for t in temps[sensors[valve['s_id']]]]
                avgTemp = statistics.mean(sensorTemps)
                lastTargetTemp = temps[sensors[valve['s_id']]][0]['target_temp']
                print(f"{valve['v_id']}:avg={avgTemp},target={lastTargetTemp}")
            except:
                avgTemp, lastTargetTemp = db.getLastTemp()
                print(f"{valve['v_id']}:avg={avgTemp},target={lastTargetTemp}")
            if avgTemp < lastTargetTemp:
                pins[valve['pin']][0].on()
                pins[valve['pin']][1].on()
            else:
                pins[valve['pin']][0].off()
                pins[valve['pin']][1].off()
        time.sleep(timing)

def HeaterHandler():
    waterSensor = MCP3008(0)
    furnace = LED(16)
    furnaceLed = LED(12)
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
            furnaceLed.on()
        else:
            furnace.off()
            furnaceLed.off()
        db.UpdateWaterTemp(temperature(waterSensor.value))
        time.sleep(timing)

connector = Connector()

led=LED(14)
led.off()

connector.waitForConnection()

led.on()
db = dbManager()

sensors = updateSensors(connector,db)

#t1:    request data from sensors, current_temp,target_temp, store in db

t1 = threading.Thread(target=SensorHandler, args = (sensors,))
t1.start()

#t2:    check water temp
#       if water_temp < 50 -> furnace on, triger relay

t2 = threading.Thread(target=HeaterHandler)
t2.start()

#t3:    check 
#       for device:
#           if device.current_temp < device.target_temp -> valve on

t3 = threading.Thread(target=ValveHandler)
t3.start()
