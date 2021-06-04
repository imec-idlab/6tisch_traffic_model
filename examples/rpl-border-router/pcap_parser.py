import sys
import pyshark
import matplotlib.pyplot as plt
import datetime
import numpy as np
import csv

NODES       = 10
RTX         = 1     # include retransmissions
retransmissions = [[],[],[],[],[],[]]

class node:
    def __init__(self, id):
        self.id = id
        self.n = 0
        self.eb = [[],[]]
        self.eack = [[],[]]
        self.dio = [[],[]]
        self.dis = [[],[]]
        self.dao = [[],[]]
        self.dao_ack = [[],[]]
        self.udp = [[],[]]
        self.txeb = 0
        self.txeack = 0
        self.txdio = 0
        self.txdis = 0
        self.txdao = 0
        self.txdao_ack = 0
        self.txudp = 0
        self.txtotal = 0

def clear_nodes(nodes):
    for n in nodes:
        n.txeb = 0
        n.txeack = 0
        n.txdio = 0
        n.txdis = 0
        n.txdao = 0
        n.txdao_ack = 0
        n.txudp = 0
        n.txtotal = 0

def get_nodes(N):
    nodes = []
    for n in range(0,N):
        nodes.append(node(n+1))
    return nodes

def hex2dec(hex):
    if(hex[0] == ":"):
        temp = "0x" + hex[1]
    else:
        temp = "0x" + hex
    dec = int(temp,16)
    return dec

def parse_pcap(cap, nodes):
    for p in range(0,len(cap)):
        fcf = int(cap[p]['wpan'].fcf,16)
        time = cap[p].sniff_time
        length = int(cap[p].frame_info.cap_len)
        fcf_mask = 0x7
        # EACKs
        if((fcf & fcf_mask) == 0x2):
            source = hex2dec(str(cap[p-1]['wpan'].dst64)[-2:])
            #if("UDP" in str(cap[p-1].layers)):          # Only include UDP/CoAP EACKs
            nodes[int(source)-1].eack[0].append(time)
            nodes[int(source)-1].eack[1].append(length)
        else:
            source = hex2dec(str(cap[p]['wpan'].src64)[-2:])
            # EBs
            if((fcf & fcf_mask) == 0x0):
                nodes[int(source)-1].eb[0].append(time)
                nodes[int(source)-1].eb[1].append(length)
            # ICMPv6
            elif("ICMPV6" in str(cap[p].layers)):
                icmpv6code = int(cap[p]['icmpv6'].code)
                # DIO
                if(icmpv6code == 1):
                    nodes[int(source)-1].dio[0].append(time)
                    nodes[int(source)-1].dio[1].append(length)
                # DAO
                elif(icmpv6code == 2):
                    if(RTX or ((int(cap[p+1]['wpan'].fcf,16) & fcf_mask) == 0x2)):
                        nodes[int(source)-1].dao[0].append(time)
                        nodes[int(source)-1].dao[1].append(length)
                    else:
                        destination = hex2dec(str(cap[p]['wpan'].dst64)[-2:])
                        retransmissions[0].append(source)
                        retransmissions[1].append(destination)                    
                # DAO ACK
                elif(icmpv6code == 3):
                    if(RTX or ((int(cap[p+1]['wpan'].fcf,16) & fcf_mask) == 0x2)):
                        nodes[int(source)-1].dao_ack[0].append(time)
                        nodes[int(source)-1].dao_ack[1].append(length)
                    else:
                        destination = hex2dec(str(cap[p]['wpan'].dst64)[-2:])
                        retransmissions[2].append(source)
                        retransmissions[3].append(destination)
            # UDP and 6LoWPAN (fragments)
            elif("UDP" in str(cap[p].layers) or "6LOWPAN" in str(cap[p].layers)):
                if(RTX or ((int(cap[p+1]['wpan'].fcf,16) & fcf_mask) == 0x2)):
                    nodes[int(source)-1].udp[0].append(time)
                    nodes[int(source)-1].udp[1].append(length)
                else:
                    destination = hex2dec(str(cap[p]['wpan'].dst64)[-2:])
                    retransmissions[4].append(source)
                    retransmissions[5].append(destination)
            else:
                print("Message type not recognized at " + str(time))
                print(cap[p])
    return nodes

def nearest(times, time):
    time_diff = np.abs([date - time for date in times])
    return time_diff.argmin(0)

def get_protocol_bytes(protocol, start, end):
    if(len(protocol[0]) != 0):
        start = nearest(protocol[0], start)
        end = nearest(protocol[0], end)
        return np.sum(protocol[1][start:end])
    else:
        return 0

def get_total_bytes(node, start, end):
    node.txeb = get_protocol_bytes(node.eb,start,end)
    node.txeack = get_protocol_bytes(node.eack,start,end)
    node.txdio = get_protocol_bytes(node.dio,start,end)
    node.txdis = get_protocol_bytes(node.dis,start,end)
    node.txdao = get_protocol_bytes(node.dao,start,end)
    node.txdao_ack = get_protocol_bytes(node.dao_ack,start,end)
    node.txudp = get_protocol_bytes(node.udp,start,end)
    node.txtotal = node.txeb+node.txeack+node.txdio+node.txdis+node.txdao+node.txdao_ack+node.txudp

def print_bytes_per_node(nodes, start, end):
    # print("Start time: " + str(start.time))
    # print("End time: " + str(end.time))
    for n in nodes:
        get_total_bytes(n,start,end)
        print("----------")
        print("Node " + str(n.id))
        print("EB bytes: " + str(n.txeb))
        print("EACK bytes: " + str(n.txeack))
        print("DIO bytes: " + str(n.txdio))
        print("DIS bytes: " + str(n.txdis))
        print("DAO bytes: " + str(n.txdao))
        print("DAO ACK bytes: " + str(n.txdao_ack))
        print("UDP/CoAP bytes: " + str(n.txudp))
        print("Total bytes: " + str(n.txtotal))

# def plot_messages(nodes, mtype):
#     if(mtype == 0):
#         # EBs
#         plt.figure("EBs per node")
#     elif(mtype == 1):
#         # DIOs
#         plt.figure("DIOs per node")
#     elif(mtype == 2):
#         # UDP
#         plt.figure("UDP/CoAP packets per node")
#     # elif(mtype == 3):
#     #     # ACK
#     #     plt.figure("EACKs per node")
#     for n in range(1,len(nodes)-1):
#         plt.plot_date(nodes[n][mtype], range(0,len(nodes[n][mtype])), label=("Node " + str(n)))
#     plt.legend()
#     #plt.show()

def analyse_retransmissions(retransmissions):
    dao = np.zeros((10,10))
    for i in range(0, len(retransmissions[0])):
        dao[retransmissions[0][i]-1,retransmissions[1][i]-1] += 1
    dao_ack = np.zeros((10,10))
    for i in range(0, len(retransmissions[2])):
        dao_ack[retransmissions[2][i]-1,retransmissions[3][i]-1] += 1
    coap = np.zeros((10,10))
    for i in range(0, len(retransmissions[4])):
        coap[retransmissions[4][i]-1,retransmissions[5][i]-1] += 1
    print("DAOs")
    print(dao)
    print("DAO ACKs")
    print(dao_ack)
    print("CoAP")
    print(coap)

#assert (sys.argv[1])
#pcap_filename = sys.argv[1]
pcap_filename = '../../tools/cooja/build/radiolog-1620813503474.pcap'
cap = pyshark.FileCapture(pcap_filename)
cap.load_packets()
nodes = parse_pcap(cap, get_nodes(NODES))

start = cap[0].sniff_time + datetime.timedelta(hours=1)
end = start + datetime.timedelta(hours=1)

predictions = []

with open('predictions.csv', newline='') as csvfile:
    predreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in predreader:
        predictions.append(row)

def get_prediction_times(preds):
    times = []
    is_new_time = 1
    for i in range(2,len(preds)):
        if(is_new_time == 1):
            times.append(float(preds[i][0]))
            is_new_time = 0
        elif(preds[i][0] == ''):
            is_new_time = 1
    return times

times = get_prediction_times(predictions)

with open('actual.csv', 'w', newline='') as csvfile:
    actwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    actwriter.writerow(['Node_ID', 'EB_TX', 'EACK_TX', 'DIO_TX', 'DIS_TX', 'DAO_TX', 'DAO_ACK_TX', 'CoAP_TX'])
    for t in times:
        start = cap[0].sniff_time + datetime.timedelta(seconds=(t/1000))
        end = start + datetime.timedelta(minutes=20)
        clear_nodes(nodes)
        print_bytes_per_node(nodes,start,end)
        for n in nodes:
            actwriter.writerow([n.id, n.txeb, n.txeack, n.txdio, n.txdis, n.txdao, int(n.txdao_ack), n.txudp])
        actwriter.writerow([0,0,0,0,0,0,0,0])

# print_bytes_per_node(nodes,start,end)
# with open('actual.csv', 'w', newline='') as csvfile:
#     actwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
#     actwriter.writerow(['Node ID', 'EB TX', 'EACK TX', 'DIO TX', 'DIS TX', 'DAO TX', 'DAO ACK TX', 'CoAP TX'])
#     for n in nodes:
#         actwriter.writerow([n.id, n.txeb, n.txeack, n.txdio, n.txdis, n.txdao, int(n.txdao_ack), n.txudp])

# plot_messages(nodes,0)
# plot_messages(nodes,1)
# plot_messages(nodes,2)
# plt.show()