import os
import sqlite3

# Data Transfer Objects:
class Vaccine:
    def __init__(self, id, date, supplier, quantity):
        # auto generate ids
        self.id = id
        self.date = date
        self.supplier = int(supplier)
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
            INSERT INTO vaccines (date,supplier, quantity) VALUES (?, ?, ?)
        """, [vaccine.date, vaccine.supplier, vaccine.quantity])

    def delete(self, vaccine):
        self._conn.execute("""
            DELETE FROM vaccines WHERE id=(?)
        """, [vaccine.id])

    def findOldest(self):
        c = self._conn.cursor()
        c.execute("""
            SELECT * FROM vaccines ORDER BY date LIMIT 1
        """)
        return Vaccine(*c.fetchone())

    def update(self, vaccine,amount):
        self._conn.execute("""
               UPDATE vaccines SET quantity = quantity - (?) WHERE id=(?)
           """, [amount, vaccine.id])

class _Suppliers:
    def __init__(self, conn):
        self._conn = conn

    def insert(self, supplier):
        self._conn.execute("""
            INSERT INTO suppliers (id, name, logistic) VALUES (?, ?, ?)
        """, [supplier.id, supplier.name, supplier.logistic])

    def find(self, sup_name):
        c = self._conn.cursor()
        c.execute("""
            SELECT * FROM suppliers WHERE name = ?
        """, [sup_name])
        return Supplier(*c.fetchone())

class _Clinics:
    def __init__(self, conn):
        self._conn = conn

    def insert(self, clinic):
        self._conn.execute("""
            INSERT INTO clinics (id, location, demand, logistic) VALUES (?, ?, ?,?)
        """, [clinic.id, clinic.location, clinic.demand, clinic.logistic])

    def find(self, clinic_location):
        c = self._conn.cursor()
        c.execute("""
            SELECT * FROM clinics WHERE location = ?
        """, [clinic_location])
        return Clinic(*c.fetchone())

    def update(self, clinic_location,clinic_amount):
        self._conn.execute("""
               UPDATE clinics SET demand= demand - (?) WHERE location=(?)
           """, [clinic_amount, clinic_location])


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
            SELECT * FROM logistics WHERE id = ?
        """, [log_id])
        return Logistic(*c.fetchone())

    def updateRecevied(self, log_id, countRec):
        self._conn.execute("""
               UPDATE logistics SET  count_received= count_received + (?) WHERE id =(?)
           """, [countRec,log_id])

    def updateSent(self, logistic_id,amount):
        self._conn.execute("""
               UPDATE logistics SET  count_sent =count_sent + (?) WHERE id =(?)
           """, [amount,logistic_id])

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


    def receiveShipment(self,name,amount,date):
        currentSup=self.suppliers.find(name)
        self.vaccines.insert(Vaccine(0,date,currentSup.id,amount))
        self.logistics.updateRecevied(currentSup.logistic,amount)

    def sendShipment(self, location, amount):
        # take vaccines
        updatedAmount=int(amount)
        while updatedAmount>0:
            currVaccine= self.vaccines.findOldest()
            if updatedAmount >= currVaccine.quantity:
                updatedAmount = updatedAmount - currVaccine.quantity
                self.vaccines.delete(currVaccine)
            else:
                self.vaccines.update(currVaccine, updatedAmount)
                updatedAmount = 0

        # update clinic and logistic
        self.clinics.update(location,amount)
        currClinic=self.clinics.find(location)
        currLogistic=self.logistics.find(currClinic.logistic)
        self.logistics.updateSent(currLogistic.id,amount)


    def _close(self):
        self._conn.commit()
        self._conn.close()

    def create_tables(self):
        self._conn.executescript("""
        CREATE TABLE vaccines (
            id              INTEGER     PRIMARY KEY,
            date            DATE    NOT NULL,
            supplier        REFERENCES Supplier(id),
            quantity        INTEGER     NOT NULL        
        );

        CREATE TABLE suppliers (
            id              INTEGER     PRIMARY KEY,
            name            TEXT    NOT NULL,
            logistic        REFERENCES Logistic(id)    
        );

        CREATE TABLE clinics (
            id              INTEGER     PRIMARY KEY,
            location        TEXT    NOT NULL,
            demand          INTEGER     NOT NULL,
            logistic        REFERENCES Logistic(id)
        );

        CREATE TABLE logistics (
            id              INTEGER      PRIMARY KEY,
            name            TEXT     NOT NULL,
            count_sent      INTEGER      NOT NULL,
            count_received  INTEGER      NOT NULL
        );
    """)
