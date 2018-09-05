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
                         "(cid INTEGER PRIMARY KEY, Name TEXT NOT NULL, Plants TEXT")
        self.cur.execute("CREATE TABLE IF NOT EXISTS maintenance "
                         "(mid INTEGER PRIMARY KEY, description TEXT, January TEXT, "
                         "February TEXT, March TEXT, April TEXT, May TEXT, June TEXT, "
                         "July TEXT, August TEXT, September TEXT, October TEXT, "
                         "November TEXT, December TEXT);")
        self.cur.execute("CREATE TABLE IF NOT EXISTS plants "
                         "(pid INTEGER PRIMARY KEY, name TEXT, latin_name TEXT UNIQUE, "
                         "maintenance TEXT);")
        return self

    def __exit__(self, *args):
        self.con.commit()
        self.con.close()
        self.con = None
        self.cur = None

    def execute(self, *args):
        self.cur.execute(*args)


def insert_plant(name, latin_name, maintenance):
    with DBConnection() as c:
        c.execute("INSERT INTO plants (name,latin_name,maintenance) VALUES (?,?,?)",
                  (name, latin_name, maintenance))


def drop_plant(pid):
    with DBConnection() as c:
        c.execute("DELETE FROM plants WHERE pid=?", (pid,))


def update_plant(pid, name, latin_name, maintenance):
    with DBConnection() as c:
        c.execute("UPDATE plants "
                  "SET name=?, latin_name=?, maintenance=? "
                  "WHERE pid=?",
                  (name, latin_name, maintenance, pid))


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
             "latin_name": row[2],
             "maintenance": row[3]}
            for row in select_plants(pid)]
