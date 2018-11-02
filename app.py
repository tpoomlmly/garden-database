from flask import Flask, render_template, send_from_directory, request, redirect, url_for
from flask_sslify import SSLify
import util
import dbc
import os

# TODO use flash() to add invalid form detection including non-unique latin names and invalid months
app = Flask(__name__)
sslify = SSLify(app=app, permanent=True)
months = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


@app.route("/")
def index():
    return redirect(url_for("clients"))


@app.route("/clients", methods=["GET", "POST"])
def clients():
    # TODO add plant linking support to the form and backend
    with dbc.DBConnection() as c:
        if request.method == "POST":
            pids_to_link = [field[6:] for field in request.form.keys() if field[:5] == "plant"]
            if "delete" in request.form:
                c.drop_client(request.form["id"])

            elif "add" in request.form:
                client = dbc.Client(request.form["name"], plants=pids_to_link)
                client.insert()

            elif "edit" in request.form:
                client = dbc.Client(request.form["name"], cid=request.form["id"], plants=pids_to_link)
                client.update()

        return render_template("clients.html", data=c.load_sql_client_data(),
                               plant_list=c.load_sql_plant_data(), months=months)


@app.route("/plants", methods=["GET", "POST"])
def plants():
    # TODO add sensible way to handle blooming period (perhaps month selection again?)
    with dbc.DBConnection() as c:
        if request.method == "POST":
            mids_to_link = [field[4:] for field in request.form.keys() if field[:3] == "job"]
            if "delete" in request.form:
                c.drop_plant(request.form["id"])

            elif "add" in request.form:
                plant = dbc.Plant(request.form["name"], request.form["latin-name"],
                                  request.form["blooming-period"], jobs=mids_to_link)
                plant.insert()

            elif "edit" in request.form:
                plant = dbc.Plant(request.form["name"], request.form["latin-name"],
                                  request.form["blooming-period"], pid=request.form["id"],
                                  jobs=mids_to_link)
                plant.update()
        return render_template("plants.html", data=c.load_sql_plant_data(),
                               job_list=c.load_sql_job_data())


@app.route("/maintenance", methods=["GET", "POST"])
def jobs():
    with dbc.DBConnection() as c:
        if request.method == "POST":
            if "delete" in request.form:
                c.drop_job(request.form["id"])

            elif "add" in request.form:
                # & is the intersection operator. set() converts the dict_keyiterator and list to sets so that the
                # intersection can be found of them. list() converts this back to a list which is sorted on the
                # basis that each item in the new list is the name of a month.
                active_months = sorted(list(set(request.form) & set(months)), key=util.dt_from_month)
                job = dbc.Maintenance(request.form["name"],
                                      request.form["desc"],
                                      active_months)
                job.insert()

            elif "edit" in request.form:
                active_months = sorted(list(set(request.form) & set(months)), key=util.dt_from_month)
                job = dbc.Maintenance(request.form["name"],
                                      request.form["desc"],
                                      active_months,
                                      request.form["id"])
                job.update()
        return render_template("maintenance.html", data=c.load_sql_job_data(), month_list=months)


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/x-icon')


if __name__ == "__main__":
    context = ('server.crt', 'server.key')
    app.secret_key = "Ye to misery wisdom plenty polite to as."
    app.run(host='0.0.0.0', port=443, debug=False, ssl_context=context)
