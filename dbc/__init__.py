import sqlite3 as sql


class DBConnection(object):
    def __init__(self):
        self.dbname = "database.db"
        self.con = None
        self.cur = None

    def __enter__(self):
        self.con = sql.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS clients "
                         "(cid INTEGER PRIMARY KEY, name TEXT NOT NULL);")
        self.cur.execute("CREATE TABLE IF NOT EXISTS jobs "
                         "(mid INTEGER PRIMARY KEY, description TEXT, jan TEXT, "
                         "feb TEXT, mar TEXT, apr TEXT, may TEXT, jun TEXT, jul TEXT, "
                         "aug TEXT, sep TEXT, oct TEXT, nov TEXT, dec TEXT);")
        self.cur.execute("CREATE TABLE IF NOT EXISTS plants "
                         "(pid INTEGER PRIMARY KEY, name TEXT, latin_name TEXT UNIQUE);")
        self.cur.execute("CREATE TABLE IF NOT EXISTS client_plant_junction "
                         "(cid INTEGER, pid INTEGER);")
        self.cur.execute("CREATE TABLE IF NOT EXISTS plant_job_junction "
                         "(pid INTEGER, mid INTEGER);")
        return self

    def __exit__(self, *args):
        self.con.commit()
        self.con.close()
        self.con = None
        self.cur = None

    def execute(self, *args):
        self.cur.execute(*args)


###############################################
# Plants
###############################################
def insert_plant(name, latin_name):
    with DBConnection() as c:
        c.execute("INSERT INTO plants (name,latin_name) VALUES (?,?)",
                  (name, latin_name))


def drop_plant(pid):
    with DBConnection() as c:
        c.execute("DELETE FROM plants WHERE pid=?", (pid,))


def update_plant(pid, name, latin_name):
    with DBConnection() as c:
        c.execute("UPDATE plants "
                  "SET name=?, latin_name=? "
                  "WHERE pid=?",
                  (name, latin_name, pid))


def select_plants(pid=None):
    with DBConnection() as c:
        if pid is not None:
            c.execute("SELECT * FROM plants WHERE pid=?", (pid,))
        else:
            c.execute("SELECT * FROM plants")
        return c.cur.fetchall()


def load_sql_plant_data(pid=None):
    return [{"pid": row[0],
             "name": row[1],
             "latin_name": row[2]}
            for row in select_plants(pid)]


###############################################
# Clients
###############################################
def insert_client(name):
    with DBConnection() as c:
        c.execute("INSERT INTO clients (name) VALUES (?)",
                  (name,))


def drop_client(cid):
    with DBConnection() as c:
        c.execute("DELETE FROM clients WHERE cid=?", (cid,))


def update_client(cid, name):
    with DBConnection() as c:
        c.execute("UPDATE clients "
                  "SET name=? WHERE cid=?",
                  (name, cid))


def select_clients(cid=None):
    with DBConnection() as c:
        if cid is not None:
            c.execute("SELECT * FROM clients WHERE cid=?", (cid,))
        else:
            c.execute("SELECT * FROM clients")
        return c.cur.fetchall()


def load_sql_client_data(pid=None):
    return [{"cid": row[0],
             "name": row[1]}
            for row in select_clients(pid)]


###############################################
# Maintenance jobs
###############################################
def insert_job(description, jan, feb, mar, apr, may, jun, jul, aug, sep, oct_, nov, dec):
    with DBConnection() as c:
        c.execute("INSERT INTO jobs (description,jan,feb,mar,apr,may,jun,jul,aug,sep,oct,nov,dec) "
                  "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                  (description, jan, feb, mar, apr, may, jun, jul, aug, sep, oct_, nov, dec))


def drop_job(mid):
    with DBConnection() as c:
        c.execute("DELETE FROM jobs WHERE mid=?", (mid,))


def update_job(mid, description, jan, feb, mar, apr, may, jun, jul, aug, sep, oct_, nov, dec):
    with DBConnection() as c:
        c.execute("UPDATE jobs "
                  "SET description=?, jan=?, feb=?, mar=?, apr=?, may=?, "
                  "jun=?, jul=?, aug=?, sep=?, oct=?, nov=?, dec=? WHERE mid=?",
                  (description, jan, feb, mar, apr, may, jun, jul, aug, sep, oct_, nov, dec, mid))


def select_jobs(mid=None):
    with DBConnection() as c:
        if mid is not None:
            c.execute("SELECT * FROM jobs WHERE mid=?", (mid,))
        else:
            c.execute("SELECT * FROM jobs")
        return c.cur.fetchall()


def load_sql_job_data(mid=None):
    return [{"mid": row[0], "desc": row[1], "jan": row[2], "feb": row[3],
             "mar": row[4], "apr": row[5], "may": row[6], "jun": row[7], "jul": row[8],
             "aug": row[9], "sep": row[10], "oct": row[11], "nov": row[12], "dec": row[13]}
            for row in select_jobs(mid)]


###############################################
# Junction tables
###############################################
def link_plant_to_client(cid, pid):
    with DBConnection() as c:
        c.execute("INSERT INTO client_plant_junction (cid,pid) VALUES (?,?)", (cid, pid))


def delete_pc_link(cid, pid):
    with DBConnection() as c:
        c.execute("DELETE FROM client_plant_junction WHERE cid=? AND pid=?", (cid, pid))


def select_pc_links(cid=None, pid=None):
    with DBConnection() as c:
        if (cid and pid) is not None:
            return c.execute("SELECT * FROM client_plant_junction WHERE cid=? AND pid=?", (cid, pid))
        elif cid is not None:
            return c.execute("SELECT * FROM client_plant_junction WHERE cid=?", (cid,))
        elif pid is not None:
            return c.execute("SELECT * FROM client_plant_junction WHERE pid=?", (pid,))
        else:
            return c.execute("SELECT * FROM client_plant_junction")


def link_job_to_plant(pid, mid):
    with DBConnection() as c:
        c.execute("INSERT INTO plant_job_junction (pid, mid) VALUES (?,?)", (pid, mid))


def delete_jp_link(pid, mid):
    with DBConnection() as c:
        c.execute("DELETE FROM plant_job_junction WHERE pid=? AND mid=?", (pid, mid))


def select_jp_links(pid=None, mid=None):
    with DBConnection() as c:
        if (pid and mid) is not None:
            return c.execute("SELECT * FROM plant_jop_junction WHERE pid=? AND mid=?", (pid, mid))
        elif pid is not None:
            return c.execute("SELECT * FROM plant_jop_junction WHERE pid=?", (pid,))
        elif mid is not None:
            return c.execute("SELECT * FROM plant_jop_junction WHERE mid=?", (mid,))
        else:
            return c.execute("SELECT * FROM plant_jop_junction")
