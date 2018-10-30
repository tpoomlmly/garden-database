import sqlite3 as sql


# TODO normalise to 3rd normal form
# TODO put all functions into classes
class DBConnection:
    def __init__(self):
        self.dbname = "database.db"
        self.con = None
        self.cur = None

    def __enter__(self):
        self.con = sql.connect(self.dbname)
        self.cur = self.con.cursor()
        self.execute("PRAGMA foreign_keys = ON;")
        
        self.execute("CREATE TABLE IF NOT EXISTS clients "
                     "(cid INTEGER PRIMARY KEY, name TEXT NOT NULL);")

        self.execute("CREATE TABLE IF NOT EXISTS jobs "
                     "(mid INTEGER PRIMARY KEY, name TEXT, description TEXT, "
                     "months TEXT);")

        self.execute("CREATE TABLE IF NOT EXISTS plants "
                     "(pid INTEGER PRIMARY KEY, name TEXT, latin_name TEXT UNIQUE, "
                     "blooming_period TEXT);")

        self.execute("CREATE TABLE IF NOT EXISTS client_plant_junction "
                     "(cid INTEGER REFERENCES clients, pid INTEGER REFERENCES plants, "
                     "PRIMARY KEY(cid, pid));")

        self.execute("CREATE TABLE IF NOT EXISTS plant_job_junction "
                     "(pid INTEGER REFERENCES plants, mid INTEGER REFERENCES jobs, "
                     "PRIMARY KEY(pid ,mid));")
        return self

    def __exit__(self, *args):
        self.con.commit()
        self.con.close()
        self.con = None
        self.cur = None

    def execute(self, *args):
        self.cur.execute(*args)

    def fetchall(self):
        return self.cur.fetchall()


class Client:
    def __init__(self, name, cid=None, plants=None):
        self.id = cid or -1
        self.name = name
        self.plants = plants or []


class Plant:
    def __init__(self, name, latin_name, blooming_period, pid=None, jobs=None):
        self.id = pid or -1  # This is only used when reading from the database
        self.name = name
        self.latin_name = latin_name
        self.blooming_period = blooming_period
        self.jobs = jobs or []


class Maintenance:
    def __init__(self, name, description, months, mid=None):
        self.id = mid or -1
        self.name = name
        self.description = description
        self.months = months


###############################################
# Plants
###############################################
def insert_plant(plant):
    with DBConnection() as c:
        c.execute("INSERT INTO plants (name,latin_name,blooming_period) VALUES (?,?,?)",
                  (plant.name, plant.latin_name, plant.blooming_period))
        for mid in plant.jobs:
            c.execute("SELECT last_insert_rowid()")
            pid = c.fetchall()[0][0]
            link_job_to_plant(pid=pid, mid=mid)


def drop_plant(pid):
    delete_pc_links(pid=pid)
    delete_jp_links(pid=pid)
    with DBConnection() as c:
        c.execute("DELETE FROM plants WHERE pid=?", (pid,))


def update_plant(plant):
    with DBConnection() as c:
        c.execute("UPDATE plants "
                  "SET name=?, latin_name=?, blooming_period=? "
                  "WHERE pid=?",
                  (plant.name, plant.latin_name, plant.blooming_period, plant.id))
    delete_jp_links(pid=plant.id)
    for mid in plant.jobs:
        link_job_to_plant(pid=plant.id, mid=mid)


def select_plants(pid=None):
    with DBConnection() as c:
        if pid is not None:
            c.execute("SELECT * FROM plants WHERE pid=?", (pid,))
        else:
            c.execute("SELECT * FROM plants")
        return c.fetchall()


def load_sql_plant_data(pid=None):
    return [Plant(row[1], row[2], row[3], pid=row[0],
                  jobs=select_jp_links(pid=row[0])) for row in select_plants(pid)]


###############################################
# Clients
###############################################
def insert_client(client):
    with DBConnection() as c:
        c.execute("INSERT INTO clients (name) VALUES (?)",
                  (client.name,))
        for pid in client.plants:
            c.execute("SELECT last_insert_rowid()")
            cid = c.fetchall()[0][0]
            link_plant_to_client(cid=cid, pid=pid)


def drop_client(cid):
    delete_pc_links(cid=cid)
    with DBConnection() as c:
        c.execute("DELETE FROM clients WHERE cid=?", (cid,))


def update_client(client):
    with DBConnection() as c:
        c.execute("UPDATE clients "
                  "SET name=? WHERE cid=?",
                  (client.name, client.id))
    delete_pc_links(cid=client.id)
    for pid in client.plants:
        link_plant_to_client(cid=client.id, pid=pid)


def select_clients(cid=None):
    with DBConnection() as c:
        if cid is not None:
            c.execute("SELECT * FROM clients WHERE cid=?", (cid,))
        else:
            c.execute("SELECT * FROM clients")
        return c.fetchall()


def load_sql_client_data(cid=None):
    return [Client(row[1], cid=row[0],
                   plants=select_pc_links(cid=cid)) for row in select_clients(cid)]


###############################################
# Maintenance jobs
###############################################
def insert_job(job):
    with DBConnection() as c:
        c.execute("INSERT INTO jobs (name,description,months) VALUES (?,?,?)",
                  (job.name, job.description, repr(job.months)))


def drop_job(mid):
    delete_jp_links(mid=mid)
    with DBConnection() as c:
        c.execute("DELETE FROM jobs WHERE mid=?", (mid,))


def update_job(job):
    with DBConnection() as c:
        c.execute("UPDATE jobs "
                  "SET name=?, description=?, months=? WHERE mid=?",
                  (job.name, job.description, repr(job.months), job.id))


def select_jobs(mid=None):
    with DBConnection() as c:
        if mid is not None:
            c.execute("SELECT * FROM jobs WHERE mid=?", (mid,))
        else:
            c.execute("SELECT * FROM jobs")
        return c.fetchall()


def load_sql_job_data(mid=None):
    return [Maintenance(row[1], row[2], eval(row[3]), row[0]) for row in select_jobs(mid)]


###############################################
# Junction tables
###############################################
def link_plant_to_client(cid, pid):
    with DBConnection() as c:
        c.execute("INSERT INTO client_plant_junction (cid,pid) VALUES (?,?)", (cid, pid))


def delete_pc_links(cid=None, pid=None):
    with DBConnection() as c:
        if (cid and pid) is not None:
            c.execute("DELETE FROM client_plant_junction WHERE cid=? AND pid=?", (cid, pid))
        elif cid is not None:
            c.execute("DELETE FROM client_plant_junction WHERE cid=?", (cid,))
        elif pid is not None:
            c.execute("DELETE FROM client_plant_junction WHERE pid=?", (pid,))


def select_pc_links(cid=None, pid=None):
    with DBConnection() as c:
        if (cid and pid) is not None:
            c.execute("SELECT * FROM client_plant_junction WHERE cid=? AND pid=?", (cid, pid))
            return c.fetchall()[0]
        elif cid is not None:
            c.execute("SELECT * FROM client_plant_junction WHERE cid=?", (cid,))
        elif pid is not None:
            c.execute("SELECT * FROM client_plant_junction WHERE pid=?", (pid,))
        else:
            c.execute("SELECT * FROM client_plant_junction")
    return [row[0] for row in c.fetchall()]


def link_job_to_plant(pid, mid):
    with DBConnection() as c:
        c.execute("INSERT INTO plant_job_junction (pid, mid) VALUES (?,?)", (pid, mid))


def delete_jp_links(pid=None, mid=None):
    with DBConnection() as c:
        if (pid and mid) is not None:
            c.execute("DELETE FROM plant_job_junction WHERE pid=? AND mid=?", (pid, mid))
        elif pid is not None:
            c.execute("DELETE FROM plant_job_junction WHERE pid=?", (pid,))
        elif mid is not None:
            c.execute("DELETE FROM plant_job_junction WHERE mid=?", (mid,))


def select_jp_links(pid=None, mid=None):
    with DBConnection() as c:
        if (pid and mid) is not None:
            c.execute("SELECT * FROM plant_job_junction WHERE pid=? AND mid=?", (pid, mid))
            return c.fetchall()[0]
        elif pid is not None:
            c.execute("SELECT * FROM plant_job_junction WHERE pid=?", (pid,))
        elif mid is not None:
            c.execute("SELECT * FROM plant_job_junction WHERE mid=?", (mid,))
        else:
            c.execute("SELECT * FROM plant_job_junction")
    return [row[0] for row in c.fetchall()]
