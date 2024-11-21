from flask import Flask, render_template,jsonify
from waitress import serve

from dbManager import dbManager

app = Flask(__name__)
db = dbManager()

#main page with links to other stuff
#settings page to change timings
#connect page to connect sensor with valve

@app.route('/display')
def index():
    data = db.getMeasurement()
    sensor = {c[1]:c[2] for c in db.getSensors()}
    return render_template('display.html', data=data, sensor=sensor)
@app.route("/recent")
def recent():
    return render_template("recent.html",data=db.getRecentTemps())
@app.route("/sensors")
def sensors():
    sensors = db.getSensors()
    valves = db.getValves()
    return render_template("sensors.html",sensors=sensors,valves=valves)

app.run(debug=True)
#serve(app, host='0.0.0.0', port=8080)