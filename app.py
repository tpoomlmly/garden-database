from flask import Flask, render_template, send_from_directory
from flask_sslify import SSLify
import sqlite3
import os

app = Flask(__name__)
sslify = SSLify(app)
db = sqlite3.connect('garden.db')


@app.route("/")
def index():
    return render_template("website.html")


@app.route("/clients")
def clients():
    return render_template("clients.html")


@app.route("/plants")
def plants():
    return render_template("plants.html")


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/x-icon')


if __name__ == "__main__":
    context = ('server.crt', 'server.key')
    app.run(host='localhost', port='443', debug=False, ssl_context=context)
