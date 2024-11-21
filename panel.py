from flask import Flask, flash, render_template,jsonify,request,redirect,url_for
from waitress import serve

from dbManager import dbManager

app = Flask(__name__)
db = dbManager()
#main page with links to other stuff
#settings page to change timings
#connect page to connect sensor with valve
@app.route("/")
def index():
    return render_template("index.html",water=db.GetWaterTemp()[0])
@app.route('/display')
def display():
    data = db.getMeasurement()
    sensor = {c[1]:c[2] for c in db.getSensors()}
    return render_template('display.html', data=data, sensor=sensor)
@app.route("/recent")
def recent():
    return render_template("recent.html",data=db.getRecentTemps())
@app.route("/sensors")
def sensors():
    sensors = [(s["id"],s["ip"],s["room"]) for s in db.getSensors()]
    return render_template("sensors.html",sensors=sensors)
@app.route("/sensor/<int:id>",methods=["GET","POST"])
def sensor(id):
    valves = db.getValves()
    connections = {v["s_id"]:v["v_id"] for v in valves}
    sensor = ((row["id"],row["ip"],row["room"],row["isOn"]) for row in db.getSensors() if row["id"]==id)
    if request.method == "POST":
        new_name = request.form.get("sensor_name","").strip()
        valve = request.form.get("valveSelect", None)
        a = list(sensor)
        if new_name:
            print(new_name)
            db.changeSensorName(a[0][0], new_name)
        if valve and valve != "---":
            print(valve)
            db.connectSensorToValve(a[0][0], valve)
        return redirect("/sensors")
        
    return render_template("sensor.html",sensor=sensor,valves=valves,connections=connections)

app.run(debug=True)
#serve(app, host='0.0.0.0', port=8080)