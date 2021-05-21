import atexit
import sqlite3
import os
from PersistenceLayer import _Repository, Logistic, Supplier, Vaccine, Clinic


def main():
    # the repository singleton
    repo = _Repository()
    atexit.register(repo._close)
    # we will take info from config by order of objects : 1.vacccines 2.suppliers 3. clinics 4.logistics
    with open('config.txt') as inputfile:
        linesList = [line.rstrip('\n') for line in inputfile]  # take lines
        lens = list(map(int, linesList[0].split(",")))
        from itertools import accumulate
        locations = list(accumulate(lens))
        # print(lens)
        # print(locations)
        linesList = linesList[1:]  # remove first line of sizes
        # insert logistics
        for i in range(0, lens[3]):
            next = locations[2] + i
            repo.logistics.insert(Logistic(*linesList[next].split(",")))
        # insert suppliers
        for i in range(0, lens[1]):
            next = locations[0] + i
            repo.suppliers.insert(Supplier(*linesList[next].split(",")))
        # insert vaccines
        for i in range(0, lens[0]):
            next = 0 + i
            repo.vaccines.insert(Vaccine(*linesList[next].split(",")))
        # insert clinics
        for i in range(0, lens[2]):
            next = locations[1] + i
            repo.clinics.insert(Clinic(*linesList[next].split(",")))

        print(repo.vaccines.printT())


if __name__ == '__main__':
    main()
