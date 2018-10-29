from flask import Flask, render_template, send_from_directory, request, redirect, url_for
from flask_sslify import SSLify
from datetime import datetime as dt
import dbc
import os

# TODO use flash() to add invalid form detection including non-unique latin names
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
    if request.method == "POST":
        if "delete" in request.form:
            dbc.drop_client(request.form["id"])
        elif "add" in request.form:
            client = dbc.Client(request.form["name"])
            dbc.insert_client(client)
        elif "edit" in request.form:
            client = dbc.Client(request.form["name"], request.form["id"])
            dbc.update_client(client)
    return render_template("clients.html", data=dbc.load_sql_client_data(),
                           plant_list=[{"id": plant.id, "name": plant.name} for plant in dbc.load_sql_plant_data()])


@app.route("/plants", methods=["GET", "POST"])
def plants():
    # TODO add maintenance linking support to the form and backend
    # TODO add sensible way to handle blooming period (perhaps month selection again?)
    if request.method == "POST":
        print(request.form)
        mids_to_link = [field[4:] for field in request.form.keys() if field[:2] == "job"]
        if "delete" in request.form:
            dbc.drop_plant(request.form["id"])

        elif "add" in request.form:
            plant = dbc.Plant(request.form["name"],
                              request.form["latin-name"],
                              request.form["blooming-period"],
                              jobs=jobs_to_link)
            dbc.insert_plant(plant)

        elif "edit" in request.form:
            plant = dbc.Plant(request.form["name"],
                              request.form["latin-name"],
                              request.form["blooming-period"],
                              pid=request.form["id"],
                              jobs=mids_to_link)
            dbc.update_plant(plant)

    return render_template("plants.html", data=dbc.load_sql_plant_data(),
                           job_list=[{"id": job.id, "name": job.name} for job in dbc.load_sql_job_data()])


@app.route("/maintenance", methods=["GET", "POST"])
def jobs():
    if request.method == "POST":
        if "delete" in request.form:
            dbc.drop_job(request.form["id"])
        elif "add" in request.form:
            # & is the intersection operator. set() converts the dict_keyiterator and list to sets so that the
            # intersection can be found of them. list() converts this back to a list which is sorted on the basis that
            # each item in the new list is the name of a month.
            active_months = sorted(list(set(request.form) & set(months)), key=dt_from_month)
            job = dbc.Maintenance(request.form["name"],
                                  request.form["desc"],
                                  active_months)
            dbc.insert_job(job)
        elif "edit" in request.form:
            active_months = sorted(list(set(request.form) & set(months)), key=dt_from_month)
            job = dbc.Maintenance(request.form["name"],
                                  request.form["desc"],
                                  active_months,
                                  request.form["id"])
            dbc.update_job(job)
    return render_template("maintenance.html", data=dbc.load_sql_job_data(), month_list=months)


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/x-icon')


def dt_from_month(month):
    """Converts the name of a month to a sortable datetime object.

    Only works in english countries.
    """
    return dt.strptime(month, '%B')


if __name__ == "__main__":
    context = ('server.crt', 'server.key')
    app.secret_key = "Ye to misery wisdom plenty polite to as."
    app.run(host='0.0.0.0', port=443, debug=False, ssl_context=context)
