import time
import os
import re
import nodes
import numpy as np

class node:
    def __init__(self, id):
        self.id = id
        self.n = 0
        self.ns = []
        self.pn = None      # Preferred parent
        self.pdio = 0
        self.coaptx = 0     # Amount of TX bytes due to CoAP traffic
        self.udptx = 0      # Amount of TX bytes due to UDP traffic
        self.ebtx = 0       # Amound of TX bytes due to EB traffic
        self.diotx = 0      # Amount of TX bytes due to DIO traffic
        self.distx = 0      # Amount of TX bytes due to DIS traffic
        self.daotx = 0      # Amount of TX bytes due to DAO traffic
        self.dao_acktx = 0  # Amount of TX bytes due to DAO ACK traffic
        self.eacktx = 0     # Amount of TX bytes due to EACK traffic
        self.lastdao = None
        self.toptime = None
        self.coaptimes = []
        self.coaplengths = []
        self.coapresptimes = []
        self.coapresplengths = []

    def update_n(self, ns, pn):
        self.ns = ns
        self.n = len(ns)
        self.pn = pn

    def reset_bytecount(self):
        self.coaptx = 0
        self.udptx = 0
        self.ebtx = 0
        self.diotx = 0   
        self.distx = 0    
        self.daotx = 0  
        self.dao_acktx = 0 
        self.eacktx = 0

    def update_dao_time(self, new_time):
        self.lastdao = new_time

    def update_topology_time(self, new_time):
        self.toptime = new_time

    def update_coap(self, new_time, new_length):
        self.coaptimes.append(new_time)
        self.coaplengths.append(new_length)

    def update_coapresp(self, new_time, new_length):
        self.coapresptimes.append(new_time)
        self.coapresplengths.append(new_length)

    def print_n(self):
        print("----------")
        print("Node " + str(self.id))
        print("#Neighbours: " + str(self.n))
        string = ""
        for n in self.ns:
            string = string + str(n.id) + " "
        print("Neighbours: " + string)
        if(self.pn != None):
            print("Preferred parent: " + str(self.pn.id))
        print("P(DIO): " + str(self.pdio))

        if(self.lastdao != None):
            print("Last DAO time: " + str(self.lastdao))
        if(self.toptime != None):
            print("Current time: " + str(self.toptime))
        print("COAP requests: " + str(len(self.coaptimes)))
        print("COAP responses: " + str(len(self.coapresptimes)))
        print("1 hour prediction: ")
        print("EB bytes: \t" + str(self.ebtx))
        print("EACK bytes: \t" + str(self.eacktx))
        print("DIO bytes: \t" + str(self.diotx))
        print("DIS bytes: \t" + str(self.distx))
        print("DAO bytes: \t" + str(self.daotx))
        print("DAO ACK bytes: \t" + str(self.dao_acktx))
        #print("UDP bytes: " + str(self.udptx))
        print("CoAP bytes: \t" + str(self.coaptx))
        print("Total bytes: \t" + str(self.udptx + self.diotx + self.ebtx + self.eacktx + self.coaptx + self.daotx + self.dao_acktx + self.diotx))
        

#     def get_p(self):
#         cs = p_combinations(self.n)
#         pi = k/(self.n+1)
#         string = "-p" + str(self.id) + "+" + str(pi) + "+" + str(1-pi) + "*("
#         for c in cs:
#             if(len(c[0]) != 0):
#                 string += "+"
#                 for c1 in c[0]:
#                     string += "p" + str(self.ns[c1].id) + "*"
#                 string = string[:-1]
#                 if(len(c[1]) != 0):
#                     for c2 in c[1]:
#                         string += "*(1-p" + str(self.ns[c2].id) + ")"
#         return Eq(parse_expr(string+")"),0)

def search_node(nodes,n):
    if(len(nodes) != 0):
        for i in range(0,len(nodes)):
            if(n == nodes[i].id):
                return i
    return -1

def hex2dec(hex):
    temp = "0x" + hex
    dec = int(temp,16)
    return dec

REGEXP_ADDR = re.compile('^.*?INFO:\sRPL\s\s\s\s\s\s\s]\slinks:\sfd00::2(?P<node>([0-9a-f]+))')
REGEXP_PARENT = re.compile('^.*?INFO:\sRPL\s\s\s\s\s\s\s]\slinks:\sfd00::2[0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+\s\sto\sfd00::2(?P<parent>([0-9a-f]+)):[0-9a-f]+:[0-9a-f]+:[0-9a-f]+\stime:\s(?P<topology_time>([0-9]+))')
REGEXP_DAO = re.compile('^.*?INFO:\sRPL\s\s\s\s\s\s\s]\sreceived\sa\sDAO\sfrom\sfd00::2(?P<dao_origin>([0-9a-f]+)):[0-9a-f]+:[0-9a-f]+:[0-9a-f]+,\stime:\s(?P<dao_time>([0-9]+))')
REGEXP_COAP = re.compile('^.*?INFO:\scoap-uip\s\s]\sreceiving\sUDP\sdatagram\sfrom\s\[fd00::2(?P<coap_origin>([0-9a-f]+)):[0-9a-f]+:[0-9a-f]+:[0-9a-f]+\]:[0-9]+\stime:\s(?P<coap_time>([0-9]+))\sms,\sLength:\s(?P<coap_length>([0-9]+))')
REGEXP_COAPRESP = re.compile('^.*?INFO:\scoap-uip\s\s]\ssent\sto\scoap://\[fd00::2(?P<coap_respdest>([0-9a-f]+)):[0-9a-f]+:[0-9a-f]+:[0-9a-f]+\]:[0-9]+\s(?P<coap_resplength>([0-9]+))\sbytes,\stime:\s(?P<coap_resptime>([0-9]+))\sms')

def follow(thefile):
    thefile.seek(0, os.SEEK_END)
    while nodes.read:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

def update_topology():    
    logfile = open("topology.log","r")
    loglines = follow(logfile)
    nodes.count = 0
    for line in loglines:
        chomped_line = line.rstrip()
        match = re.match(REGEXP_ADDR, chomped_line)
        if(match):
            n = match.group("node")
            n = hex2dec(n)
            node_place = search_node(nodes.nodes,n)
            if(node_place == -1):
                nodes.nodes.append(node(n))
                node_place = len(nodes.nodes)-1
            match = re.match(REGEXP_PARENT, chomped_line)
            if(match):
                p = match.group("parent")
                p = hex2dec(p)
                p_t = float(match.group("topology_time"))
                parent_place = search_node(nodes.nodes,p)
                if(parent_place == -1):
                    nodes.nodes.append(node(p))
                    parent_place = len(nodes.nodes)-1
                nodes.nodes[node_place].update_n([],nodes.nodes[parent_place])
                nodes.nodes[node_place].update_topology_time(p_t)
            nodes.count += 1
        matchdao = re.match(REGEXP_DAO, chomped_line)
        if(matchdao):
            dao_o = matchdao.group("dao_origin")
            dao_o = hex2dec(dao_o)
            dao_t = float(matchdao.group("dao_time"))
            node_place = search_node(nodes.nodes,dao_o)
            if(node_place != -1):
                nodes.nodes[node_place].update_dao_time(dao_t)
        matchcoap = re.match(REGEXP_COAP, chomped_line)
        if(matchcoap):
            coap_o = matchcoap.group("coap_origin")
            coap_o = hex2dec(coap_o)
            coap_t = float(matchcoap.group("coap_time"))
            coap_l = int(matchcoap.group("coap_length"))
            node_place = search_node(nodes.nodes,coap_o)
            if(node_place != -1):
                nodes.nodes[node_place].update_coap(coap_t,coap_l)
        matchcoapresp = re.match(REGEXP_COAPRESP, chomped_line)
        if(matchcoapresp):
            coap_rd = matchcoapresp.group('coap_respdest')
            coap_rd = hex2dec(coap_rd)
            coap_rt = float(matchcoapresp.group("coap_resptime"))
            coap_rl = int(matchcoapresp.group("coap_resplength"))
            node_place = search_node(nodes.nodes,coap_rd)
            if(node_place != -1):
                nodes.nodes[node_place].update_coapresp(coap_rt,coap_rl)
        # if(len(nodes.nodes) == nodes.N):
        #     nodes.read = 0
        if(nodes.count == nodes.N):
            nodes.read = 0
            nodes.count = 0

### NODE TEST FUNCTIONS ###

# n1 = node(1)
# n2 = node(2)
# n3 = node(3)
# n4 = node(4)
# n5 = node(5)
# n6 = node(6)
# n7 = node(7)
# n8 = node(8)

# n2.update_n([],n1)
# n7.update_n([],n2)
# n3.update_n([],n1)
# n5.update_n([],n1)
# n8.update_n([],n5)
# n4.update_n([],n5)
# n6.update_n([],n4)