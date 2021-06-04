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
SF_SIZE         = 7         # Default 6TiSCH Minimal schedule contiki-NG
TS_SIZE         = 0.01      # Default 2.4 GHz timeslot
L_EB            = 37        # Beacon length
L_MAC_HDR       = 23        # MAC header

# RPL #
Imin            = 0.08
Imax            = 1048.0    
k               = 10.0      # Default = 10
L_DIO           = 96        # DIO length
DAO_PERIOD      = 28.0*60   # DAG lifetime, 30-1/2 minutes
L_DAO           = 85        # DAO length
L_DAO_ACK       = 43        # DAO ACK length

# UDP
UDP_PERIOD      = 60        # 1 minute
L_UDP_D         = 50        # UDP length direct link
L_UDP_MF        = 58        # UDP length multihop first link
L_UDP_MI        = 67        # UDP length multihop intermediate link
L_UDP_ML        = 59        # UDP length multihop last link
L_TOT_HDR       = 49        # Total header

# CoAP
CoAP_PERIOD     = 60        # 1 minute
# L_CoAP_RQ       = 65        # CoAP request length direct link
# L_CoAP_RP       = 50        # CoAP response length direct link
L_CoAP_RQ       = 16        # CoAP request payload
L_CoAP_RP       = 64        # CoAP response payload

# EACK
L_EACK          = 19        # EACK length

# PREDICTION
#TIME            = 60*60     # Prediction time (minutes)
TIME            = 60*20

#################
### Functions ###
#################

def search_node(nodes,n):
    if(len(nodes) != 0):
        for i in range(0,len(nodes)):
            if(n == nodes[i].id):
                return i
    return -1

# get combinations and rest #
# def p_combinations(N):
#     M = range(0,N)
#     cs = []
#     for i in range(0,int(k)):
#         for c in combinations(M,i):
#             t = copy.copy(M)
#             r = []
#             for e in c:
#                 r.append(e)
#                 t.remove(e)
#             cs.append([r,t])   
#     return cs

# get P(DIO) for all nodes #
def get_pdios(nodes):
    for n in nodes:
        n.pdio = 1
    # eqs = []
    # s = ""
    # for n in nodes:
    #     s += "p" + str(n.id) + ", "
    #     if n.n < k:
    #         n.pdio = 1
    #         eqs.append(Eq(parse_expr("p" + str(n.id) + "-1"),0))
    #     else:
    #         eqs.append(n.get_p())
    # s = s[:-2]
#     # TODO: find different (faster) solver for Real domain
#     # p1, p2, p3, p4, p5, p6 = symbols(s)
#     # pdios = solve(eqs,(p1,p2,p3,p4,p5,p6))[0]
#     # for i in range(0,len(nodes)):
#     #     nodes[i].pdio = pdios[i]

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
    if(sender.id != 1):
        next_hop = sender.pn
        while((next_hop.id != 1) and (next_hop.id != receiver.id)):
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
    if(receiver.id == 1):
        return uplink, downlink
    downlink.append(receiver)
    next_hop = receiver.pn
    while((next_hop.id != 1) and (next_hop.id != sender.id)):
        downlink.append(next_hop)
        next_hop = next_hop.pn
    if(next_hop.id == sender.id):
        downlink.append(next_hop)
    else:
        downlink.append(next_hop)
        temp = []
        temp.append(sender)
        next_hop = sender.pn
        while(next_hop.id != 1):
            temp.append(next_hop)
            next_hop = next_hop.pn
        downlink = np.concatenate((downlink,temp[::-1]))
    return uplink, downlink

def get_source_routing_header(node, is_p2p):
    hops = 1
    if(node.pn.id == 1):
        hops = 1
    else:
        next_hop = node.pn 
        hops += 1
        while(next_hop.pn.id != 1):
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

def get_source_routing_header_hops(hops):
    SRH_F = (hops-1)*8
    SRH_I =  SRH_F + 9 
    SRH_L = SRH_I
    RQ_F = 8
    RQ_I = RQ_F + 9
    RQ_L = RQ_I - 8
    return SRH_F, SRH_I, SRH_L, RQ_F, RQ_I, RQ_L

###
# Get Source Routing Header and Hop-2-hop header from path
# Input:    Path - array of nodes
# Output:   SRH and H2H for first, intermediate and last hops, path type, #uplink hops and #downlink hops
###
def get_srh_h2h(path):
    path_type = 0           #0 = uplink non-P2P, 1 = downlink non-P2P, 2 = P2P with root, 3 = P2P without root
    # Uplink non-P2P path
    if(path[-1].id == 1):
        H2H_F = 8
        H2H_I = H2H_F + 9
        H2H_L = H2H_I - 8
        SRH_F, SRH_I, SRH_L = 0, 0, 0
        path_type = 0
        uplink_hops = len(path)-1
        downlink_hops = 0
    # Downlink non-P2P path
    elif(path[0].id == 1):
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

# def get_multihop_coap_bytes(node, rq_payload, rp_payload, mac_hdr, tot_hdr, is_p2p):
#     #s_request, mhf_request, mhi_request, mhl_request = request
#     #s_response, mhf_response, mhi_response, mhl_response = response
#     # Get Source Routing Header and hop-to-hop header
#     SRH_F, SRH_I, SRH_L, RQ_F, RQ_I, RQ_L = get_source_routing_header(node, 0)
#     # Get total request frames
#     s_request = get_fragmenting(rq_payload, mac_hdr, tot_hdr, 0)
#     mhf_request = get_fragmenting(rq_payload, mac_hdr, tot_hdr, RQ_F)
#     mhi_request = get_fragmenting(rq_payload, mac_hdr, tot_hdr, RQ_I)
#     mhl_request = get_fragmenting(rq_payload, mac_hdr, tot_hdr, RQ_L)
#     s_response = get_fragmenting(rp_payload, mac_hdr, tot_hdr, 0)
#     mhf_response = get_fragmenting(rp_payload, mac_hdr, tot_hdr, SRH_F)
#     mhi_response = get_fragmenting(rp_payload, mac_hdr, tot_hdr, SRH_I)
#     mhl_response = get_fragmenting(rp_payload, mac_hdr, tot_hdr, SRH_L)
#     if(node.pn.id == 1):
#         if(is_p2p):
#             node.coaptx += sum(mhf_request)                                                 # Client request
#             nodes.nodes[search_node(nodes.nodes,1)].eacktx += len(mhf_request)*L_EACK       # ACK response
#             nodes.nodes[search_node(nodes.nodes,1)].coaptx += sum(mhl_response)             # Server response
#             node.eacktx += len(mhl_response)*L_EACK                                         # ACK request
#         else:
#             node.coaptx += sum(s_request)                                                   # Client request
#             nodes.nodes[search_node(nodes.nodes,1)].eacktx += len(s_request)*L_EACK         # ACK response
#             nodes.nodes[search_node(nodes.nodes,1)].coaptx += sum(s_response)               # Server response
#             node.eacktx += len(s_response)*L_EACK                                           # ACK request
#     else:
#         node.coaptx += sum(mhf_request)                                                     # Client request
#         node.eacktx += len(mhl_response)*L_EACK                                             # ACK response
#         next_hop = node.pn           
#         next_hop.coaptx += sum(mhl_response)                                                # Server response
#         next_hop.eacktx += len(mhf_request)*L_EACK                                          # ACK request
#         while(next_hop.pn.id != 1):
#             next_hop.coaptx += sum(mhi_request)                                             # Client request
#             next_hop.eacktx += len(mhi_response)*L_EACK                                     # ACK response
#             next_hop = next_hop.pn
#             next_hop.coaptx += sum(mhi_response)                                            # Server response
#             next_hop.eacktx += len(mhi_request)*L_EACK                                      # Ack request
#         next_hop.coaptx += sum(mhl_request)                                                 # Client request
#         next_hop.eacktx += len(mhf_response)*L_EACK                                         # ACK response
#         nodes.nodes[search_node(nodes.nodes,1)].coaptx += sum(mhf_response)                 # Server response
#         nodes.nodes[search_node(nodes.nodes,1)].eacktx += len(mhl_request)*L_EACK           # Ack request 

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
            while(path[i].id != 1):
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
    
# def get_coap_bytes(node, rq_payload, rp_payload, mac_hdr, tot_hdr, is_p2p):
#     # Get Source Routing Header and hop-to-hop header
#     SRH_F, SRH_I, SRH_L, RQ_F, RQ_I, RQ_L = get_source_routing_header(node, is_p2p)
#     # Get total request frames
#     request_frames = get_fragmenting(rq_payload, mac_hdr, tot_hdr, 0)
#     mhf_request_frames = get_fragmenting(rq_payload, mac_hdr, tot_hdr, RQ_F)
#     mhi_request_frames = get_fragmenting(rq_payload, mac_hdr, tot_hdr, RQ_I)
#     mhl_request_frames = get_fragmenting(rq_payload, mac_hdr, tot_hdr, RQ_L)
#     request = [request_frames, mhf_request_frames, mhi_request_frames, mhl_request_frames]
#     # Get total response frames
#     response_frames = get_fragmenting(rp_payload, mac_hdr, tot_hdr, 0)
#     mhf_response_frames = get_fragmenting(rp_payload, mac_hdr, tot_hdr, SRH_F)
#     mhi_response_frames = get_fragmenting(rp_payload, mac_hdr, tot_hdr, SRH_I)
#     mhl_response_frames = get_fragmenting(rp_payload, mac_hdr, tot_hdr, SRH_L)
#     response = [response_frames, mhf_response_frames, mhi_response_frames, mhl_response_frames]
#     get_multihop_coap_bytes(node, request, response, is_p2p)

# def get_p2p_coap_bytes(sender, receiver, rq_payload, rp_payload, mac_hdr, tot_hdr):
#     # if(sender.id != 1):
#     #     # get_coap_bytes(sender, rq_payload, rp_payload, mac_hdr, tot_hdr,1)
#     #     # get_coap_bytes(receiver, rp_payload, rq_payload, mac_hdr, tot_hdr,1)
#     #     get_multihop_coap_bytes_p2p(sender, receiver, rq_payload, rp_payload, mac_hdr, tot_hdr)
#     # else:
#     #     get_multihop_coap_bytes(receiver, rp_payload, rq_payload, mac_hdr, tot_hdr, 1)
#     #     # get_coap_bytes(receiver, rp_payload, rq_payload, mac_hdr, tot_hdr,0)

def get_p2p_coap_bytes(sender, receiver, rq_payload, rp_payload, mac_hdr, tot_hdr):
    request_path, response_path = get_multihop_path(sender, receiver)
    if(len(request_path) != 0):
        get_multihop_coap_bytes(request_path, rq_payload, mac_hdr, tot_hdr)
    if(len(response_path) != 0):
        get_multihop_coap_bytes(response_path, rp_payload, mac_hdr, tot_hdr)

def get_multihop_dao_bytes(node, L_RQ, L_RP):
    SRH_F, SRH_I, SRH_L, RQ_F, RQ_I, RQ_L = get_source_routing_header(node,0)
    L_RQ_MF = L_RQ + RQ_F
    L_RQ_MI = L_RQ + RQ_I
    L_RQ_ML = L_RQ + RQ_L
    L_RP_MF = L_RP + SRH_F
    L_RP_MI = L_RP + SRH_I
    L_RP_ML = L_RP + SRH_L
    if(node.pn.id == 1):
        node.daotx += L_RQ                                        
        nodes.nodes[search_node(nodes.nodes,1)].eacktx += L_EACK    
        nodes.nodes[search_node(nodes.nodes,1)].dao_acktx += L_RP     
        node.eacktx += L_EACK                                       
    else:
        node.daotx += L_RQ_MF                                     
        node.eacktx += L_EACK                                      
        next_hop = node.pn           
        next_hop.dao_acktx += L_RP_ML                                
        next_hop.eacktx += L_EACK                                  
        while(next_hop.pn.id != 1):
            next_hop.daotx += L_RQ_MI                           
            next_hop.eacktx += L_EACK                           
            next_hop = next_hop.pn
            next_hop.dao_acktx += L_RP_MI                           
            next_hop.eacktx += L_EACK                              
        next_hop.daotx += L_RQ_ML                                  
        next_hop.eacktx += L_EACK                                 
        nodes.nodes[search_node(nodes.nodes,1)].dao_acktx += L_RP_MF
        nodes.nodes[search_node(nodes.nodes,1)].eacktx += L_EACK

def get_eb_bytes(nodes):
    for n in nodes:
        n.ebtx += L_EB

def get_dio_bytes(nodes):
    for n in nodes:
        n.diotx += L_DIO*n.pdio

def get_daos(nodes, est_time, dao_period):
    daos = []
    for n in nodes:
        if((n.lastdao != None) and (n.toptime != None)):
            final = n.toptime/1000 + est_time
            dao = int(np.floor((final-n.lastdao/1000)/dao_period))
        else:
            dao = int(np.floor(est_time/dao_period))
        daos.append(dao)
    return daos
            
############
### MAIN ###
############
coap_periods = int(np.floor(TIME/CoAP_PERIOD))
eb_periods = int(np.floor(TIME/EB_PERIOD))
dio_periods = int(np.floor(TIME/Imax))
dao_periods = int(np.floor(TIME/DAO_PERIOD))

with open('predictions.csv', 'w', newline='') as csvfile:
    predwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    predwriter.writerow(['Time', 'Node_ID', 'EB_TX', 'EACK_TX', 'DIO_TX', 'DIS_TX', 'DAO_TX', 'DAO_ACK_TX', 'CoAP_TX'])

    nodes.init()
    while(1):
        # Start reading logfile
        nodes.read = 1
        # Reset estimated bytes
        for n in nodes.nodes:
            n.reset_bytecount()
        # Get topology from logfile
        parse_log.update_topology()
        # Get P(DIO)
        get_pdios(nodes.nodes)
        # Estimate EB bytes
        for i in range(0, eb_periods):
            get_eb_bytes(nodes.nodes)
        # Estimate DIO bytes
        for i in range(0, dio_periods):
            get_dio_bytes(nodes.nodes)
        # Estimate CoAP bytes
        for i in range(0,coap_periods):
            for n in nodes.nodes:
                # if(n.id != 1):
                #     get_coap_bytes(n, L_CoAP_RQ, L_CoAP_RP, L_MAC_HDR, L_TOT_HDR,0)  
                if(n.id != 8):
                    get_p2p_coap_bytes(n, nodes.nodes[search_node(nodes.nodes,8)], L_CoAP_RQ, L_CoAP_RP, L_MAC_HDR, L_TOT_HDR) 
        # Estimate DAO bytes         
        daos = get_daos(nodes.nodes, TIME, DAO_PERIOD)
        for i in range(0,len(nodes.nodes)):
            if(nodes.nodes[i].id != 1):
                for j in range(0,daos[i]):
                    get_multihop_dao_bytes(nodes.nodes[i],L_DAO,L_DAO_ACK)  
        if(nodes.nodes[-1].toptime != None): 
            for n in nodes.nodes:
                n.print_n()
                predwriter.writerow([n.toptime ,n.id, n.ebtx, n.eacktx, n.diotx, n.distx, n.daotx, n.dao_acktx, n.coaptx])
            predwriter.writerow([0,0,0,0,0,0,0,0,0])
        # with open('predictions.csv', 'w', newline='') as csvfile:
        #     predwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        #     predwriter.writerow(['Node ID', 'EB TX', 'EACK TX', 'DIO TX', 'DIS TX', 'DAO TX', 'DAO ACK TX', 'CoAP TX'])
        #     for n in nodes.nodes:
        #             predwriter.writerow([n.id, n.ebtx, n.eacktx, n.diotx, n.distx, n.daotx, n.dao_acktx, n.coaptx])


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

# get_p2p_coap_bytes(nodes.nodes[search_node(nodes.nodes,2)], nodes.nodes[search_node(nodes.nodes,8)], L_CoAP_RQ, L_CoAP_RP, L_MAC_HDR, L_TOT_HDR)
# for n in nodes.nodes:
#     n.print_n()
