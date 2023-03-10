import numpy as np
import csv
import re
import sys

try:    
    import config
except:
    print("Did you fill the fields in the config.py.example file and rename it to config.py?")
    exit()

class node:
    def __init__(self, id):
        self.id = id
        self.n = 0
        # Transmitted frames [timestamp, bytes]
        self.ebtx = [[],[]]
        self.eacktx = [[],[]]
        self.diotx = [[],[]]
        self.daotx = [[],[]]
        self.dao_acktx = [[],[]]
        self.coaptx = [[],[]]
        # Received frames [timestamp, bytes]
        self.ebrx = [[],[]]
        self.eackrx = [[],[]]
        self.diorx = [[],[]]
        self.daorx = [[],[]]
        self.dao_ackrx = [[],[]]
        self.coaprx = [[],[]]
        # Total transmitted bytes
        self.txeb = 0
        self.txeack = 0
        self.txdio = 0
        self.txdao = 0
        self.txdao_ack = 0
        self.txcoap = 0
        self.txcoapcount = 0
        self.txtotal = 0
        # Total received bytes
        self.rxeb = 0
        self.rxeack = 0
        self.rxdio = 0
        self.rxdao = 0
        self.rxdao_ack = 0
        self.rxcoap = 0
        self.rxtotal = 0
        self.rtx = 0

def clear_nodes(nodes):
    for n in nodes:
        n.txeb = 0
        n.txeack = 0
        n.txdio = 0
        n.txdao = 0
        n.txdao_ack = 0
        n.txcoap = 0
        n.txtotal = 0
        n.rxeb = 0
        n.rxeack = 0
        n.rxdio = 0
        n.rxdao = 0
        n.rxdao_ack = 0
        n.rxcoap = 0
        n.rxtotal = 0

def get_nodes(N):
    nodes = []
    for n in range(0,N):
        nodes.append(node(n+1))
    return nodes

def search_node(nodes,n):
    if(len(nodes) != 0):
        for i in range(0,len(nodes)):
            if(n == nodes[i].id):
                return i
    return -1

def parse_cooja(file, nodes, rtx):
    with open(file) as csvfile:
        prevline = 0
        for line in csvfile:
            line_data = re.split('\t|[|]', line)
            source_id = search_node(nodes,int(line_data[1]))
            if(source_id != -1):
                metadata = re.split(' ',line_data[3].strip())
                time = int(line_data[0])
                length = int(metadata[0][:-1])
                receivers = re.split(',',line_data[2].strip())
                if((rtx == 0) and (receivers[0] == '-') and (length != 37)):
                    nodes[source_id].rtx += 1
                else:
                    receiver_ids = []
                    for r in receivers:
                        if(r != '-'):
                            r_id = search_node(nodes,int(r))
                            if(r_id != -1):
                                receiver_ids.append(r_id)
                    if(metadata[2] == '-'):
                        prevline = 0
                        nodes[source_id].ebtx[0].append(time)
                        nodes[source_id].ebtx[1].append(length)
                        for receiver_id in receiver_ids:
                            nodes[receiver_id].ebrx[0].append(time)
                            nodes[receiver_id].ebrx[1].append(length)
                    elif(metadata[2] == 'A'):
                        # if(prevline == 0):
                        nodes[source_id].eacktx[0].append(time)
                        nodes[source_id].eacktx[1].append(length)
                        for receiver_id in receiver_ids:
                            nodes[receiver_id].eackrx[0].append(time)
                            nodes[receiver_id].eackrx[1].append(length)
                        prevline = 0
                    elif(metadata[2] == 'D'):
                        data = line_data[-1].replace(' ','')
                        prevline = 0
                        if('9B01' in data):
                            nodes[source_id].diotx[0].append(time)
                            nodes[source_id].diotx[1].append(length)
                            for receiver_id in receiver_ids:
                                nodes[receiver_id].diorx[0].append(time)
                                nodes[receiver_id].diorx[1].append(length)
                        elif('9B02' in data):
                            nodes[source_id].daotx[0].append(time)
                            nodes[source_id].daotx[1].append(length)
                            for receiver_id in receiver_ids:
                                nodes[receiver_id].daorx[0].append(time)
                                nodes[receiver_id].daorx[1].append(length)
                        elif('9B03' in data):
                            nodes[source_id].dao_acktx[0].append(time)
                            nodes[source_id].dao_acktx[1].append(length)
                            for receiver_id in receiver_ids:
                                nodes[receiver_id].dao_ackrx[0].append(time)
                                nodes[receiver_id].dao_ackrx[1].append(length)
                        else:
                            nodes[source_id].coaptx[0].append(time)
                            nodes[source_id].coaptx[1].append(length)
                            for receiver_id in receiver_ids:
                                nodes[receiver_id].coaprx[0].append(time)
                                nodes[receiver_id].coaprx[1].append(length)
                            prevline = 1
                    
            else:
                print("Source " + line_data[1] + " not recognized!")
    return nodes

def nearest_start(times, time):
    arg = 0
    for t in times:
        if(t-time >= 0):
            return arg
        arg += 1

def nearest_stop(times,time):
    arg = 0
    for t in times:
        if(t-time >= 0):
            return arg-1
        arg += 1

def get_protocol_bytes(protocol, start, end):
    if(len(protocol[0]) != 0):
        start = nearest_start(protocol[0], start)
        end = nearest_stop(protocol[0], end)
        if(end == None or start == None or start > end):
            return 0
        else:
            return np.sum(protocol[1][start:end+1])
    else:
        return 0

def get_total_bytes(node, start, end):
    node.txeb = get_protocol_bytes(node.ebtx,start,end)
    node.txeack = get_protocol_bytes(node.eacktx,start,end)
    node.txdio = get_protocol_bytes(node.diotx,start,end)
    node.txdao = get_protocol_bytes(node.daotx,start,end)
    node.txdao_ack = get_protocol_bytes(node.dao_acktx,start,end)
    node.txcoap = get_protocol_bytes(node.coaptx,start,end)
    node.txtotal = node.txeb+node.txeack+node.txdio+node.txdao+node.txdao_ack+node.txcoap
    node.rxeb = get_protocol_bytes(node.ebrx,start,end)
    node.rxeack = get_protocol_bytes(node.eackrx,start,end)
    node.rxdio = get_protocol_bytes(node.diorx,start,end)
    node.rxdao = get_protocol_bytes(node.daorx,start,end)
    node.rxdao_ack = get_protocol_bytes(node.dao_ackrx,start,end)
    node.rxcoap = get_protocol_bytes(node.coaprx,start,end)
    node.rxtotal = node.rxeb+node.rxeack+node.rxdio+node.rxdao+node.rxdao_ack+node.rxcoap

def get_prediction_times(preds):
    times = []
    is_new_time = 1
    for i in range(1,len(preds)):
        if(is_new_time == 1 and preds[i][0] != '0'):
            times.append(float(preds[i][0]))
            is_new_time = 0
        elif(preds[i][0] == '0'):
            is_new_time = 1
    return times

def get_prediction_nodes(preds):
    new = 0
    nodes = []
    for i in range(len(preds)-100,len(preds)):
        if((new == 0) and (preds[i][0] == '0')):
            new = 1
        elif(new == 1):
            if(preds[i][0] != '0'):
                nodes.append(node(int(preds[i][1])))
            else:
                return nodes
    return nodes

if(len(sys.argv) < 2):
    print("Missing argument!")
else:
    print("Parsing cooja logfile...")
    retransmissions = int(sys.argv[1])
    predictions = []

    with open('predictions.csv', newline='') as csvfile:
        predreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in predreader:
            predictions.append(row)

    start = nodes = parse_cooja(config.SIM_DIR + "/cooja_log.csv", get_prediction_nodes(predictions),retransmissions)
    times = get_prediction_times(predictions)

    with open('actual.csv', 'w', newline='') as csvfile:
        actwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        actwriter.writerow(['Time','Node_ID','EB_TX','EB_RX','EACK_TX','EACK_RX','DIO_TX','DIO_RX','DAO_TX','DAO_RX','DAO_ACK_TX','DAO_ACK_RX','CoAP_TX','CoAP_RX','Total_TX','Total_RX','Total'])
        for t in times:
            start = t
            end = start + config.P_INTERVAL*1000
            clear_nodes(nodes)
            for n in nodes:
                get_total_bytes(n,start,end)
                actwriter.writerow([int(t),n.id,int(n.txeb),int(n.rxeb),int(n.txeack),int(n.rxeack),int(n.txdio),int(n.rxdio),int(n.txdao),int(n.rxdao),int(n.txdao_ack),int(n.rxdao_ack),int(n.txcoap),int(n.rxcoap),int(n.txtotal),int(n.rxtotal),int(n.txtotal+n.rxtotal)])
            actwriter.writerow([0,'Node_ID','EB_TX','EB_RX','EACK_TX','EACK_RX','DIO_TX','DIO_RX','DAO_TX','DAO_RX','DAO_ACK_TX','DAO_ACK_RX','CoAP_TX','CoAP_RX','Total_TX','Total_RX','Total'])