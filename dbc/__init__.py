import sqlite3 as sql
import util


class DBConnection:
    def __init__(self):
        self.dbname = "tests.db"
        self.con = None
        self.cur = None

    def __enter__(self):
        self.con = sql.connect(self.dbname)
        self.cur = self.con.cursor()
        self.perform("PRAGMA foreign_keys = ON;")
        
        self.perform("CREATE TABLE IF NOT EXISTS clients "
                     "(cid INTEGER PRIMARY KEY, name TEXT NOT NULL);")

        self.perform("CREATE TABLE IF NOT EXISTS plants "
                     "(pid INTEGER PRIMARY KEY, name TEXT, latin_name TEXT UNIQUE, "
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

    def __exit__(self, *args):
        self.con.commit()
        self.con.close()
        self.con = None
        self.cur = None

    def execute(self, *args):
        self.cur.execute(*args)
        self.con.commit()

    def perform(self, *args):
        self.cur.execute(*args)

    def fetchall(self):
        return self.cur.fetchall()

    def select_clients(self, cid=None):
        if cid is not None:
            self.execute("SELECT * FROM clients WHERE cid=?", (cid,))
        else:
            self.execute("SELECT * FROM clients")
        return self.fetchall()

    def select_plants(self, pid=None):
        if pid is not None:
            self.execute("SELECT * FROM plants WHERE pid=?", (pid,))
        else:
            self.execute("SELECT * FROM plants")
        return self.fetchall()

    def select_jobs(self, mid=None):
        if mid is not None:
            self.execute("SELECT * FROM jobs WHERE mid=?", (mid,))
        else:
            self.execute("SELECT * FROM jobs")
        return self.fetchall()

    def drop_client(self, cid):
        self.delete_pc_links(cid=cid)
        self.execute("DELETE FROM clients WHERE cid=?", (cid,))

    def drop_plant(self, pid):
        self.delete_pc_links(pid=pid)
        self.delete_jp_links(pid=pid)
        self.execute("DELETE FROM plants WHERE pid=?", (pid,))

    def drop_job(self, mid):
        self.delete_jp_links(mid=mid)
        self.delete_mj_links(mid)
        self.execute("DELETE FROM jobs WHERE mid=?", (mid,))

    def load_sql_client_data(self, cid=None):
        return [Client(row[1], cid=row[0],
                       plants=self.select_pc_links(cid=cid)) for row in self.select_clients(cid)]

    def load_sql_plant_data(self, pid=None):
        return [Plant(row[1], row[2], row[3], pid=row[0],
                      jobs=self.select_jp_links(pid=row[0]))
                for row in self.select_plants(pid)]

    def load_sql_job_data(self, mid=None):
        return [Maintenance(row[1], row[2],
                            self.select_mj_links(row[0]), row[0]) for row in self.select_jobs(mid)]

    def select_pc_links(self, cid=None, pid=None):
        if (cid and pid) is not None:
            self.execute("SELECT * FROM client_plant_junction WHERE cid=? AND pid=?", (cid, pid))
            return self.fetchall()[0]
        elif cid is not None:
            self.execute("SELECT pid FROM client_plant_junction WHERE cid=?", (cid,))
        elif pid is not None:
            self.execute("SELECT mid FROM client_plant_junction WHERE pid=?", (pid,))
        else:
            self.execute("SELECT * FROM client_plant_junction")
            return self.fetchall()
        return [row[0] for row in self.fetchall()]

    def select_jp_links(self, pid=None, mid=None):
        if pid is not None:
            self.execute("SELECT jobs.* FROM plant_job_junction "
                         "INNER JOIN jobs ON jobs.mid=plant_job_junction.mid "
                         "WHERE pid=?", (pid,))
        elif mid is not None:
            self.execute("SELECT plants.* FROM plant_job_junction "
                         "INNER JOIN plants ON plants.pid=plant_job_juncion.mid "
                         "WHERE mid=?", (mid,))
        else:
            self.execute("SELECT * FROM plant_job_junction")
            return self.fetchall()
        return [Maintenance(row[1], row[2], None, row[0]) for row in self.fetchall()]

    def select_mj_links(self, mid=None):
        if mid is None:
            self.execute("SELECT * FROM months")
            return self.fetchall()
        else:
            self.execute("SELECT month FROM months WHERE mid=?", (mid,))
        return [row[0] for row in self.fetchall()]

    def link_plant_to_client(self, cid, pid):
        self.execute("INSERT INTO client_plant_junction (cid,pid) VALUES (?,?)", (cid, pid))

    def link_job_to_plant(self, pid, mid):
        self.execute("INSERT INTO plant_job_junction (pid,mid) VALUES (?,?)", (pid, mid))

    def link_month_to_job(self, mid, month):
        self.execute("INSERT INTO months (mid,month) VALUES (?,?)", (mid, month))

    def delete_pc_links(self, cid=None, pid=None):
        if (cid and pid) is not None:
            self.execute("DELETE FROM client_plant_junction WHERE cid=? AND pid=?", (cid, pid))
        elif cid is not None:
            self.execute("DELETE FROM client_plant_junction WHERE cid=?", (cid,))
        elif pid is not None:
            self.execute("DELETE FROM client_plant_junction WHERE pid=?", (pid,))

    def delete_jp_links(self, pid=None, mid=None):
        if (pid and mid) is not None:
            self.execute("DELETE FROM plant_job_junction WHERE pid=? AND mid=?", (pid, mid))
        elif pid is not None:
            self.execute("DELETE FROM plant_job_junction WHERE pid=?", (pid,))
        elif mid is not None:
            self.execute("DELETE FROM plant_job_junction WHERE mid=?", (mid,))

    def delete_mj_links(self, mid):
        if mid is not None:
            self.execute("DELETE FROM months WHERE mid=?", (mid,))


class Client:
    def __init__(self, name, cid=None, plants=None):
        self.id = cid or -1
        self.name = name
        self.plants = plants or []

    def insert(self):
        with DBConnection() as c:
            c.execute("INSERT INTO clients (name) VALUES (?)", (self.name,))
            c.execute("SELECT last_insert_rowid()")
            self.id = c.fetchall()[0][0]
            for pid in self.plants:
                c.link_plant_to_client(cid=self.id, pid=pid)

    def update(self):
        with DBConnection() as c:
            c.delete_pc_links(cid=self.id)
            c.execute("UPDATE clients "
                      "SET name=? WHERE cid=?",
                      (self.name, self.id))
            for pid in self.plants:
                c.link_plant_to_client(cid=self.id, pid=pid)


class Plant:
    def __init__(self, name, latin_name, blooming_period, pid=None, jobs=None):
        self.id = pid or -1  # This is only used when reading from the database
        self.name = name
        self.latin_name = latin_name
        self.blooming_period = blooming_period
        self.jobs = jobs or []
        self.mids = [job.id for job in jobs] if type(jobs[0]) == Maintenance else self.jobs

    def insert(self):
        with DBConnection() as c:
            c.execute("INSERT INTO plants (name,latin_name,blooming_period) VALUES (?,?,?)",
                      (self.name, self.latin_name, self.blooming_period))
            c.execute("SELECT last_insert_rowid()")
            self.id = c.fetchall()[0][0]
            for mid in self.jobs:
                c.link_job_to_plant(pid=self.id, mid=mid)

    def update(self):
        with DBConnection() as c:
            c.delete_jp_links(pid=self.id)
            c.execute("UPDATE plants "
                      "SET name=?, latin_name=?, blooming_period=? "
                      "WHERE pid=?",
                      (self.name, self.latin_name, self.blooming_period, self.id))
            for mid in self.jobs:
                c.link_job_to_plant(pid=self.id, mid=mid)


class Maintenance:
    def __init__(self, name, description, months, mid=None):
        self.id = mid or -1
        self.name = name or ""
        self.description = description or ""
        self.months = sorted(months, key=util.dt_from_month) if months is not None else []

    def insert(self):
        with DBConnection() as c:
            c.execute("INSERT INTO jobs (name,description) VALUES (?,?)",
                      (self.name, self.description))
            c.execute("SELECT last_insert_rowid()")
            self.id = c.fetchall()[0][0]
            for month in self.months:
                c.link_month_to_job(self.id, month)

    def update(self):
        with DBConnection() as c:
            c.delete_mj_links(self.id)
            c.execute("UPDATE jobs "
                      "SET name=?, description=? WHERE mid=?",
                      (self.name, self.description, self.id))
            for month in self.months:
                c.link_month_to_job(self.id, month)
