import sqlite3
from datetime import datetime
#sensors(id $key, ip, room)
#measure(m_id $key,id $f_key, temp, hum, target,date)

class Sensor:
    def __init__(self, id=None, ip="", room="", isOn=True):
        self.id = id
        self.ip = ip
        self.room = room
        self.isOn = isOn

class Measurement:
    def __init__(self, m_id = None, sensor= None, temp = 0, hum = 0, target = 0, date = ""):
        self.m_id = m_id
        self.sensor = sensor
        self.temp = temp
        self.hum = hum
        self.target = target
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class Valve:
    def __init__(self,v_id = None, sensor=None, pin=None):
        self.v_id = v_id
        self.sensor = sensor
        self.pin = pin

class dbManager:
    def __init__(self):
        self.connection = sqlite3.connect("data.db", check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
    def getSensors(self):
        self.cursor.execute("SELECT * FROM sensors")
        return self.cursor.fetchall()
    def createSensor(self,sensor):
        self.cursor.execute("INSERT INTO sensors(ip, room,isOn) VALUES(?,?,?)",(sensor.ip,sensor.room,sensor.isOn))
        self.connection.commit()
        return
    def createMeasurement(self,sensor_ip, measurement):
        self.cursor.execute("INSERT INTO measurement(s_id,temp,target_temp,humidity, date) VALUES(?,?,?,?,?)",
        (
            sensor_ip,
            measurement.temp,
            measurement.target,
            measurement.hum,
            measurement.date
        ))
        self.connection.commit()
        self.SensorOn(sensor_ip)
        return
    def getMeasurement(self):
        self.cursor.execute("SELECT * FROM measurement")
        return self.cursor.fetchall()
    #get last ... measured temperatures from sensors that are online
    def getRecentTemps(self, top=3):
        query = """
            SELECT m1.m_id, m1.s_id, m1.temp, m1.target_temp, m1.humidity, m1.date
            FROM measurement m1
            WHERE (
                SELECT COUNT(*)
                FROM measurement m2
                WHERE m2.s_id = m1.s_id
                AND m2.date > m1.date
            ) < ?
            ORDER BY m1.s_id, m1.date DESC;
        """
        self.cursor.execute(query, (top,))
        rows = self.cursor.fetchall()
        sensors = {s["ip"]: s["room"] for s in self.getSensors() if s["isOn"]}
        data_map = {}
        for row in rows:
            m_id, s_id, temp, target_temp, humidity, date = row
            if s_id in sensors:
                if sensors[s_id] not in data_map:
                    data_map[sensors[s_id]] = []
                data_map[sensors[s_id]].append({
                    'temp': temp,
                    'target_temp': target_temp,
                    'humidity': humidity,
                    'date': date
                })

        return data_map
    def SensorOn(self,sensor):
        self.cursor.execute("UPDATE sensors SET isOn = true WHERE ip = ?",(sensor,))
        self.connection.commit()
        return
    def SensorOff(self,sensor):
        self.cursor.execute("UPDATE sensors SET isOn = false WHERE ip = ?",(sensor,))
        self.connection.commit()
        return
    def getValves(self):
        self.cursor.execute("SELECT * FROM valves")
        return self.cursor.fetchall()
    def createValve(self,valve):
        self.cursor.execute("INSERT INTO valves(s_id, pin) VALUES(?,?)",(valve.sensor,valve.pin))
        self.connection.commit()
        return
    def UpdateWaterTemp(self,temp):
        self.cursor.execute("UPDATE config SET waterTemp = ? ",(temp,))
        self.connection.commit()
    def GetWaterTemp(self):
        self.cursor.execute("SELECT waterTemp FROM config")
        return self.cursor.fetchone()
    def changeSensorName(self,sensor,name):
        self.cursor.execute("UPDATE sensors SET room = ? WHERE id = ?",(name,sensor))
        self.connection.commit()
    def GetTimings(self):
        self.cursor.execute("SELECT timing1,timing2,timing3 from config")
        return self.cursor.fetchall()
    def UpdateTimings(self, new):
        #new - tuple, -1 means no change
        if new[0] != -1:
            self.cursor.execute("UPDATE config SET timing1 = ? ",(new[0],))
            self.connection.commit()
        if new[1] != -1:
            self.cursor.execute("UPDATE config SET timing2 = ? ",(new[1],))
            self.connection.commit()
        if new[2] != -1:
            self.cursor.execute("UPDATE config SET timing3 = ? ",(new[2],))
            self.connection.commit()
    def connectSensorToValve(self,sensor,valve):
        self.cursor.execute("UPDATE valves SET s_id = ? WHERE v_id = ?",(sensor,valve))
        self.connection.commit()