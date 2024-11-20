from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('data.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    data = conn.execute('SELECT * FROM measurement').fetchall()
    sensor = {c[1]:c[2] for c in conn.execute('SELECT * FROM sensors').fetchall()}
    conn.close()
    return render_template('index.html', data=data, sensor=sensor)

if __name__ == '__main__':
    app.run()