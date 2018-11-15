import dbc
import os

from flask import Flask, render_template, send_from_directory, request, redirect, url_for

import sorting

app = Flask(__name__)
# A necessary list of all the months.
months = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


@app.route("/")
def index():
    """Redirect all requests for '/' to the clients page"""
    return redirect(url_for("clients"))


@app.route("/clients", methods=["GET", "POST"])
def clients():
    """Handle requests for the clients page.

    If the request is a POST request, execute the action specified by
    the browser in the form.
    Return clients.html, rendered with the client, plant and month data inserted.
    """
    with dbc.DBConnection() as c:
        if request.method == "POST":
            # In the form, the browser may send a list of plant IDs to link. They arrive as form fields
            # with names like 'plant-n' where n is the ID of a plant to link.
            # For every form field, check if the 1st 5 characters are 'plant'. If so, then extract the plant id.
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
    with dbc.DBConnection() as c:
        if request.method == "POST":
            mids_to_link = [field[4:] for field in request.form.keys() if field[:3] == "job"]
            if "delete" in request.form:
                c.drop_plant(request.form["id"])

            elif "add" in request.form:
                # Create a dbc.Plant object from the data in the form and insert it into the database.
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
            # & is the intersection operator. set() converts the dict_keyiterator and list to sets so that the
            # intersection can be found of them. list() converts this back to a list which is sorted on the
            # basis that each item in the new list is the name of a month.
            # A useful side effect of this operation is that any invalid months
            # sent by rogue browsers are filtered out.
            active_months = sorted(list(set(request.form) & set(months)), key=sorting.dt_from_month)
            if "delete" in request.form:
                c.drop_job(request.form["id"])

            elif "add" in request.form:
                job = dbc.Maintenance(request.form["name"],
                                      request.form["desc"],
                                      active_months)
                job.insert()

            elif "edit" in request.form:
                job = dbc.Maintenance(request.form["name"],
                                      request.form["desc"],
                                      active_months,
                                      request.form["id"])
                job.update()
        return render_template("maintenance.html", data=c.load_sql_job_data(), month_list=months)


@app.route("/favicon.ico")
def favicon():
    """Send the favicon from static/favicon.ico and specify its MIME type."""
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/x-icon')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=False)
