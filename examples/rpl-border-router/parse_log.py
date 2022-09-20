from datetime import datetime
import time
import os
import re
import nodes
import numpy as np

class node:
    def __init__(self, id):
        self.id = id            # Node ID
        self.n = 0              # Number of neighbours
        self.ns = []            # Neighbours
        self.pn = None          # Preferred parent
        self.coaptx = 0         # Amount of TX bytes due to CoAP traffic
        self.ebtx = 0           # Amound of TX bytes due to EB traffic
        self.diotx = 0          # Amount of TX bytes due to DIO traffic
        self.daotx = 0          # Amount of TX bytes due to DAO traffic
        self.dao_acktx = 0      # Amount of TX bytes due to DAO ACK traffic
        self.eacktx = 0         # Amount of TX bytes due to EACK traffic
        self.lastdao = None     # Node time of last DAO transmission
        self.lastdio = None     # Node time of last DIO transmission
        self.lastebgen = None   # Node time of last EB generation
        self.lastebtx = None    # Node time of last EB transmission
        self.updtime = None     # Node time of last INT update
        self.predtime = None    # Time of prediction
        self.coaptimes = []
        self.coaplengths = []
        self.coapresptimes = []
        self.coapresplengths = []
        ###TODO: include routing table and DAO parents for storing-mode ###
        self.rt = []        # Routing table

    def update_parent(self, pn):
        self.pn = pn

    def add_neighbour(self, neighbour):
        if(np.any(np.isin(self.ns,neighbour)) == 0):
            self.ns = np.append(self.ns,neighbour)
            self.n = len(self.ns)

    ###TODO: include update_n for storing-mode ###
    def update_rt(self, dest, router):
        self.rt.append([dest, router])

    def reset_bytecount(self):
        self.coaptx = 0
        self.ebtx = 0
        self.diotx = 0     
        self.daotx = 0  
        self.dao_acktx = 0 
        self.eacktx = 0

    def update_dao_time(self, new_time):
        self.lastdao = new_time

    def update_topology_time(self, new_time):
        self.updtime = new_time

    def update_coap(self, new_time, new_length):
        self.coaptimes.append(new_time)
        self.coaplengths.append(new_length)

    def update_coapresp(self, new_time, new_length):
        self.coapresptimes.append(new_time)
        self.coapresplengths.append(new_length)

    def print_n_test(self):
        print("----------")
        print("Node " + str(self.id))
        if(self.pn != None):
            print("Preferred parent: " + str(self.pn.id))
        if(len(self.rt) != 0):
            print("Routes: ")
            for r in self.rt:
                print("\t" + str(r[0].id) + " via " + str(r[1].id))


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
        print("COAP requests: " + str(len(self.coaptimes)))
        print("COAP responses: " + str(len(self.coapresptimes)))
        print("1 hour prediction: ")
        print("EB bytes: \t" + str(self.ebtx))
        print("EACK bytes: \t" + str(self.eacktx))
        print("DIO bytes: \t" + str(self.diotx))
        print("DAO bytes: \t" + str(self.daotx))
        print("DAO ACK bytes: \t" + str(self.dao_acktx))
        print("CoAP bytes: \t" + str(self.coaptx))
        print("Total bytes: \t" + str(self.diotx + self.ebtx + self.eacktx + self.coaptx + self.daotx + self.dao_acktx + self.diotx))

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

REGEXP_PRED = re.compile('^.*?INFO:\sApp\s\s\s\s\s\s\s]\sPREDICT\s(?P<time>([0-9]+))')
REGEXP_ADDR = re.compile('^.*?INFO:\sRPL\s\s\s\s\s\s\s]\slinks:\sfd00::2(?P<node>([0-9a-f]+))')
REGEXP_PARENT = re.compile('^.*?INFO:\sRPL\s\s\s\s\s\s\s]\slinks:\sfd00::2[0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+\s\sto\sfd00::2(?P<parent>([0-9a-f]+)):[0-9a-f]+:[0-9a-f]+:[0-9a-f]+\stime:\s(?P<topology_time>([0-9]+))')
REGEXP_NB = re.compile('^.*?WARN:\sTSCH\s\s\s\s\s\s]\sINT:\s(?P<neighbour>([0-9a-f]+))\sneighbour\sof\s(?P<node>([0-9a-f]+))')
REGEXP_INT = re.compile('^.*?WARN:\sTSCH\s\s\s\s\s\s]\sINT:\sRECEIVED\sINT\sfrom\snode\s(?P<node>([0-9a-f]+)):\sseqno:\s[0-9a-f]+\slen\s[0-9a-f]+\sASN\s(?P<node_asn_ms1b>([0-9]+))\s(?P<node_asn_ls4b>([0-9]+))')
REGEXP_DAOTX = re.compile('^.*?WARN:\sTSCH\s\s\s\s\s\s]\sINT:\slast\sDAO\sof\s(?P<node>([0-9a-f]+))\sat\sASN\s(?P<dao_asn_ms1b>([0-9]+))\s(?P<dao_asn_ls4b>([0-9]+))')
REGEXP_DIOTX = re.compile('^.*?WARN:\sTSCH\s\s\s\s\s\s]\sINT:\slast\sDIO\sof\s(?P<node>([0-9a-f]+))\sat\sASN\s(?P<dio_asn_ms1b>([0-9]+))\s(?P<dio_asn_ls4b>([0-9]+))')
REGEXP_EBGEN = re.compile('^.*?WARN:\sTSCH\s\s\s\s\s\s]\sINT:\slast\sEB\sgeneration\sof\s(?P<node>([0-9a-f]+))\sat\sASN\s(?P<ebgen_asn_ms1b>([0-9]+))\s(?P<ebgen_asn_ls4b>([0-9]+))')
REGEXP_EBTX = re.compile('^.*?WARN:\sTSCH\s\s\s\s\s\s]\sINT:\slast\sEB\stransmission\sof\s(?P<node>([0-9a-f]+))\sat\sASN\s(?P<ebtx_asn_ms1b>([0-9]+))\s(?P<ebtx_asn_ls4b>([0-9]+))')
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
        match = re.match(REGEXP_PRED, chomped_line)
        if(match):
            t = float(match.group("time"))
            for n in nodes.nodes:
                n.predtime = t
            nodes.read = 0
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
                parent_place = search_node(nodes.nodes,p)
                if(parent_place == -1):
                    nodes.nodes.append(node(p))
                    parent_place = len(nodes.nodes)-1
                nodes.nodes[node_place].update_parent(nodes.nodes[parent_place])
            nodes.count += 1
        matchnb = re.match(REGEXP_NB, chomped_line)
        if(matchnb):
            n = (int)(matchnb.group("node"))
            nb = (int)(matchnb.group("neighbour"))
            node_place = search_node(nodes.nodes,n)
            if(node_place != -1):
                neighbour_place = search_node(nodes.nodes,nb)
                if(neighbour_place != -1):
                    nodes.nodes[node_place].add_neighbour(nodes.nodes[neighbour_place])
        matchint = re.match(REGEXP_INT, chomped_line)
        if(matchint):
            n = (int)(matchint.group("node"))
            node_asn_ms1b = (int)(matchint.group("node_asn_ms1b"))
            node_asn_ls4b = (int)(matchint.group("node_asn_ls4b"))
            node_place = search_node(nodes.nodes,n)
            if(node_place != -1):
                nodes.nodes[node_place].updtime = ((node_asn_ls4b+node_asn_ms1b*pow(2,32))*10)
        matchdaotx = re.match(REGEXP_DAOTX, chomped_line)
        if(matchdaotx):
            n = (int)(matchdaotx.group("node"))
            dao_asn_ms1b = (int)(matchdaotx.group("dao_asn_ms1b"))
            dao_asn_ls4b = (int)(matchdaotx.group("dao_asn_ls4b"))
            node_place = search_node(nodes.nodes,n)
            if(node_place != -1):
                nodes.nodes[node_place].lastdao = ((dao_asn_ls4b+dao_asn_ms1b*pow(2,32))*10)
        matchdiotx = re.match(REGEXP_DIOTX, chomped_line)
        if(matchdiotx):
            n = (int)(matchdiotx.group("node"))
            dio_asn_ms1b = (int)(matchdiotx.group("dio_asn_ms1b"))
            dio_asn_ls4b = (int)(matchdiotx.group("dio_asn_ls4b"))
            node_place = search_node(nodes.nodes,n)
            if(node_place != -1):
                nodes.nodes[node_place].lastdio = ((dio_asn_ls4b+dio_asn_ms1b*pow(2,32))*10)
        matchebgen = re.match(REGEXP_EBGEN, chomped_line)
        if(matchebgen):
            n = (int)(matchebgen.group("node"))
            ebgen_asn_ms1b = (int)(matchebgen.group("ebgen_asn_ms1b"))
            ebgen_asn_ls4b = (int)(matchebgen.group("ebgen_asn_ls4b"))
            node_place = search_node(nodes.nodes,n)
            if(node_place != -1):
                nodes.nodes[node_place].lastebgen = ((ebgen_asn_ls4b+ebgen_asn_ms1b*pow(2,32))*10)
        matchebtx = re.match(REGEXP_EBTX, chomped_line)
        if(matchebtx):
            n = (int)(matchebtx.group("node"))
            ebtx_asn_ms1b = (int)(matchebtx.group("ebtx_asn_ms1b"))
            ebtx_asn_ls4b = (int)(matchebtx.group("ebtx_asn_ls4b"))
            node_place = search_node(nodes.nodes,n)
            if(node_place != -1):
                nodes.nodes[node_place].lastebtx = ((ebtx_asn_ls4b+ebtx_asn_ms1b*pow(2,32))*10)
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