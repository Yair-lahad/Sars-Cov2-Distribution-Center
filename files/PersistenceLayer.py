import os
import sqlite3

# Data Transfer Objects:
class Vaccine:
    def __init__(self, id, date, supplier, quantity):
        self.id = id
        self.date = date
        self.supplier = supplier
        self.quantity = quantity

class Supplier:
    def __init__(self, id, name, logistic):
        self.id = id
        self.name = name
        self.logistic = logistic

class Clinic:
    def __init__(self, id, location, demand, logistic):
        self.id = id
        self.location = location
        self.demand = demand
        self.logistic = logistic

class Logistic:
    def __init__(self, id, name, count_sent, count_received):
        self.id = id
        self.name = name
        self.count_sent = count_sent
        self.count_received = count_received

# Data Access Objects:
# All of these are meant to be singletons
class _Vaccines:
    def __init__(self, conn):
        self._conn = conn

    def insert(self, vaccine):
        self._conn.execute("""
            INSERT INTO vaccines (id, date,supplier, quantity) VALUES (?, ?, ?, ?)
        """, [vaccine.id, vaccine.date, vaccine.supplier, vaccine.quantity])

    def find(self, vaccine_id):
        c = self._conn.cursor()
        c.execute("""
            SELECT id, date FROM vaccines WHERE id = ?
        """, [vaccine_id])

        return Vaccine(*c.fetchone())

    def update(self, vaccine):
        self._conn.execute("""
               UPDATE vaccines SET date=(?), supplier=(?), quantity=(?) WHERE id=(?)
           """, [vaccine.date, vaccine.supplier, vaccine.quantity, vaccine.id])

    def printT(self):
        c=self._conn.cursor()
        c.execute("""
            SELECT * FROM vaccines
        """)
        return(c.fetchone())

class _Suppliers:
    def __init__(self, conn):
        self._conn = conn

    def insert(self, supplier):
        self._conn.execute("""
            INSERT INTO suppliers (id, name, logistic) VALUES (?, ?, ?)
        """, [supplier.id, supplier.name, supplier.logistic])

    def find(self, sup_id):
        c = self._conn.cursor()
        c.execute("""
            SELECT id,name FROM suppliers WHERE id = ?
        """, [sup_id])

        return Supplier(*c.fetchone())

    def update(self, supplier):
        self._conn.execute("""
               UPDATE suppliers SET name=(?), logistic=(?) WHERE id=(?)
           """, [supplier.name, supplier.logistic, supplier.id])

class _Clinics:
    def __init__(self, conn):
        self._conn = conn

    def insert(self, clinic):
        self._conn.execute("""
            INSERT INTO clinics (id, location, demand, logistic) VALUES (?, ?, ?,?)
        """, [clinic.id, clinic.location, clinic.demand, clinic.logistic])

    def find_all(self):
        c = self._conn.cursor()
        all = c.execute("""
            SELECT id, location, demand, logistic FROM clinics
        """).fetchall()

        return [Clinic(*row) for row in all]

    def update(self, clinic):
        self._conn.execute("""
               UPDATE clinics SET location=(?), demand=(?), logistic=(?) WHERE id=(?)
           """, [clinic.location, clinic.demand, clinic.logistic, clinic.id])


class _Logistics:
    def __init__(self, conn):
        self._conn = conn

    def insert(self, logistic):
        self._conn.execute("""
            INSERT INTO logistics (id, name, count_sent, count_received) VALUES (?, ?, ?, ?)
        """, [logistic.id, logistic.name, logistic.count_sent, logistic.count_received])

    def find(self, log_id):
        c = self._conn.cursor()
        c.execute("""
            SELECT id,name,count_sent, count_received FROM logistics WHERE id = ?
        """, [log_id])
        return Logistic(*c.fetchone())

    def update(self, logistic):
        self._conn.execute("""
               UPDATE logistics SET name =(?), count_sent =(?), count_received =(?) WHERE id =(?)
           """, [logistic.name, logistic.count_sent, logistic.count_received, logistic.id])


class _Repository:
    def __init__(self):
        self.delete_DB_at_start=True
        if self.delete_DB_at_start:
            if(os.path.exists("database.db")):
                os.remove("database.db")
        self._conn = sqlite3.connect('database.db')
        self.create_tables()
        self.vaccines = _Vaccines(self._conn)
        self.suppliers = _Suppliers(self._conn)
        self.clinics = _Clinics(self._conn)
        self.logistics = _Logistics(self._conn)

    def _close(self):
        self._conn.commit()
        self._conn.close()

    def create_tables(self):
        self._conn.executescript("""
        CREATE TABLE vaccines (
            id              INT     PRIMARY KEY,
            date            DATE    NOT NULL,
            supplier        REFERENCES Supplier(id),
            quantity        INT     NOT NULL        
        );

        CREATE TABLE suppliers (
            id              INT     PRIMARY KEY,
            name            TEXT    NOT NULL,
            logistic        REFERENCES Logistic(id)    
        );

        CREATE TABLE clinics (
            id              INT     PRIMARY KEY,
            location        TEXT    NOT NULL,
            demand          INT     NOT NULL,
            logistic        REFERENCES Logistic(id)
        );

        CREATE TABLE logistics (
            id              INT      PRIMARY KEY,
            name            TEXT     NOT NULL,
            count_sent      INT      NOT NULL,
            count_received  INT      NOT NULL
        );
    """)
