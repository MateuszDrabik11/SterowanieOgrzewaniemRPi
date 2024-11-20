import sqlite3
from datetime import datetime
#sensors(id $key, ip, room)
#measure(m_id $key,id $f_key, temp, hum, target,date)

class Sensor:
    def __init__(self, id=None, ip="", room=""):
        self.id = id
        self.ip = ip
        self.room = room

class Measurement:
    def __init__(self, m_id = None, sensor= "", temp = 0, hum = 0, target = 0, date = ""):
        self.m_id = m_id
        self.sensor = sensor
        self.temp = temp
        self.hum = hum
        self.target = target
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class dbManager:
    def __init__(self):
        self.connection = sqlite3.connect("data.db", check_same_thread=False)
        self.cursor = self.connection.cursor()
    def getSensors(self):
        self.cursor.execute("SELECT * FROM sensors")
        return self.cursor.fetchall()
    def createSensor(self,sensor):
        self.cursor.execute("INSERT INTO sensors(ip, room) VALUES(?,?)",(sensor.ip,sensor.room))
        self.connection.commit()
    def createMeasurement(self,sensor, measurement):
        self.cursor.execute("INSERT INTO measurement(s_id,temp,target_temp,humidity, date) VALUES(?,?,?,?,?)",
        (
            sensor,
            measurement.temp,
            measurement.target,
            measurement.hum,
            measurement.date
        ))
        self.connection.commit()
    def getMeasurement(self):
        self.cursor.execute("SELECT * FROM measurement")
        return self.cursor.fetchall()

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
        data_map = {}
        for row in rows:
            m_id, s_id, temp, target_temp, humidity, date = row
            if s_id not in data_map:
                data_map[s_id] = []
            data_map[s_id].append({
                'm_id': m_id,
                'temp': temp,
                'target_temp': target_temp,
                'humidity': humidity,
                'date': date
            })

        return data_map