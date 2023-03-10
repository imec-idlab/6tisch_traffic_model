import numpy as np

def init(MOP):
    global nodes                # Array of nodes
    global read                 # Interrupt reading logfile and perform prediction
    global count                # How many nodes did we encounter?
    global mop                  # RPL MOP (1 = storing mode, 0 = non-storing mode)
    global logfile              # Logfile name
    global logsize              # Logfile size
    global logcount             # Current line in logfile
    global cont                 # Continue reading logfile
    global intstream            # Required to change INT update interval

    nodes = []
    count = 0
    read = True
    logcount = 0
    cont = True
    intstream = False
    mop = MOP

class node:
    def __init__(self, id):
        self.id = id            # Node ID
        self.n = 0              # Number of neighbours
        self.ns = []            # Neighbours
        self.ts = None          # Time source
        self.pn = None          # Preferred parent
        self.etx = 1            # ETX preferred parent
        self.coaptx = 0         # Amount of TX bytes due to CoAP traffic
        self.coaprx = 0         # Amount of RX bytes due to CoAP traffic
        self.ebtx = 0           # Amount of TX bytes due to EB traffic
        self.ebrx = 0           # Amoount of RX bytes due to EB traffic
        self.diotx = 0          # Amount of TX bytes due to DIO traffic
        self.diorx = 0          # Amount of RX bytes due to DIO traffic
        self.daotx = 0          # Amount of TX bytes due to DAO traffic
        self.daorx = 0          # Amount of RX bytes due to DAO traffic
        self.dao_acktx = 0      # Amount of TX bytes due to DAO ACK traffic
        self.dao_ackrx = 0      # Amount of RX bytes due to DAO ACK traffic
        self.eacktx = 0         # Amount of TX bytes due to EACK traffic
        self.eackrx = 0         # Amount of RX bytes due to EACK traffic
        self.lastdao = None     # Node time of last DAO transmission
        self.lastdio = None     # Node time of last DIO transmission
        self.lastebgen = None   # Node time of last EB generation
        self.lastebtx = None    # Node time of last EB transmission
        self.updtime = None     # Node time of last INT update
        self.predtime = None    # Time of prediction
        self.intbytes = [[],[]] # Number of INT bytes with timestamp
        self.rt = []            # Routing table

    def add_neighbour(self, neighbour):
        if(np.any(np.isin(self.ns,neighbour)) == 0):
            self.ns = np.append(self.ns,neighbour)
            self.n = len(self.ns)

    def search_eb_receivers(self):
        receivers = []
        if(len(nodes) != 0):
            for tsn in nodes:
                if((tsn.ts != None) and (tsn.ts.id == self.id)):
                    receivers.append(tsn)
        return receivers
    
    def get_next_hop_sm(self, destination):
        if(len(self.rt) != 0):
            for route in self.rt:
                if(route[0].id == destination.id):
                    return route[1]
        return -1
    
    def is_node_in_path(self,path):
        if(len(path) != 0):
            for p in path:
                if(p.id == self.id):
                    return True
        return False

    def reset_bytecount(self):
        self.coaptx = 0
        self.ebtx = 0
        self.diotx = 0     
        self.daotx = 0  
        self.dao_acktx = 0 
        self.eacktx = 0
        self.coaprx = 0
        self.ebrx = 0
        self.diorx = 0     
        self.daorx = 0  
        self.dao_ackrx = 0 
        self.eackrx = 0

    def print_n(self, telemetry, protocol, interval):
        print("----------")
        print("Node " + str(self.id))
        if(telemetry):
            print("#Neighbours: " + str(self.n))
            string = ""
            for n in self.ns:
                string = string + str(n.id) + " "
            print("Neighbours: " + string)
            if(self.rt != []):
                print("Routing table: ")
                for r in self.rt:
                    print(str(r[0].id) + " v " + str(r[1].id))
            if(self.ts != None):
                print("Time source: " + str(self.ts.id))
            if(self.pn != None):
                print("Preferred parent: " + str(self.pn.id))
            if(self.lastdao != None):
                print("Last DAO at: " + str(self.lastdao) + " ms")
            if(self.lastdio != None):
                print("Last DIO at: " + str(self.lastdio) + " ms")
            if(self.lastebgen != None):
                print("Last EB gen at: " + str(self.lastebgen) + " ms")
            if(self.lastebtx != None):
                print("Last EB TX at: " + str(self.lastebtx) + " ms")
            if(self.updtime != None):
                print("Last update at: " + str(self.updtime) + " ms")
        if(self.predtime != None):
            print("Prediction at: " + str(self.predtime) + " ms")
        print(str(interval) + " s prediction: ")
        if(protocol):
            print("EB bytes: \t" + str(self.ebtx) + " TX / " + str(self.ebrx) + " RX")
            print("EACK bytes: \t" + str(self.eacktx) + " TX / " + str(self.eackrx) + " RX")
            print("DIO bytes: \t" + str(self.diotx) + " TX / " + str(self.diorx) + " RX")
            print("DAO bytes: \t" + str(self.daotx) + " TX / " + str(self.daorx) + " RX")
            print("DAO ACK bytes: \t" + str(self.dao_acktx) + " TX / " + str(self.dao_ackrx) + " RX")
            print("CoAP bytes: \t" + str(self.coaptx) + " TX / " + str(self.coaprx) + " RX")
        print("Total TX bytes:\t" + str(self.diotx+self.ebtx+self.eacktx+self.coaptx+self.daotx+self.dao_acktx+self.diotx))
        print("Total RX bytes:\t" + str(self.diorx+self.ebrx+self.eackrx+self.coaprx+self.daorx+self.dao_ackrx+self.diorx))
        print("Total bytes:\t" + str(self.diotx+self.ebtx+self.eacktx+self.coaptx+self.daotx+self.dao_acktx+self.diotx+self.diorx+self.ebrx+self.eackrx+self.coaprx+self.daorx+self.dao_ackrx+self.diorx))

def search_node(n):
    if(len(nodes) != 0):
        for i in nodes:
            if(n == i.id):
                return i
    return -1

def get_etx(node1, node2):
    if((node1.pn != None) and (node1.pn.id == node2.id)):
        etx = max(node1.etx,1)
    elif((node2.pn != None) and (node2.pn.id == node1.id)):
        etx = max(node2.etx,1)
    else:
        etx = 1
    return etx