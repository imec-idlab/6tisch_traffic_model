###############
### IMPORTS ###
###############

import numpy as np
import nodes as ns
import parse_log
import csv
import sys

try:    
    import config
except:
    print("Did you fill the fields in the config.py.example file and rename it to config.py?")
    exit()

###
# Get EB bytes during prediction interval
# Input:    nodes, prediction interval (p_time), optional telemetry enabled (opt_tel)
# Output:   TX and RX bytes for every node in nodes
###
def get_eb_bytes(nodes):
    ti = config.P_INTERVAL*1000.0
    eb = config.EB_PERIOD*1000.0
    sf = config.SF_PERIOD*1000.0
    for n in nodes:
        if(config.EB_INT and (n.predtime != None) and (n.lastebgen != None) and (n.lastebtx != None)):
            to1 = n.predtime - (n.lastebgen + np.floor((n.predtime-n.lastebgen)/eb)*eb)
            to2 = n.predtime - (n.lastebtx + np.floor((n.predtime-n.lastebtx)/sf)*sf)
            to1_ = ti+to1-np.floor((ti+to1)/eb)*eb
            to2_ = ti+to2-np.floor((ti+to2)/sf)*sf
            if(ti+to1-eb > 0):
                n_eb = np.floor((ti+to1-eb)/eb)+1
                if(to2 > to1):
                    n_eb += 1
                if(to2_ > to1_):
                    n_eb -= 1
            else:
                n_eb = 0
                if(to2 > to1):
                    n_eb += 1
        else:
            n_eb = ti/eb
        n.ebtx = n_eb*config.L_EB
        receivers = n.search_eb_receivers()
        if(receivers != 0):
            for r in receivers:
                r.ebrx += n_eb*config.L_EB

###
# Get DIO bytes during prediction interval
# Input:    nodes, prediction interval (p_time), optional telemetry enabled (opt_tel)
# Output:   TX and RX bytes for every node in nodes
###
def get_dio_bytes(nodes):
    ti = config.P_INTERVAL*1000.0
    dio = config.IMAX*1000.0
    for n in nodes:
        if(config.DIO_INT and (n.predtime != None) and (n.lastdio != None)):
            to = n.predtime - (n.lastdio + np.floor((n.predtime-n.lastdio)/dio)*dio)
            n_dio = np.floor((ti+to)/dio)
            n_dio = ti/dio
            n.diotx = n_dio*config.L_DIO
            if(n.n != 0):
                for nb in n.ns:
                    nb.diorx += n_dio*config.L_DIO
        else:
            n_dio = ti/dio
        n.diotx = n_dio*config.L_DIO
        if(n.n != 0):
            for nb in n.ns:
                nb.diorx += n_dio*config.L_DIO

###
# Get multihop storing mode path from sender to receiver
# Input:    sender and receiver nodes
# Output:   path from sender to receiver
###
def get_multihop_path(sender, receiver):
    path = []
    if(sender.id == receiver.id):
        return path
    path.append(sender)
    hop = sender
    next_hop = sender.get_next_hop_sm(receiver)
    while(path[-1].id != receiver.id):
        # Is there a downlink route?
        if(next_hop == -1):
            # No downlink route from root, abort
            if(hop.id == config.ROOT):
                return []
            # Try uplink root
            elif(hop.pn != None):
                # Is the parent the receiver?
                if(hop.pn.id == receiver.id):
                    path.append(receiver)
                    return path
                # Is the parent in the path?
                elif(hop.pn.is_node_in_path(path)):
                    return []
                else:
                    path.append(hop.pn)
                    next_hop = hop.pn.get_next_hop_sm(receiver)
                    hop = hop.pn
            else:
                return []
        elif(next_hop.id == receiver.id):
            path.append(receiver)
            return path
        else:
            path.append(next_hop)
            hop = next_hop
            next_hop = hop.get_next_hop_sm(receiver)
    return path

###
# Get fragments for a given payload
# Input:    Payload, MAC header length, IP, UDP and CoAP header length and SRH/H2H length
# Output:   Array of fragment lengths
###   
def get_fragmenting(payload, srh):
    fragments = []
    tot_hdr = config.L_TOT_HDR + srh
    if(payload + tot_hdr <= 126):
        fragments.append(payload+tot_hdr)
    else:
        if(srh%2 == 0):
            temp = 125-4-tot_hdr
            fragments.append(temp+tot_hdr+4)
        else:
            temp = 126-4-tot_hdr
            fragments.append(temp+tot_hdr+4)
        payload -= temp
        while(payload != 0):
            temp = np.min([126-5-config.L_MAC_HDR,payload])
            fragments.append(temp+config.L_MAC_HDR+5)
            payload -= temp
    return fragments

###
# Get CoAP bytes for a given path and payload
# Input:    Path, payload, MAC header, total header, number of CoAP messages
# Output:   TX and RX bytes for every node in path
###
def get_multihop_coap_bytes(path, payload, n_coap):
    # Get fragments
    single = get_fragmenting(payload, 0)
    mh_first = get_fragmenting(payload, 8)
    mh_inter = get_fragmenting(payload, 17)
    mh_last = get_fragmenting(payload, 9)
    etx = 1
    if(len(path) == 2):
        etx = ns.get_etx(path[0], path[-1])
        path[0].coaptx += sum(single)*n_coap*etx
        path[-1].eacktx += len(single)*config.L_EACK*n_coap
        path[-1].coaprx += sum(single)*n_coap
        path[0].eackrx += len(single)*config.L_EACK*n_coap
    elif(len(path) > 2):
        etx = ns.get_etx(path[0], path[1])
        path[0].coaptx += sum(mh_first)*n_coap*etx
        path[1].eacktx += len(mh_first)*config.L_EACK*n_coap
        path[1].coaprx += sum(mh_first)*n_coap
        path[0].eackrx += len(mh_first)*config.L_EACK*n_coap
        for i in range (1, len(path)-2):
            etx = ns.get_etx(path[i], path[i+1])
            path[i].coaptx += sum(mh_inter)*n_coap*etx
            path[i+1].eacktx += len(mh_inter)*config.L_EACK*n_coap
            path[i+1].coaprx += sum(mh_inter)*n_coap
            path[i].eackrx += len(mh_inter)*config.L_EACK*n_coap
        etx = ns.get_etx(path[-1], path[-2])
        path[-2].coaptx += sum(mh_last)*n_coap*etx
        path[-1].eacktx += len(mh_last)*config.L_EACK*n_coap
        path[-1].coaprx += sum(mh_last)*n_coap
        path[-2].eackrx += len(mh_last)*config.L_EACK*n_coap

###
# Get P2P CoAP bytes
# Input:    Nodes, request payload, response payload, MAC header, total header, number of CoAP messages
# Output:   TX and RX bytes for every node in nodes
###
def get_p2p_coap_bytes(nodes, rq_payload, rp_payload):
    ti = config.P_INTERVAL*1000.0
    coap = config.COAP_PERIOD*1000.0
    for n in nodes:
        if(n.id != config.SERVER):
            # CoAP messages were spread out to prevent network flooding, remove if not applicable
            if(n.id < 9):
                firstcoap = (((n.id-1)*(config.COAP_PERIOD/9.0))%config.COAP_PERIOD)*1000.0+384
            else:
                firstcoap = (((n.id-2)*(config.COAP_PERIOD/9.0))%config.COAP_PERIOD)*1000.0+384
            to = n.predtime - (firstcoap + np.floor((n.predtime-firstcoap)/coap)*coap)
            n_coap = np.floor((ti+to)/coap)
            request_path = get_multihop_path(n, ns.search_node(config.SERVER))
            response_path = get_multihop_path(ns.search_node(config.SERVER), n)
            if(len(request_path) != 0):
                get_multihop_coap_bytes(request_path, rq_payload, n_coap)
            if(len(response_path) != 0):
                get_multihop_coap_bytes(response_path, rp_payload, n_coap)

###
# Get DAO bytes for a given path and payload
# Input:    Path, number of frames, payload, DAO (0) or DAO_ACK (1)
# Output:   TX and RX bytes for every node in path
###
def get_multihop_dao_bytes(path, n_dao, l_dao, dao):
    if(len(path) == 2):
        etx = ns.get_etx(path[0], path[-1])
        if(dao):
            path[0].daotx += l_dao*n_dao*etx
            path[-1].daorx += l_dao*n_dao
        else:
            path[0].dao_acktx += l_dao*n_dao*etx
            path[-1].dao_ackrx += l_dao*n_dao
        path[-1].eacktx += config.L_EACK*n_dao
        path[0].eackrx += config.L_EACK*n_dao
    elif(len(path) > 2):
        etx = ns.get_etx(path[0], path[1])
        if(dao):
            path[0].daotx += l_dao*n_dao*etx
            path[1].daorx += l_dao*n_dao
        else:
            path[0].dao_acktx += l_dao*n_dao*etx
            path[1].dao_ackrx += l_dao*n_dao
        path[1].eacktx += config.L_EACK*n_dao        
        path[0].eackrx += config.L_EACK*n_dao
        for i in range (1, len(path)-2):
            etx = ns.get_etx(path[i], path[i+1])
            if(dao):
                path[i].daotx += l_dao*n_dao*etx
                path[i+1].daorx += l_dao*n_dao
            else:
                path[i].dao_acktx += l_dao*n_dao*etx
                path[i+1].dao_ackrx += l_dao*n_dao
            path[i+1].eacktx += config.L_EACK*n_dao            
            path[i].eackrx += config.L_EACK*n_dao
        etx = ns.get_etx(path[-1], path[-2])
        if(dao):
            path[-2].daotx += l_dao*n_dao*etx
            path[-1].daorx += l_dao*n_dao
        else:
            path[-2].dao_acktx += l_dao*n_dao*etx
            path[-1].dao_ackrx += l_dao*n_dao
        path[-1].eacktx += config.L_EACK*n_dao        
        path[-2].eackrx += config.L_EACK*n_dao

###
# Get DAO bytes during prediction interval
# Input:    nodes, prediction interval (p_time), optional telemetry enabled (opt_tel)
# Output:   TX and RX bytes for every node in nodes
###
def get_daos(nodes):
    ti = config.P_INTERVAL*1000.0
    dao = config.DAO_PERIOD*1000.0
    daos = []
    for n in nodes:
        if(config.DAO_INT and (n.lastdao != None) and (n.updtime != None)):
            to = n.predtime - (n.lastdao + np.floor((n.predtime-n.lastdao)/dao)*dao)
            n_dao = np.floor((ti+to)/dao)
        else:
            n_dao = ti/dao
        if(n.id != config.ROOT):
            # Account for INT bytes
            l_dao = config.L_DAO_S + 23 + n.n + len(n.rt)*2
            path = get_multihop_path(n,ns.search_node(config.ROOT))
            get_multihop_dao_bytes(path,n_dao,l_dao,1)
            get_multihop_dao_bytes(path[::-1],n_dao,config.L_DAO_ACK,0)
            
############
### MAIN ###
############

ns.init(1)
if(not config.RT):
    ns.logfile = open(config.SIM_DIR + "/topology.log","r")
    ns.logsize = len(ns.logfile.readlines())
    ns.logfile.seek(0)
    print("Parsing root logfile...")
with open('predictions.csv', 'w', newline='') as csvfile:
    predwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    predwriter.writerow(['Time','Node_ID','EB_TX','EACK_TX','EACK_RX','EB_RX','DIO_TX','DIO_RX','DAO_TX','DAO_RX','DAO_ACK_TX','DAO_ACK_RX','CoAP_TX','CoAP_RX','Total_TX','Total_RX','Total'])
    
    while(ns.cont):
        # Start reading logfile
        ns.read = True
        # Reset estimated bytes
        for n in ns.nodes:
            n.reset_bytecount()
        # Get topology from logfile
        parse_log.update_topology(config.RT)
        # Estimate EB bytes
        get_eb_bytes(ns.nodes)
        # Estimate DIO bytes
        get_dio_bytes(ns.nodes)
        # Estimate DAO bytes         
        get_daos(ns.nodes)
        # Estimate CoAP bytes
        get_p2p_coap_bytes(ns.nodes, config.L_COAP_RQ, config.L_COAP_RP)
        if(len(ns.nodes) == config.N):
            totalint = 0
            numberint = 0
            for n in ns.nodes:
                if(config.RT):
                    n.print_n(1, 1, config.P_INTERVAL)
                predwriter.writerow([int(n.predtime),n.id,float(n.ebtx),float(n.ebrx),int(n.eacktx),int(n.eackrx),int(n.diotx),int(n.diorx),int(n.daotx),int(n.daorx),int(n.dao_acktx),int(n.dao_ackrx),int(n.coaptx),int(n.coaprx),int(n.ebtx+n.eacktx+n.diotx+n.daotx+n.dao_acktx+n.coaptx),int(n.ebrx+n.eackrx+n.diorx+n.daorx+n.dao_ackrx+n.coaprx), int(n.ebtx+n.eacktx+n.diotx+n.daotx+n.dao_acktx+n.coaptx+n.ebrx+n.eackrx+n.diorx+n.daorx+n.dao_ackrx+n.coaprx)])
                totalint += sum(n.intbytes[1])
                numberint = len(n.intbytes[1])
            predwriter.writerow([0,'Node_ID','EB_TX','EB_RX','EACK_TX','EACK_RX','DIO_TX','DIO_RX','DAO_TX','DAO_RX','DAO_ACK_TX','DAO_ACK_RX','CoAP_TX','CoAP_RX','Total_TX','Total_RX','Total'])  
