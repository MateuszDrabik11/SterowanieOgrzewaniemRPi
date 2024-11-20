# Complete Project Details: https://RandomNerdTutorials.com/raspberry-pi-analog-inputs-python-mcp3008/

from gpiozero import PWMLED, MCP3008,LED
from time import sleep
from flask import Flask,render_template,request


#create an object called pot that refers to MCP3008 channel 0
pot = MCP3008(0)
#create a PWMLED object called led that refers to GPIO 14
led = PWMLED(pin=12,frequency=60)

app = Flask(__name__)

@app.route("/")
def index():
    """Main page showing the LED controls."""
    return render_template("index.html")
@app.route("/get-value")
def getValue():
    led.value = pot.value
    return {"value":pot.value}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
