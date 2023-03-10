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
# Input:    nodes
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
# Input:    nodes
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
# Get multihop non-storing mode path from sender to receiver
# Input:    sender and receiver nodes
# Output:   path from sender to receiver
###
def get_multihop_path(sender, receiver):
    uplink, downlink = [], []
    if(sender.id == receiver.id):
        return uplink, downlink
    # Uplink
    uplink.append(sender)
    if(sender.id != config.ROOT):
        next_hop = sender.pn
        while((next_hop.id != config.ROOT) and (next_hop.id != receiver.id)):
            uplink.append(next_hop)
            next_hop = next_hop.pn
        if(next_hop.id == receiver.id):
            uplink.append(next_hop)
        else:
            uplink.append(next_hop)
            temp = []
            temp.append(receiver)
            next_hop = receiver.pn
            while(next_hop.id != 1):
                temp.append(next_hop)
                next_hop = next_hop.pn
            uplink = np.concatenate((uplink,temp[::-1]))
    else:
        temp = []
        temp.append(receiver)
        next_hop = receiver.pn
        while(next_hop.id != 1):
            temp.append(next_hop)
            next_hop = next_hop.pn
        uplink = np.concatenate((uplink,temp[::-1]))
    # Downlink
    if(receiver.id == config.ROOT):
        return uplink, downlink
    downlink.append(receiver)
    next_hop = receiver.pn
    while((next_hop.id != config.ROOT) and (next_hop.id != sender.id)):
        downlink.append(next_hop)
        next_hop = next_hop.pn
    if(next_hop.id == sender.id):
        downlink.append(next_hop)
    else:
        downlink.append(next_hop)
        temp = []
        temp.append(sender)
        next_hop = sender.pn
        while(next_hop.id != config.ROOT):
            temp.append(next_hop)
            next_hop = next_hop.pn
        downlink = np.concatenate((downlink,temp[::-1]))
    return uplink, downlink

###
# Get Source Routing Header and Hop-2-hop header for DAO
# Input:    
# Output:   
###
def get_source_routing_header(node, is_p2p):
    hops = 1
    if(node.pn.id == 1):
        hops = 1
    else:
        next_hop = node.pn 
        hops += 1
        while(next_hop.pn.id != config.ROOT):
            next_hop = next_hop.pn
            hops += 1
    RQ_F = 8
    RQ_I = RQ_F + 9
    if(is_p2p):
        SRH_F = (hops-1)*8 + 9
        SRH_I = SRH_F
        RQ_L = RQ_I
    else:
        SRH_F = (hops-1)*8
        SRH_I =  SRH_F + 9
        RQ_L = RQ_I - 8
    SRH_L = SRH_I
    return SRH_F, SRH_I, SRH_L, RQ_F, RQ_I, RQ_L

###
# Get Source Routing Header and Hop-2-hop header from path
# Input:    Path - array of nodes
# Output:   SRH and H2H for first, intermediate and last hops, path type, #uplink hops and #downlink hops
###
def get_srh_h2h(path):
    path_type = 0           #0 = uplink non-P2P, 1 = downlink non-P2P, 2 = P2P with root, 3 = P2P without root
    # Uplink non-P2P path
    if(path[-1].id == config.ROOT):
        H2H_F = 8
        H2H_I = H2H_F + 9
        H2H_L = H2H_I - 8
        SRH_F, SRH_I, SRH_L = 0, 0, 0
        path_type = 0
        uplink_hops = len(path)-1
        downlink_hops = 0
    # Downlink non-P2P path
    elif(path[0].id == config.ROOT):
        SRH_F = (len(path)-2)*8
        SRH_I = SRH_F + 9
        SRH_L = SRH_I
        H2H_F, H2H_I, H2H_L = 0, 0, 0
        path_type = 1
        uplink_hops = 0
        downlink_hops = len(path)-1
    # P2P path
    else:
        uplink_hops = 0
        while((uplink_hops != len(path)-1) and (path[uplink_hops].id != 1)):
            uplink_hops += 1
        downlink_hops = len(path)-uplink_hops-1
        H2H_F = 8
        H2H_I = H2H_F + 9
        H2H_L = H2H_I
        if(downlink_hops != 0):
            SRH_F = (downlink_hops-1)*8 + 9
            SRH_I = SRH_F
            SRH_L = SRH_I
            path_type = 2
        else:
            SRH_F, SRH_I, SRH_L = 0, 0, 0
            path_type = 3
    return H2H_F, H2H_I, H2H_L, SRH_F, SRH_I, SRH_L, path_type, uplink_hops, downlink_hops

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

def get_etx(node1, node2):
    if((node1.pn != None) and (node1.pn.id == node2.id)):
        etx = max(node1.etx,1)
    elif((node2.pn != None) and (node2.pn.id == node1.id)):
        etx = max(node2.etx,1)
    else:
        etx = 1
    return etx

###
# Get CoAP bytes for a given path and payload
# Input:    Path, payload, MAC header, total header, number of CoAP messages
# Output:   TX and RX bytes for every node in path
###
def get_multihop_coap_bytes(path, payload, n_coap):
    # Get Source Routing Header and hop-to-hop header
    H2H_F, H2H_I, H2H_L, SRH_F, SRH_I, SRH_L, path_type, uplink_hops, downlink_hops = get_srh_h2h(path)
    # Get frames
    single = get_fragmenting(payload, 0)
    mhf_uplink = get_fragmenting(payload, H2H_F)
    mhi_uplink = get_fragmenting(payload, H2H_I)
    mhl_uplink = get_fragmenting(payload, H2H_L)
    mhf_downlink = get_fragmenting(payload, SRH_F)
    mhi_downlink = get_fragmenting(payload, SRH_I)
    mhl_downlink = get_fragmenting(payload, SRH_L)
    etx = 1
    # Direct link
    if(len(path) == 2):
        etx = get_etx(path[0], path[-1])
        path[0].coaptx += sum(single)*n_coap*etx
        path[-1].eacktx += len(single)*config.L_EACK*n_coap
        path[-1].coaprx += sum(single)*n_coap
        path[0].eackrx += len(single)*config.L_EACK*n_coap
    # P2P without root
    elif(path_type == 3):
        etx = get_etx(path[0], path[1])
        path[0].coaptx += sum(mhf_uplink)*n_coap*etx
        path[1].eacktx += len(mhf_uplink)*config.L_EACK*n_coap
        path[1].coaprx += sum(mhf_uplink)*n_coap
        path[0].eackrx += len(mhf_uplink)*config.L_EACK*n_coap
        for i in range(1, len(path)-2):
            etx = get_etx(path[i], path[i+1])
            path[i].coaptx += sum(mhi_uplink)*n_coap*etx
            path[i+1].eacktx += len(mhi_uplink)*config.L_EACK*n_coap
            path[i+1].coaprx += sum(mhi_uplink)*n_coap
            path[i].eackrx += len(mhi_uplink)*config.L_EACK*n_coap
        etx = get_etx(path[-1], path[-2])
        path[-2].coaptx += sum(mhl_uplink)*n_coap*etx
        path[-1].eacktx += len(mhl_uplink)*config.L_EACK*n_coap
        path[-1].coaprx += sum(mhl_uplink)*n_coap
        path[-2].eackrx += len(mhl_uplink)*config.L_EACK*n_coap
    # Uplink non-P2P
    elif(path_type == 0):
        etx = get_etx(path[0], path[1])
        path[0].coaptx += sum(mhf_uplink)*n_coap*etx
        path[1].eacktx += len(mhf_uplink)*config.L_EACK*n_coap
        path[1].coaprx += sum(mhf_uplink)*n_coap
        path[0].eackrx += len(mhf_uplink)*config.L_EACK*n_coap
        for i in range(1, len(path)-2):
            etx = get_etx(path[i], path[i+1])
            path[i].coaptx += sum(mhi_uplink)*n_coap*etx
            path[i+1].eacktx += len(mhi_uplink)*config.L_EACK*n_coap
            path[i+1].coaprx += sum(mhi_uplink)*n_coap
            path[i].eackrx += len(mhi_uplink)*config.L_EACK*n_coap
        etx = get_etx(path[-2], path[-1])
        path[-2].coaptx += sum(mhl_uplink)*n_coap*etx
        path[-1].eacktx += len(mhl_uplink)*config.L_EACK*n_coap
        path[-1].coaprx += sum(mhl_uplink)*n_coap
        path[-2].eackrx += len(mhl_uplink)*config.L_EACK*n_coap
    # Downlink non-P2P
    elif(path_type == 1):
        etx = get_etx(path[0], path[1])
        path[0].coaptx += sum(mhf_downlink)*n_coap*etx
        path[1].eacktx += len(mhf_downlink)*config.L_EACK*n_coap
        path[1].coaprx += sum(mhf_downlink)*n_coap
        path[0].eackrx += len(mhf_downlink)*config.L_EACK*n_coap
        for i in range(1, len(path)-2):
            etx = get_etx(path[i], path[i+1])
            path[i].coaptx += sum(mhi_downlink)*n_coap*etx
            path[i+1].eacktx += len(mhi_downlink)*config.L_EACK*n_coap
            path[i+1].coaprx += sum(mhi_downlink)*n_coap
            path[i].eackrx += len(mhi_downlink)*config.L_EACK*n_coap
        etx = get_etx(path[-2], path[-1])
        path[-2].coaptx += sum(mhl_downlink)*n_coap*etx
        path[-1].eacktx += len(mhl_downlink)*config.L_EACK*n_coap
        path[-1].coaprx += sum(mhl_downlink)*n_coap
        path[-2].eackrx += len(mhl_downlink)*config.L_EACK*n_coap
    # P2P with root
    elif(path_type == 2):
        # Uplink
        etx = get_etx(path[0], path[1])
        path[0].coaptx += sum(mhf_uplink)*n_coap*etx
        path[1].eacktx += len(mhf_uplink)*config.L_EACK*n_coap  
        path[1].coaprx += sum(mhf_uplink)*n_coap
        path[0].eackrx += len(mhf_uplink)*config.L_EACK*n_coap  
        i = 1          
        if(uplink_hops == 2):
            etx = get_etx(path[1], path[2])
            path[1].coaptx += sum(mhl_uplink)*n_coap*etx
            path[2].eacktx += len(mhl_uplink)*config.L_EACK*n_coap
            path[2].coaprx += sum(mhl_uplink)*n_coap
            path[1].eackrx += len(mhl_uplink)*config.L_EACK*n_coap
            i = 2
        elif(uplink_hops > 2):
            i = 2
            while(path[i].id != config.ROOT):
                etx = get_etx(path[i], path[i-1])
                path[i-1].coaptx += sum(mhi_uplink)*n_coap*etx
                path[i].eacktx += len(mhi_uplink)*config.L_EACK*n_coap
                path[i].coaprx += sum(mhi_uplink)*n_coap
                path[i-1].eackrx += len(mhi_uplink)*config.L_EACK*n_coap
                i += 1
            etx = get_etx(path[i], path[i-1])
            path[i-1].coaptx += sum(mhl_uplink)*n_coap*etx
            path[i].eacktx += len(mhl_uplink)*config.L_EACK*n_coap
            path[i].coaprx += sum(mhl_uplink)*n_coap
            path[i-1].eackrx += len(mhl_uplink)*config.L_EACK*n_coap
        # Downlink
        etx = get_etx(path[i], path[i+1])
        path[i].coaptx += sum(mhf_downlink)*n_coap*etx
        path[i+1].eacktx += len(mhf_downlink)*config.L_EACK*n_coap
        path[i+1].coaprx += sum(mhf_downlink)*n_coap
        path[i].eackrx += len(mhf_downlink)*config.L_EACK*n_coap
        i += 1
        if(downlink_hops == 2):
            etx = get_etx(path[i], path[i+1])
            path[i].coaptx += sum(mhl_downlink)*n_coap*etx
            path[i+1].eacktx += len(mhl_downlink)*config.L_EACK*n_coap
            path[i+1].coaprx += sum(mhl_downlink)*n_coap
            path[i].eackrx += len(mhl_downlink)*config.L_EACK*n_coap
            i += 1
        elif(downlink_hops > 2):
            i += 1
            while(i != len(path)-1):
                etx = get_etx(path[i], path[i-1])
                path[i-1].coaptx += sum(mhi_downlink)*n_coap*etx
                path[i].eacktx += len(mhi_downlink)*config.L_EACK*n_coap
                path[i].coaprx += sum(mhi_downlink)*n_coap
                path[i-1].eackrx += len(mhi_downlink)*config.L_EACK*n_coap
                i += 1
            etx = get_etx(path[i], path[i-1])
            path[i-1].coaptx += sum(mhl_downlink)*n_coap*etx
            path[i].eacktx += len(mhl_downlink)*config.L_EACK*n_coap
            path[i].coaprx += sum(mhl_downlink)*n_coap
            path[i-1].eackrx += len(mhl_downlink)*config.L_EACK*n_coap

###
# Get P2P CoAP bytes
# Input:    Nodes, request payload, response payload
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
            request_path, response_path = get_multihop_path(n, ns.search_node(config.SERVER))
            if(len(request_path) != 0):
                get_multihop_coap_bytes(request_path, rq_payload, n_coap)
            if(len(response_path) != 0):
                get_multihop_coap_bytes(response_path, rp_payload, n_coap)

###
# Get number DAOs within a chosen time period
# Input:    Nodes
# Output:   Number of DAOs
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
            get_multihop_dao_bytes(n,n_dao,config.L_DAO_NS,config.L_DAO_ACK)

def get_multihop_dao_bytes(node,n_dao,L_RQ, L_RP):
    SRH_F, SRH_I, SRH_L, RQ_F, RQ_I, RQ_L = get_source_routing_header(node,0)
    L_RQ_MF = L_RQ + RQ_F
    L_RQ_MI = L_RQ + RQ_I
    L_RQ_ML = L_RQ + RQ_L
    L_RP_MF = L_RP + SRH_F
    L_RP_MI = L_RP + SRH_I
    L_RP_ML = L_RP + SRH_L
    etx = 1
    root = ns.search_node(config.ROOT)
    if(node.pn.id == config.ROOT):
        etx = max(node.etx,1)
        node.daotx += L_RQ*n_dao*etx
        root.eacktx += config.L_EACK*n_dao          
        root.daorx += L_RQ*n_dao 
        node.eackrx += config.L_EACK*n_dao
        root.dao_acktx += L_RP*n_dao*etx
        node.eacktx += config.L_EACK*n_dao
        node.dao_ackrx += L_RP*n_dao
        root.eackrx += config.L_EACK*n_dao 
    else:
        etx = max(node.etx,1)
        node.daotx += L_RQ_MF*n_dao*etx                                     
        node.eacktx += config.L_EACK*n_dao                                      
        next_hop = node.pn
        next_hop.daorx += L_RQ_MF*n_dao                                     
        next_hop.eackrx += config.L_EACK*n_dao            
        next_hop.dao_acktx += L_RP_ML*n_dao*etx                                
        next_hop.eacktx += config.L_EACK*n_dao
        node.dao_ackrx += L_RP_ML*n_dao                                
        node.eackrx += config.L_EACK*n_dao                                  
        while(next_hop.pn.id != config.ROOT):
            etx = max(next_hop.etx,1)
            next_hop.daotx += L_RQ_MI*n_dao*etx                           
            next_hop.eacktx += config.L_EACK*n_dao 
            next_hop.dao_ackrx += L_RP_MI*n_dao                           
            next_hop.eackrx += config.L_EACK*n_dao                           
            next_hop = next_hop.pn            
            next_hop.daorx += L_RQ_MI*n_dao                           
            next_hop.eackrx += config.L_EACK*n_dao
            next_hop.dao_acktx += L_RP_MI*n_dao*etx                           
            next_hop.eacktx += config.L_EACK*n_dao
        etx = max(next_hop.etx,1)                              
        next_hop.daotx += L_RQ_ML*n_dao*etx                                  
        next_hop.eacktx += config.L_EACK*n_dao   
        next_hop.dao_ackrx += L_RP_MF*n_dao
        next_hop.eackrx += config.L_EACK*n_dao                                
        root.dao_acktx += L_RP_MF*n_dao*etx
        root.eacktx += config.L_EACK*n_dao
        root.daorx += L_RQ_ML*n_dao                                  
        root.eackrx += config.L_EACK*n_dao  

def get_int_bytes(nodes):
    ti = config.P_INTERVAL*1000.0
    int = config.INT_PERIOD*1000.0
    for n in nodes:
        if(n.id != config.ROOT):
            if(n.updtime != None):
                n_int = ti/int
                l_int = 16 + n.n + 8
                next_hop = n.pn
                while(next_hop.id != config.ROOT):
                    n.coaptx += n_int*l_int
                    next_hop.coaprx += n_int*l_int
                    n = next_hop
                    next_hop = next_hop.pn
                n.coaptx += n_int*l_int
                next_hop.coaprx += n_int*l_int
            
############
### MAIN ###
############

ns.init(0)
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
        # Estimate CoAP bytes
        get_p2p_coap_bytes(ns.nodes, config.L_COAP_RQ, config.L_COAP_RP)
        # Estimate DAO bytes         
        get_daos(ns.nodes)
        # Estimate INT bytes
        get_int_bytes(ns.nodes)
        if(len(ns.nodes) == config.N):
            for n in ns.nodes:
                if(config.RT):
                    n.print_n()
                predwriter.writerow([int(n.predtime),n.id,float(n.ebtx),float(n.ebrx),int(n.eacktx),int(n.eackrx),int(n.diotx),int(n.diorx),int(n.daotx),int(n.daorx),int(n.dao_acktx),int(n.dao_ackrx),int(n.coaptx),int(n.coaprx),int(n.ebtx+n.eacktx+n.diotx+n.daotx+n.dao_acktx+n.coaptx),int(n.ebrx+n.eackrx+n.diorx+n.daorx+n.dao_ackrx+n.coaprx),int(n.ebtx+n.eacktx+n.diotx+n.daotx+n.dao_acktx+n.coaptx+n.ebrx+n.eackrx+n.diorx+n.daorx+n.dao_ackrx+n.coaprx)])
            predwriter.writerow([0,'Node_ID','EB_TX','EB_RX','EACK_TX','EACK_RX','DIO_TX','DIO_RX','DAO_TX','DAO_RX','DAO_ACK_TX','DAO_ACK_RX','CoAP_TX','CoAP_RX','Total_TX','Total_RX','Total'])  
