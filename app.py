from flask import Flask, render_template, send_from_directory, request, redirect, url_for
from flask_sslify import SSLify
import dbc
import os

app = Flask(__name__)
sslify = SSLify(app=app, permanent=True)
months = {"jan": "January", "feb": "February", "mar": "March", "apr": "April",
          "may": "May", "jun": "June", "jul": "July", "aug": "August",
          "sep": "September", "oct": "October", "nov": "November", "dec": "December"}


@app.route("/")
def index():
    return redirect(url_for("clients"))


@app.route("/clients", methods=["GET", "POST"])
def clients():
    # TODO add plant linking support to the form and backend
    if request.method == "POST":
        client = dbc.Client(request.form["name"])
        dbc.insert_client(client)
    return render_template("clients.html")


@app.route("/plants", methods=["GET", "POST"])
def plants():
    # TODO add maintenance linking support to the form and backend
    # TODO add sensible way to handle blooming period (perhaps month selection again?)
    if request.method == "POST":
        plant = dbc.Plant(request.form["name"],
                          request.form["latin-name"],
                          request.form["blooming-period"])
        dbc.insert_plant(plant)
    return render_template("plants.html")


@app.route("/maintenance", methods=["GET", "POST"])
def jobs():
    if request.method == "POST":
        # & is the intersection operator. keys() creates a set out of the keys in each dictionary, then '&'
        # is used to select only they keys that the dictionaries have in common.
        active_months = ",".join(request.form.keys() & months.keys())
        job = dbc.Maintenance(request.form["name"],
                              request.form["desc"],
                              active_months)
        dbc.insert_job(job)
    return render_template("maintenance.html", month_dict=months)


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/x-icon')


if __name__ == "__main__":
    context = ('server.crt', 'server.key')
    app.secret_key = "Ye to misery wisdom plenty polite to as."
    app.run(host='0.0.0.0', port=443, debug=False, ssl_context=context)
