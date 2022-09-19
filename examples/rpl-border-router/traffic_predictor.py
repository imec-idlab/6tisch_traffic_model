###############
### IMPORTS ###
###############

import numpy as np
import copy
from sympy import *
from sympy.parsing.sympy_parser import parse_expr
from itertools import combinations
import nodes
import parse_log
import csv

##################
### PARAMETERS ###
##################

# TSCH #
EB_PERIOD       = 14.0      # Default contiki-NG 16, recommended 4
L_EB            = 37        # Beacon length
L_MAC_HDR       = 23        # MAC header

# RPL #
IMAX            = 1048.0    # Trickle maximum interval
L_DIO           = 96        # DIO length
DAO_PERIOD      = 28.0*60   # DAG lifetime, 30-1/2 minutes
L_DAO           = 85        # DAO length
L_DAO_ACK       = 43        # DAO ACK length

L_TOT_HDR       = 49        # Fixed header size

# CoAP
COAP_PERIOD     = 60        # 1 minute
L_COAP_RQ       = 16        # CoAP request payload
L_COAP_RP       = 64        # CoAP response payload

# EACK
L_EACK          = 19        # EACK length

# PREDICTION
TIME            = 60*60     # Prediction time (minutes)
SERVER          = 8         # Server node ID
ROOT            = 1         # RPL root node ID

#################
### Functions ###
#################

###
# Search node in nodes
# Input:    Nodes, node ID
# Output:   Index of node in nodes
###
def search_node(nodes,n):
    if(len(nodes) != 0):
        for i in range(0,len(nodes)):
            if(n == nodes[i].id):
                return i
    return -1

###
# Get EB bytes within one EB period
# Input:    Nodes
# Output:   None
###
def get_eb_bytes(nodes):
    for n in nodes:
        n.ebtx += L_EB

###
# Get DIO bytes within one EB period
# Input:    Nodes
# Output:   None
###
def get_dio_bytes(nodes):
    for n in nodes:
        n.diotx += L_DIO

###
# Get multihop path from sender to receiver
# Input:    sender and receiver nodes
# Output:   uplink and downlink path
###
def get_multihop_path(sender, receiver):
    uplink, downlink = [], []
    if(sender.id == receiver.id):
        return uplink, downlink
    # Uplink
    uplink.append(sender)
    if(sender.id != ROOT):
        next_hop = sender.pn
        while((next_hop.id != ROOT) and (next_hop.id != receiver.id)):
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
    if(receiver.id == ROOT):
        return uplink, downlink
    downlink.append(receiver)
    next_hop = receiver.pn
    while((next_hop.id != ROOT) and (next_hop.id != sender.id)):
        downlink.append(next_hop)
        next_hop = next_hop.pn
    if(next_hop.id == sender.id):
        downlink.append(next_hop)
    else:
        downlink.append(next_hop)
        temp = []
        temp.append(sender)
        next_hop = sender.pn
        while(next_hop.id != ROOT):
            temp.append(next_hop)
            next_hop = next_hop.pn
        downlink = np.concatenate((downlink,temp[::-1]))
    return uplink, downlink

# TODO: remove this function
def get_source_routing_header(node, is_p2p):
    hops = 1
    if(node.pn.id == 1):
        hops = 1
    else:
        next_hop = node.pn 
        hops += 1
        while(next_hop.pn.id != ROOT):
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
    if(path[-1].id == ROOT):
        H2H_F = 8
        H2H_I = H2H_F + 9
        H2H_L = H2H_I - 8
        SRH_F, SRH_I, SRH_L = 0, 0, 0
        path_type = 0
        uplink_hops = len(path)-1
        downlink_hops = 0
    # Downlink non-P2P path
    elif(path[0].id == ROOT):
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
            #TODO: this conflicts with type 3 paths
            SRH_L = SRH_I
            #SRH_L = SRH_I - 8
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
def get_fragmenting(payload, mac_hdr, ipudp_hdr, srh):
    fragments = []
    tot_hdr = ipudp_hdr + srh
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
            temp = np.min([126-5-mac_hdr,payload])
            fragments.append(temp+mac_hdr+5)
            payload -= temp
    return fragments

###
# Get CoAP bytes sent for a given path and payload
# Input:    Path - array of nodes, payload, MAC header and total header
# Output:   None
###
def get_multihop_coap_bytes(path, payload, mac_hdr, tot_hdr):
    # Get Source Routing Header and hop-to-hop header
    H2H_F, H2H_I, H2H_L, SRH_F, SRH_I, SRH_L, path_type, uplink_hops, downlink_hops = get_srh_h2h(path)
    # Get frames
    single = get_fragmenting(payload, mac_hdr, tot_hdr, 0)
    mhf_uplink = get_fragmenting(payload, mac_hdr, tot_hdr, H2H_F)
    mhi_uplink = get_fragmenting(payload, mac_hdr, tot_hdr, H2H_I)
    mhl_uplink = get_fragmenting(payload, mac_hdr, tot_hdr, H2H_L)
    mhf_downlink = get_fragmenting(payload, mac_hdr, tot_hdr, SRH_F)
    mhi_downlink = get_fragmenting(payload, mac_hdr, tot_hdr, SRH_I)
    mhl_downlink = get_fragmenting(payload, mac_hdr, tot_hdr, SRH_L)
    # Direct link
    if(len(path) == 2):
        path[0].coaptx += sum(single)
        path[-1].eacktx += len(single)*L_EACK
    # P2P without root - TODO: check this
    elif(path_type == 3):
        path[0].coaptx += sum(mhf_uplink)
        path[1].eacktx += len(mhf_uplink)*L_EACK
        for i in range(1, len(path)-2):
            path[i].coaptx += sum(mhi_uplink)
            path[i+1].eacktx += len(mhi_uplink)*L_EACK
        path[-2].coaptx += sum(mhl_uplink)
        path[-1].eacktx += len(mhl_uplink)*L_EACK
    # Uplink non-P2P
    elif(path_type == 0):
        path[0].coaptx += sum(mhf_uplink)
        path[1].eacktx += len(mhf_uplink)*L_EACK
        for i in range(1, len(path)-2):
            path[i].coaptx += sum(mhi_uplink)
            path[i+1].eacktx += len(mhi_uplink)*L_EACK
        path[-2].coaptx += sum(mhl_uplink)
        path[-1].eacktx += len(mhl_uplink)*L_EACK
    # Downlink non-P2P
    elif(path_type == 1):
        path[0].coaptx += sum(mhf_downlink)
        path[1].eacktx += len(mhf_downlink)*L_EACK
        for i in range(1, len(path)-2):
            path[i].coaptx += sum(mhi_downlink)
            path[i+1].eacktx += len(mhi_downlink)*L_EACK
        path[-2].coaptx += sum(mhl_downlink)
        path[-1].eacktx += len(mhl_downlink)*L_EACK
    # P2P with root
    elif(path_type == 2):
        # Uplink
        path[0].coaptx += sum(mhf_uplink)
        path[1].eacktx += len(mhf_uplink)*L_EACK  
        i = 1          
        if(uplink_hops == 2):
            path[1].coaptx += sum(mhl_uplink)
            path[2].eacktx += len(mhl_uplink)*L_EACK
            i = 2
        elif(uplink_hops > 2):
            i = 2
            while(path[i].id != ROOT):
                path[i-1].coaptx += sum(mhi_uplink)
                path[i].eacktx += len(mhi_uplink)*L_EACK
                i += 1
            path[i-1].coaptx += sum(mhl_uplink)
            path[i].eacktx += len(mhl_uplink)*L_EACK
        # Downlink
        path[i].coaptx += sum(mhf_downlink)
        path[i+1].eacktx += len(mhf_downlink)*L_EACK
        i += 1
        if(downlink_hops == 2):
            path[i].coaptx += sum(mhl_downlink)
            path[i+1].eacktx += len(mhl_downlink)*L_EACK
            i += 1
        elif(downlink_hops > 2):
            i += 1
            while(i != len(path)-1):
                path[i-1].coaptx += sum(mhi_downlink)
                path[i].eacktx += len(mhi_downlink)*L_EACK
                i += 1
            path[i-1].coaptx += sum(mhl_downlink)
            path[i].eacktx += len(mhl_downlink)*L_EACK

###
# Get CoAP bytes from bidirectional traffic (request-response)
# Input:    Sender, receiver, request and response payload, MAC header and fixed header size
# Output:   None
###
def get_p2p_coap_bytes(sender, receiver, rq_payload, rp_payload, mac_hdr, tot_hdr):
    request_path, response_path = get_multihop_path(sender, receiver)
    if(len(request_path) != 0):
        get_multihop_coap_bytes(request_path, rq_payload, mac_hdr, tot_hdr)
    if(len(response_path) != 0):
        get_multihop_coap_bytes(response_path, rp_payload, mac_hdr, tot_hdr)

###
# Get number DAOs within a chosen time period
# Input:    Nodes, time period, DAO period
# Output:   Number of DAOs
###
def get_daos(nodes, est_time, dao_period):
    daos = []
    for n in nodes:
        if((n.lastdao != None) and (n.updtime != None)):
            final = n.updtime/1000 + est_time
            dao = int(np.floor((final-n.lastdao/1000)/dao_period))
        else:
            dao = int(np.floor(est_time/dao_period))
        daos.append(dao)
    return daos

# TODO: replace and merge this function with get_multihop_coap_bytes
def get_multihop_dao_bytes(node, L_RQ, L_RP):
    SRH_F, SRH_I, SRH_L, RQ_F, RQ_I, RQ_L = get_source_routing_header(node,0)
    L_RQ_MF = L_RQ + RQ_F
    L_RQ_MI = L_RQ + RQ_I
    L_RQ_ML = L_RQ + RQ_L
    L_RP_MF = L_RP + SRH_F
    L_RP_MI = L_RP + SRH_I
    L_RP_ML = L_RP + SRH_L
    if(node.pn.id == ROOT):
        node.daotx += L_RQ                                        
        nodes.nodes[search_node(nodes.nodes,ROOT)].eacktx += L_EACK    
        nodes.nodes[search_node(nodes.nodes,ROOT)].dao_acktx += L_RP     
        node.eacktx += L_EACK                                       
    else:
        node.daotx += L_RQ_MF                                     
        node.eacktx += L_EACK                                      
        next_hop = node.pn           
        next_hop.dao_acktx += L_RP_ML                                
        next_hop.eacktx += L_EACK                                  
        while(next_hop.pn.id != ROOT):
            next_hop.daotx += L_RQ_MI                           
            next_hop.eacktx += L_EACK                           
            next_hop = next_hop.pn
            next_hop.dao_acktx += L_RP_MI                           
            next_hop.eacktx += L_EACK                              
        next_hop.daotx += L_RQ_ML                                  
        next_hop.eacktx += L_EACK                                 
        nodes.nodes[search_node(nodes.nodes,ROOT)].dao_acktx += L_RP_MF
        nodes.nodes[search_node(nodes.nodes,ROOT)].eacktx += L_EACK
            
############
### MAIN ###
############
coap_periods = int(np.floor(TIME/COAP_PERIOD))
eb_periods = int(np.floor(TIME/EB_PERIOD))
dio_periods = int(np.floor(TIME/IMAX))
dao_periods = int(np.floor(TIME/DAO_PERIOD))

with open('predictions.csv', 'w', newline='') as csvfile:
    predwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    predwriter.writerow(['Time', 'Node_ID', 'EB_TX', 'EACK_TX', 'DIO_TX', 'DAO_TX', 'DAO_ACK_TX', 'CoAP_TX'])

    nodes.init()
    while(1):
        # Start reading logfile
        nodes.read = 1
        # Reset estimated bytes
        for n in nodes.nodes:
            n.reset_bytecount()
        # Get topology from logfile
        parse_log.update_topology()
        # Estimate EB bytes
        for i in range(0, eb_periods):
            get_eb_bytes(nodes.nodes)
        # Estimate DIO bytes
        for i in range(0, dio_periods):
            get_dio_bytes(nodes.nodes)
        # Estimate CoAP bytes
        for i in range(0,coap_periods):
            for n in nodes.nodes: 
                if(n.id != SERVER):
                    get_p2p_coap_bytes(n, nodes.nodes[search_node(nodes.nodes,SERVER)], L_COAP_RQ, L_COAP_RP, L_MAC_HDR, L_TOT_HDR) 
        # Estimate DAO bytes         
        daos = get_daos(nodes.nodes, TIME, DAO_PERIOD)
        for i in range(0,len(nodes.nodes)):
            if(nodes.nodes[i].id != ROOT):
                for j in range(0,daos[i]):
                    get_multihop_dao_bytes(nodes.nodes[i],L_DAO,L_DAO_ACK)  
        if(nodes.nodes[-1].updtime != None): 
            for n in nodes.nodes:
                n.print_n()
                predwriter.writerow([n.updtime ,n.id, n.ebtx, n.eacktx, n.diotx, n.daotx, n.dao_acktx, n.coaptx])
            predwriter.writerow([0,0,0,0,0,0,0,0])
        # with open('predictions.csv', 'w', newline='') as csvfile:
        #     predwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        #     predwriter.writerow(['Node ID', 'EB TX', 'EACK TX', 'DIO TX', 'DAO TX', 'DAO ACK TX', 'CoAP TX'])
        #     for n in nodes.nodes:
        #             predwriter.writerow([n.id, n.ebtx, n.eacktx, n.diotx, n.daotx, n.dao_acktx, n.coaptx])


### TEST SCRIPT ###
# nodes.init()
# nodes.nodes.append(parse_log.node(1))
# nodes.nodes.append(parse_log.node(2))
# nodes.nodes.append(parse_log.node(3))
# nodes.nodes.append(parse_log.node(4))
# nodes.nodes.append(parse_log.node(5))
# nodes.nodes.append(parse_log.node(6))
# nodes.nodes.append(parse_log.node(7))
# nodes.nodes.append(parse_log.node(8))
# nodes.nodes.append(parse_log.node(9))
# nodes.nodes.append(parse_log.node(10))
# nodes.nodes[search_node(nodes.nodes,2)].update_n([],nodes.nodes[search_node(nodes.nodes,1)])
# nodes.nodes[search_node(nodes.nodes,3)].update_n([],nodes.nodes[search_node(nodes.nodes,9)])
# nodes.nodes[search_node(nodes.nodes,4)].update_n([],nodes.nodes[search_node(nodes.nodes,3)])
# nodes.nodes[search_node(nodes.nodes,5)].update_n([],nodes.nodes[search_node(nodes.nodes,1)])
# nodes.nodes[search_node(nodes.nodes,6)].update_n([],nodes.nodes[search_node(nodes.nodes,3)])
# nodes.nodes[search_node(nodes.nodes,7)].update_n([],nodes.nodes[search_node(nodes.nodes,2)])
# nodes.nodes[search_node(nodes.nodes,8)].update_n([],nodes.nodes[search_node(nodes.nodes,5)])
# nodes.nodes[search_node(nodes.nodes,9)].update_n([],nodes.nodes[search_node(nodes.nodes,1)])
# nodes.nodes[search_node(nodes.nodes,10)].update_n([],nodes.nodes[search_node(nodes.nodes,1)])

# get_p2p_coap_bytes(nodes.nodes[search_node(nodes.nodes,2)], nodes.nodes[search_node(nodes.nodes,8)], L_COAP_RQ, L_COAP_RP, L_MAC_HDR, L_TOT_HDR)
# for n in nodes.nodes:
#     n.print_n()
