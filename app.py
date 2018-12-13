import dbc
import os

from flask import Flask, render_template, send_from_directory, request, make_response, session, redirect, url_for

import sorting

app = Flask(__name__)
app.secret_key = b'L<g^3gEXdF>4"g2~5Qpc578E9!>P6R=j*,8t'
# A necessary list of all the months.
months = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


@app.route("/", methods=["GET", "POST"])
def index():
    """Handle database choosing.

    If the request is a GET request, make a list of the .db files in the
    current directory without their extensions, and pass that to the
    template renderer.
    Otherwise, check for the form type. If the form is for deleting,
    delete the specified database file and remove the database name from
    the session. If the form is for adding or selecting, set the
    database name in the session. It doesn't matter whether the form is
    for adding or selecting, since sqlite3 creates the database file if
    it doesn't exist.
    """
    if request.method == "GET":
        db_list = [file[:-3] for file in os.listdir(".") if file.endswith(".db")]
        response = make_response(render_template("index.html", db_list=db_list))
    else:
        if "delete" in request.form:
            os.remove(request.form["name"] + ".db")
            session.pop("name", None)
        elif "add" in request.form or "select" in request.form:
            session["name"] = request.form["name"]
        response = make_response(redirect(url_for("clients")))
    return response


@app.route("/clients", methods=["GET", "POST"])
def clients():
    """Handle requests for the clients page.

    If the request is a POST request, execute the action specified by
    the browser in the form.
    Return clients.html, rendered with the client, plant and month data inserted.
    """
    dbname = session["name"] if "name" in session else None
    with dbc.DBConnection(dbname) as c:
        if request.method == "POST":
            # In the form, the browser may send a list of plant IDs to link. They arrive as form fields
            # with names like 'plant-n' where n is the ID of a plant to link.
            # For every form field, check if the 1st 5 characters are 'plant'. If so, then extract the plant id.
            pids_to_link = [field[6:] for field in request.form.keys() if field[:5] == "plant"]
            if "delete" in request.form:
                c.drop_client(request.form["id"])

            elif "add" in request.form:
                client = dbc.Client(request.form["name"], plants=pids_to_link)
                client.insert(dbname)

            elif "edit" in request.form:
                client = dbc.Client(request.form["name"], cid=request.form["id"], plants=pids_to_link)
                client.update(dbname)

        return render_template("clients.html", data=c.load_sql_client_data(),
                               plant_list=c.load_sql_plant_data(), months=months)


@app.route("/plants", methods=["GET", "POST"])
def plants():
    dbname = session["name"] if "name" in session else None
    with dbc.DBConnection(dbname) as c:
        if request.method == "POST":
            mids_to_link = [field[4:] for field in request.form.keys() if field[:3] == "job"]
            if "delete" in request.form:
                c.drop_plant(request.form["id"])

            elif "add" in request.form:
                # Create a dbc.Plant object from the data in the form and insert it into the database.
                plant = dbc.Plant(request.form["name"], request.form["latin-name"],
                                  request.form["blooming-period"], jobs=mids_to_link)
                plant.insert(dbname)

            elif "edit" in request.form:
                plant = dbc.Plant(request.form["name"], request.form["latin-name"],
                                  request.form["blooming-period"], pid=request.form["id"],
                                  jobs=mids_to_link)
                plant.update(dbname)

        return render_template("plants.html", data=c.load_sql_plant_data(),
                               job_list=c.load_sql_job_data())


@app.route("/maintenance", methods=["GET", "POST"])
def jobs():
    dbname = session["name"] if "name" in session else None
    with dbc.DBConnection(dbname) as c:
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
                job.insert(dbname)

            elif "edit" in request.form:
                job = dbc.Maintenance(request.form["name"],
                                      request.form["desc"],
                                      active_months,
                                      request.form["id"])
                job.update(dbname)
        return render_template("maintenance.html", data=c.load_sql_job_data(), month_list=months)


@app.route("/favicon.ico")
def favicon():
    """Send the favicon from static/favicon.ico and specify its MIME type."""
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/x-icon')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=False)
