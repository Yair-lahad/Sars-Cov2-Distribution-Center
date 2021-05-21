import atexit
import sys

from PersistenceLayer import _Repository, Logistic, Supplier, Vaccine, Clinic


def main():
    # the repository singleton
    repo = _Repository()
    atexit.register(repo._close)
    # output paramaters
    total_inventory = 0
    total_demand = 0
    total_received = 0
    total_sent = 0

    # we will take info from config by order of objects : 1.vacccines 2.suppliers 3. clinics 4.logistics
    with open(sys.argv[1]) as inputfile:
        linesList = [line.rstrip('\n') for line in inputfile]  # take lines
        lens = list(map(int, linesList[0].split(",")))
        from itertools import accumulate
        locations = list(accumulate(lens))
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
            curr_line = linesList[next].split(",")
            repo.vaccines.insert(Vaccine(*curr_line))
            total_inventory += int(curr_line[3])
        # insert clinics
        for i in range(0, lens[2]):
            next = locations[1] + i
            curr_line=linesList[next].split(",")
            repo.clinics.insert(Clinic(*curr_line))
            total_demand += int(curr_line[2])

    out = open(sys.argv[3], 'w')
    # handle orders
    with open(sys.argv[2]) as orders:
        ordersList = [line.rstrip('\n').split(",") for line in orders]
        for i in range(0, len(ordersList)):
            lineLen = len(ordersList[i])
            if lineLen == 2:
                repo.sendShipment(*ordersList[i])
                total_sent += int(ordersList[i][1])
                total_inventory -= int(ordersList[i][1])
                total_demand -= int(ordersList[i][1])
            else:
                repo.receiveShipment(*ordersList[i])
                total_received += int(ordersList[i][1])
                total_inventory += int(ordersList[i][1])
            # update output file
            out.write(str(total_inventory) + "," + str(total_demand) + "," + str(total_received) + "," + str(total_sent))
            if i< len(ordersList)-1:
                out.write("\n")
    out.close()

if __name__ == '__main__':
    main()
