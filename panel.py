from flask import Flask, render_template,jsonify
from waitress import serve

from dbManager import dbManager

app = Flask(__name__)
db = dbManager()

@app.route('/')
def index():
    data = db.getMeasurement()
    sensor = {c[1]:c[2] for c in db.getSensors()}
    return render_template('index.html', data=data, sensor=sensor)
@app.route("/recent")
def recent():
    return render_template("recent.html",data=db.getRecentTemps())

#app.run(debug=True)
serve(app, host='0.0.0.0', port=8080)