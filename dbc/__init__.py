import sqlite3 as sql

import sorting


class DBConnection:
    """Database connection handler class."""

    def __init__(self, dbname=None):
        """Specify the database name and initialise connection and cursor variables.

        Initialising self.con and self.cur as None has the quirk that a
        'with' statement is required to instantiate the class,
        otherwise an AttributeError is raised.
        """
        self.dbname = dbname or "database.db"
        self.con = None
        self.cur = None

    def __enter__(self):
        """Initialise the database.

        Initialise the database connection and cursor objects, then
        create all the tables. Calling this method by using a 'with'
        statement will create a new blank database file.
        """
        self.con = sql.connect(self.dbname)
        self.cur = self.con.cursor()
        self.perform("PRAGMA foreign_keys = ON;")
        
        self.perform("CREATE TABLE IF NOT EXISTS clients "
                     "(cid INTEGER PRIMARY KEY, name TEXT NOT NULL);")

        self.perform("CREATE TABLE IF NOT EXISTS plants "
                     "(pid INTEGER PRIMARY KEY, name TEXT, latin_name TEXT, "
                     "blooming_period TEXT);")

        self.perform("CREATE TABLE IF NOT EXISTS jobs "
                     "(mid INTEGER PRIMARY KEY, name TEXT, description TEXT);")

        self.perform("CREATE TABLE IF NOT EXISTS months "
                     "(mid INTEGER REFERENCES jobs, month TEXT, PRIMARY KEY(mid, month));")

        self.perform("CREATE TABLE IF NOT EXISTS client_plant_junction "
                     "(cid INTEGER REFERENCES clients, pid INTEGER REFERENCES plants, "
                     "PRIMARY KEY(cid, pid));")

        self.perform("CREATE TABLE IF NOT EXISTS plant_job_junction "
                     "(pid INTEGER REFERENCES plants, mid INTEGER REFERENCES jobs, "
                     "PRIMARY KEY(pid ,mid));")
        return self

    def __exit__(self, exc_type, exc_value, tb):
        """Close the database connection.

        If all goes well, commit all the uncommitted changes and set
        self.con and self.cur to None and return True.
        If any exceptions occur, roll back all changes, then return
        False to show that an exception has occurred.
        """
        if tb is None:
            self.con.commit()
            self.con.close()
            self.con = None
            self.cur = None
            return True
        else:
            self.con.rollback()
            self.con.close()
            self.con = None
            self.cur = None
            return False

    def execute(self, *args):
        """Execute an SQL statement and commit the changes.

        Takes the same arguments as sqlite3.Cursor.execute()
        """
        self.cur.execute(*args)
        self.con.commit()

    def perform(self, *args):
        """Execute an SQL statement but don't commit the changes yet.

        Takes the same arguments as sqlite3.Cursor.execute()
        """
        self.cur.execute(*args)

    def fetchall(self):
        """Return a list of tuples representing the result from the last SELECT."""
        return self.cur.fetchall()

    def select_clients(self, cid=None):
        """Select the client with a given client ID, or select all clients."""
        if cid is not None:
            self.execute("SELECT * FROM clients WHERE cid=?", (cid,))
        else:
            self.execute("SELECT * FROM clients")
        return self.fetchall()

    def select_plants(self, pid=None):
        """Select the plant with a given plant ID, or select all plants."""
        if pid is not None:
            self.execute("SELECT * FROM plants WHERE pid=?", (pid,))
        else:
            self.execute("SELECT * FROM plants")
        return self.fetchall()

    def select_jobs(self, mid=None):
        """Select the maintenance job with a given Maintenance ID, or select all maintenance jobs."""
        if mid is not None:
            self.execute("SELECT * FROM jobs WHERE mid=?", (mid,))
        else:
            self.execute("SELECT * FROM jobs")
        return self.fetchall()

    def drop_client(self, cid):
        """Delete a client from the database.

        Takes the ID of the client to be deleted. Sever any ties it has
        with any plants first to avoid foreign key constraint errors,
        then delete the client's entry.
        """
        self.delete_pc_links(cid=cid)
        self.execute("DELETE FROM clients WHERE cid=?", (cid,))

    def drop_plant(self, pid):
        """Delete a plant from the database.

        Takes the ID of the plant to be deleted. Sever any ties it has
        with the clients that own it and remove its entries in the
        plant-maintenance link table. Finally, delete the plant itself.
        """
        self.delete_pc_links(pid=pid)
        self.delete_jp_links(pid=pid)
        self.execute("DELETE FROM plants WHERE pid=?", (pid,))

    def drop_job(self, mid):
        """Delete a maintenance job from the database.

        Takes the ID of the job to be deleted. Remove its entries in the
        plant-maintenance and maintenance-month link tables, then delete
        its entry in the maintenance table.
        """
        self.delete_jp_links(mid=mid)
        self.delete_mj_links(mid)
        self.execute("DELETE FROM jobs WHERE mid=?", (mid,))

    def load_sql_client_data(self, cid=None):
        """Create a list of Client objects from the client table.

        Create a Client object from the data in each row in the client
        table. For each Client's plants attribute, run select_pc_links()
        to create a list of all the plants the Client has.
        Running this method will result in all the data in the database
        being returned in an easy-to-use object-oriented format, which
        lets clients.html access the data in a clear and readable way
        without extra processing.
        """
        return [Client(row[1], cid=row[0],
                       plants=self.select_pc_links(cid=row[0])) for row in self.select_clients(cid)]

    def load_sql_plant_data(self, pid=None):
        """Create a list of Plant objects from the plant table.

        Create a Plant object from the data in each row in the plant
        table. For each Plant's jobs attribute, run select_mj_links()
        to create a list of all the maintenance jobs the Plant has.
        """
        return [Plant(row[1], row[2], row[3], pid=row[0],
                      jobs=self.select_jp_links(pid=row[0])) for row in self.select_plants(pid)]

    def load_sql_job_data(self, mid=None):
        """Create a list of Maintenance objects from the job table.

        Create a Maintenance object from the data in each row in the
        job table. For each Maintenance's months attribute, run
        select_mj_links() to create a list of all the months the
        Maintenance has.
        """
        return [Maintenance(row[1], row[2],
                            self.select_mj_links(row[0]), row[0]) for row in self.select_jobs(mid)]

    def select_pc_links(self, cid=None, pid=None):
        """Process the plant-client link data.

        If a client ID is specified, return a list of Plant objects that
        that client has, from the results of the select statement.
        For each Plant's jobs attribute, run select_jp_links().
        If a plant ID is specified, return a list of Client objects that
        own that plant, from the results of the select statement.
        For each Client's plants attribute, run select_pc_links() again
        but with the Client's ID.
        If no IDs are specified, return the raw data from the
        client-plant link table.
        """
        if cid is not None:
            self.execute("SELECT plants.* FROM client_plant_junction "
                         "INNER JOIN plants ON plants.pid=client_plant_junction.pid "
                         "WHERE cid=?", (cid,))
            return [Plant(row[1], row[2], row[3], pid=row[0],
                          jobs=self.select_jp_links(pid=row[0])) for row in self.fetchall()]
        elif pid is not None:
            self.execute("SELECT clients.* FROM client_plant_junction "
                         "INNER JOIN clients ON clients.cid=client_plant_junction"
                         "WHERE pid=?", (pid,))
            return [Client(row[1], cid=row[0], plants=self.select_pc_links(cid=row[0])) for row in self.fetchall()]
        else:
            self.execute("SELECT * FROM client_plant_junction")
            return self.fetchall()

    def select_jp_links(self, pid=None, mid=None):
        """Process the plant-maintenance link data.

        If a plant ID is specified, return a list of Maintenance objects
        that that plant has, from the results of the select statement.
        For the months attribute of each Maintenance in the list, run
        select_mj_links().
        If a maintenance ID is specified, return a list of Plant objects
        that require the type of maintenance belonging to that ID. For
        each Plant's jobs attribute, run select_jp_links() again but
        with the Plant's ID.
        If no IDs are specified, return the raw data from the plant-job
        link table.
        """
        if pid is not None:
            self.execute("SELECT jobs.* FROM plant_job_junction "
                         "INNER JOIN jobs ON jobs.mid=plant_job_junction.mid "
                         "WHERE pid=?", (pid,))
            return [Maintenance(row[1], row[2], self.select_mj_links(row[0]), mid=row[0]) for row in self.fetchall()]
        elif mid is not None:
            self.execute("SELECT plants.* FROM plant_job_junction "
                         "INNER JOIN plants ON plants.pid=plant_job_juncion.mid "
                         "WHERE mid=?", (mid,))
            return [Plant(row[1], row[2], row[3], pid=row[0],
                          jobs=self.select_jp_links(pid=row[0])) for row in self.fetchall()]
        else:
            self.execute("SELECT * FROM plant_job_junction")
            return self.fetchall()

    def select_mj_links(self, mid=None):
        """Process the maintenance-month link data.

        If no maintenance ID is specified, then return the raw data from
        the month table.
        If a maintenance ID is specified, then extract each job's month
        from the 1-tuple that contains it and return them all in a list.
        """
        if mid is None:
            self.execute("SELECT * FROM months")
            return self.fetchall()
        else:
            self.execute("SELECT month FROM months WHERE mid=?", (mid,))
        return [row[0] for row in self.fetchall()]

    def select_months_of_plant(self, pid):
        """Create a list of all the months when a plant needs tending to.

        Extract each month from the 1-tuple it comes in and return it
        in a list.
        """
        self.execute("SELECT DISTINCT month from plants "
                     "INNER JOIN plant_job_junction "
                     "ON plants.pid=plant_job_junction.pid "
                     "INNER JOIN jobs "
                     "ON plant_job_junction.mid=jobs.mid "
                     "INNER JOIN months ON jobs.mid=months.mid "
                     "WHERE plants.pid=?", (pid,))
        return [row[0] for row in self.fetchall()]

    def link_plant_to_client(self, cid, pid):
        """Take a client ID and plant ID and link the plant to the client."""
        self.execute("INSERT INTO client_plant_junction (cid,pid) VALUES (?,?)", (cid, pid))

    def link_job_to_plant(self, pid, mid):
        """Take a plant ID and maintenance ID and link the job to the plant."""
        self.execute("INSERT INTO plant_job_junction (pid,mid) VALUES (?,?)", (pid, mid))

    def link_month_to_job(self, mid, month):
        """Take a maintenance ID and month name and link the month to the job."""
        self.execute("INSERT INTO months (mid,month) VALUES (?,?)", (mid, month))

    def delete_pc_links(self, cid=None, pid=None):
        """Delete link data between plants and clients.

        If a both types of ID are specified, delete the entry with the
        specified client ID and plant ID.
        If just a client ID is specified, delete all plant-client link
        entries for that client.
        If just a plant ID is specified, delete all plant-client link
        entries for that plant.
        """
        if (cid and pid) is not None:
            self.execute("DELETE FROM client_plant_junction WHERE cid=? AND pid=?", (cid, pid))
        elif cid is not None:
            self.execute("DELETE FROM client_plant_junction WHERE cid=?", (cid,))
        elif pid is not None:
            self.execute("DELETE FROM client_plant_junction WHERE pid=?", (pid,))

    def delete_jp_links(self, pid=None, mid=None):
        """Delete link data between maintenance jobs and plants.

        If both types of ID are specified, delete the entry with the
        specified maintenance ID and plant ID.
        If just a plant ID is specified, delete all maintenance-plant
        link entries for that plant.
        If just a maintenance ID is specified, delete all maintenance-
        plant linke entries for that maintenance job.
        """
        if (pid and mid) is not None:
            self.execute("DELETE FROM plant_job_junction WHERE pid=? AND mid=?", (pid, mid))
        elif pid is not None:
            self.execute("DELETE FROM plant_job_junction WHERE pid=?", (pid,))
        elif mid is not None:
            self.execute("DELETE FROM plant_job_junction WHERE mid=?", (mid,))

    def delete_mj_links(self, mid):
        """Delete link data between maintenance jobs and months for the specified job ID."""
        if mid is not None:
            self.execute("DELETE FROM months WHERE mid=?", (mid,))


class DBItem:
    """Base superclass for database entries.

    Every database entry has a name and an ID, and must be able to
    insert itself into the database and update the entry corresponding
    to its ID.
    """

    def __init__(self, name, id_=None):
        self.name = name or ""
        self.id = id_ or -1

    def insert(self): raise NotImplementedError

    def update(self): raise NotImplementedError


class Client(DBItem):
    """Client class. Inherits DBItem and has a list of plants owned and their IDs."""

    def __init__(self, name, cid=None, plants=None):
        """Initialises the Client's attributes.

        Requires a name, optional client ID and plant list.
        When simply creating a Client to insert into the database, the ID
        is calculated automatically by SQLite. The ID is only specified
        when reading from the database.
        The list of plants can be specified either as a list of IDs or
        as a list of Plant objects. If the type of the first item in the
        list is a Plant, then extract their IDs and store those in a
        separate variable.
        """
        super().__init__(name, cid)
        self.plants = plants or []
        self.pids = self.plants
        if self.plants and type(self.plants[0]) == Plant:
            self.pids = [plant.id for plant in self.plants]

    def insert(self):
        """Insert this Client's data into the database.

        Inserts the client's name, then links all the plants they own.
        """
        with DBConnection() as c:
            c.execute("INSERT INTO clients (name) VALUES (?)", (self.name,))
            c.execute("SELECT last_insert_rowid()")
            self.id = c.fetchall()[0][0]
            for pid in self.pids:
                c.link_plant_to_client(cid=self.id, pid=pid)

    def update(self):
        """Update the database record corresponding to this Client's ID.

        Update the name, and also re-link the plants in case any plant
        links have changed.
        """
        with DBConnection() as c:
            c.execute("UPDATE clients "
                      "SET name=? WHERE cid=?",
                      (self.name, self.id))
            c.delete_pc_links(cid=self.id)
            for pid in self.pids:
                c.link_plant_to_client(cid=self.id, pid=pid)


class Plant(DBItem):
    """Plant class. Inherits DBItem.

    Has a latin name, blooming period, list of maintenance jobs and a
    list of the months when this plant needs tending to.
    """

    def __init__(self, name, latin_name, blooming_period, pid=None, jobs=None):
        """Initialise the Plant's attributes.

        If the job list is a list of Maintenance objects then extract
        each Maintenance's ID and store them separately.
        """
        super().__init__(name, pid)
        self.latin_name = latin_name
        self.blooming_period = blooming_period
        self.jobs = jobs or []
        self.mids = self.jobs
        if self.jobs and type(self.jobs[0]) == Maintenance:
            self.mids = [job.id for job in self.jobs]
        with DBConnection() as c:
            self.months = c.select_months_of_plant(self.id)

    def insert(self):
        """Insert this Plant's data into the database.

        Inserts the plant's name, latin name and blooming period, then
        links all necessary Maintenance jobs.
        """
        with DBConnection() as c:
            c.execute("INSERT INTO plants (name,latin_name,blooming_period) VALUES (?,?,?)",
                      (self.name, self.latin_name, self.blooming_period))
            c.execute("SELECT last_insert_rowid()")
            self.id = c.fetchall()[0][0]
            for mid in self.mids:
                c.link_job_to_plant(pid=self.id, mid=mid)

    def update(self):
        """Update the database record corresponding to this Plant's ID.

        Update the normal name, latin name and blooming period, and
        re-link any maintenance jobs in case this data has changed.
        """
        with DBConnection() as c:
            c.execute("UPDATE plants "
                      "SET name=?, latin_name=?, blooming_period=? "
                      "WHERE pid=?",
                      (self.name, self.latin_name, self.blooming_period, self.id))
            c.delete_jp_links(pid=self.id)
            for mid in self.mids:
                c.link_job_to_plant(pid=self.id, mid=mid)


class Maintenance(DBItem):
    """Maintenance job class. Inherits DBItem.

    Has a description and a list of English full names of the months to
    which it applies.
    """

    def __init__(self, name, description, months, mid=None):
        """Initialise the Maintenance's attributes.

        Sort the list of months using the utility from sorting as the key.
        """
        super().__init__(name, mid)
        self.description = description or ""
        self.months = sorted(months, key=sorting.dt_from_month) if months is not None else []

    def insert(self):
        """Insert this Maintenance's data into the database.

        Insert the name and description, then link all necessary months.
        """
        with DBConnection() as c:
            c.execute("INSERT INTO jobs (name,description) VALUES (?,?)",
                      (self.name, self.description))
            c.execute("SELECT last_insert_rowid()")
            self.id = c.fetchall()[0][0]
            for month in self.months:
                c.link_month_to_job(self.id, month)

    def update(self):
        """Update the database record corresponding to this job's ID.

        Update the name and description, and relink the months in case
        any of these have changed.
        """
        with DBConnection() as c:
            c.execute("UPDATE jobs "
                      "SET name=?, description=? WHERE mid=?",
                      (self.name, self.description, self.id))
            c.delete_mj_links(self.id)
            for month in self.months:
                c.link_month_to_job(self.id, month)
