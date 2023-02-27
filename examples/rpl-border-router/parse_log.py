import time
import os
import re
import nodes

ROOT = 1                        # Node ID of root
INT_INTERVAL = 0                # INT interval in ms (in case of non-storing mode, only for artificially increasing the interval)

REGEXP_PRED = re.compile('^.*?INFO:\sApp\s\s\s\s\s\s\s]\sPREDICT\s(?P<time>([0-9]+))')
REGEXP_ADDR = re.compile('^.*?INFO:\sRPL\s\s\s\s\s\s\s]\slinks:\sfd00::2(?P<node>([0-9a-f]+))')
REGEXP_PARENT = re.compile('^.*?INFO:\sRPL\s\s\s\s\s\s\s]\slinks:\sfd00::2[0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+\s\sto\sfd00::2(?P<parent>([0-9a-f]+)):[0-9a-f]+:[0-9a-f]+:[0-9a-f]+\stime:\s(?P<topology_time>([0-9]+))')
REGEXP_RT = re.compile('^.*?WARN:\sTSCH\s\s\s\s\s\s]\sINT:\s(?P<destination>([0-9a-f]+))\svia\s(?P<neighbour>([0-9a-f]+))\svia\s(?P<node>([0-9a-f]+))')
REGEXP_NB = re.compile('^.*?WARN:\sTSCH\s\s\s\s\s\s]\sINT:\s(?P<neighbour>([0-9a-f]+))\sneighbour\sof\s(?P<node>([0-9a-f]+))')
REGEXP_INTMULTI = re.compile('^.*?WARN:\sTSCH\s\s\s\s\s\s]\sINT:\sRECEIVED\sINT\sfrom\snode\s(?P<node>([0-9a-f]+)):\sseqno:\s[0-9a-f]+\slen\s(?P<len>([0-9]+))\sASN\s(?P<node_asn_ms1b>([0-9]+))\s(?P<node_asn_ls4b>([0-9]+))\sETX\s(?P<etx>([0-9]+))\sDAO\sASN\s(?P<dao_asn_ms1b>([0-9]+))\s(?P<dao_asn_ls4b>([0-9]+))\sEB\sgen\sASN\s(?P<eb_gen_asn_ms1b>([0-9]+))\s(?P<eb_gen_asn_ls4b>([0-9]+))\sEB\stx\sASN\s(?P<eb_tx_asn_ms1b>([0-9]+))\s(?P<eb_tx_asn_ls4b>([0-9]+))\sTS\s(?P<time_source>([0-9a-f]+))\sPP\s(?P<parent>([0-9a-f]+))')
REGEXP_INTMULTI_NS = re.compile('^.*?WARN:\sTSCH\s\s\s\s\s\s]\sINT:\sRECEIVED\sINT\sfrom\snode\s(?P<node>([0-9a-f]+)):\sseqno:\s[0-9a-f]+\slen\s(?P<len>([0-9]+))\sASN\s(?P<node_asn_ms1b>([0-9]+))\s(?P<node_asn_ls4b>([0-9]+))\sETX\s(?P<etx>([0-9]+))\sDAO\sASN\s(?P<dao_asn_ms1b>([0-9]+))\s(?P<dao_asn_ls4b>([0-9]+))\sEB\sgen\sASN\s(?P<eb_gen_asn_ms1b>([0-9]+))\s(?P<eb_gen_asn_ls4b>([0-9]+))\sEB\stx\sASN\s(?P<eb_tx_asn_ms1b>([0-9]+))\s(?P<eb_tx_asn_ls4b>([0-9]+))\sTS\s(?P<time_source>([0-9a-f]+))')
REGEXP_INTROOT = re.compile('^.*?WARN:\sTSCH\s\s\s\s\s\s]\sINT:\sROOT\sDIO\sASN\s(?P<dio_asn_ms1b>([0-9]+))\s(?P<dio_asn_ls4b>([0-9]+))\sEB\sgen\sASN\s(?P<eb_gen_asn_ms1b>([0-9]+))\s(?P<eb_gen_asn_ls4b>([0-9]+))\sEB\stx\sASN\s(?P<eb_tx_asn_ms1b>([0-9]+))\s(?P<eb_tx_asn_ls4b>([0-9]+))')

def hex2dec(hex):
    temp = "0x" + hex
    dec = int(temp,16)
    return dec

def follow(thefile):
    thefile.seek(0, os.SEEK_END)
    while nodes.read:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

def read_logline(line):
    chomped_line = line.rstrip()
    # Prediction update
    matchpred = re.match(REGEXP_PRED, chomped_line)
    if(matchpred):
        t = float(matchpred.group("time"))
        for n in nodes.nodes:
            n.predtime = t
        nodes.read = 0
    # INT update
    if(nodes.mop == 1):
        matchint = re.match(REGEXP_INTMULTI, chomped_line)
    else:
        matchint = re.match(REGEXP_INTMULTI_NS, chomped_line)
    if(matchint):
        n = (int)(matchint.group("node"))
        node_asn_ms1b = (int)(matchint.group("node_asn_ms1b"))
        node_asn_ls4b = (int)(matchint.group("node_asn_ls4b"))
        etx = (int)(matchint.group("etx"))
        length = (int)(matchint.group("len"))
        dao_asn_ms1b = (int)(matchint.group("dao_asn_ms1b"))
        dao_asn_ls4b = (int)(matchint.group("dao_asn_ls4b"))
        ebgen_asn_ms1b = (int)(matchint.group("eb_gen_asn_ms1b"))
        ebgen_asn_ls4b = (int)(matchint.group("eb_gen_asn_ls4b"))
        ebtx_asn_ms1b = (int)(matchint.group("eb_tx_asn_ms1b"))
        ebtx_asn_ls4b = (int)(matchint.group("eb_tx_asn_ls4b"))
        ts = (int)(matchint.group("time_source"))

        node = nodes.search_node(n)
        root = nodes.search_node(ROOT)
        if(node == -1):
            node = nodes.node(n)
            nodes.nodes.append(node)
        if((node.updtime == None) or ((((node_asn_ls4b+node_asn_ms1b*pow(2,32))*10)+384) > (node.updtime + INT_INTERVAL))):
            nodes.intstream = True
            if(nodes.mop == 1):
                p = int(matchint.group("parent"))
                parent = nodes.search_node(p)
                if(parent == -1):
                    parent = nodes.node(p)
                    nodes.nodes.append(parent)
                node.pn = parent
                nodes.count += 1
                # Delete current routing table, new routes will follow
                node.rt = []
                if(root != -1):
                    root.rt = []

            node.updtime = ((node_asn_ls4b+node_asn_ms1b*pow(2,32))*10)+384
            node.etx = etx/128
            node.intbytes[0].append(((node_asn_ls4b+node_asn_ms1b*pow(2,32))*10)+384)
            node.intbytes[1].append(length)
            node.lastdao = ((dao_asn_ls4b+dao_asn_ms1b*pow(2,32))*10)+384
            node.lastebgen = ((ebgen_asn_ls4b+ebgen_asn_ms1b*pow(2,32))*10)+384
            node.lastebtx = ((ebtx_asn_ls4b+ebtx_asn_ms1b*pow(2,32))*10)+384
            tsn = nodes.search_node(ts)
            if(tsn != -1):
                node.ts = tsn
            if(root != -1):
                root.updtime = ((node_asn_ls4b+node_asn_ms1b*pow(2,32))*10)+384
                root.intbytes[0].append(((node_asn_ls4b+node_asn_ms1b*pow(2,32))*10)+384)
                root.intbytes[1].append(length)
        else:
            nodes.intstream = False
    # Update root routing table
    matchrt = re.match(REGEXP_RT, chomped_line)
    if(matchrt and nodes.intstream):
        n = int(matchrt.group("node"))
        nb = int(matchrt.group("neighbour"))
        d = int(matchrt.group("destination"))
        node = nodes.search_node(n)
        nbn = nodes.search_node(nb)
        dn = nodes.search_node(d)
        if(node != -1 and nbn != -1 and dn != -1):
            node.rt.append([dn,nbn])
    # Node and preferred parent update non-storing mode
    matchadd = re.match(REGEXP_ADDR, chomped_line)
    if(matchadd):
        n = matchadd.group("node")
        n = hex2dec(n)
        node = nodes.search_node(n)
        if(node == -1):
            node = nodes.node(n) 
            nodes.nodes.append(node)
        matchp = re.match(REGEXP_PARENT, chomped_line)
        if(matchp):
            p = matchp.group("parent")
            p = hex2dec(p)
            parent = nodes.search_node(p)
            if(parent == -1):
                parent = nodes.node(p)
                nodes.nodes.append(parent)
            node.pn = parent
        nodes.count += 1
    # Root neighbour update
    matchnb = re.match(REGEXP_NB, chomped_line)
    if(matchnb and nodes.intstream):
        n = (int)(matchnb.group("node"))
        nb = (int)(matchnb.group("neighbour"))
        node = nodes.search_node(n)
        if(node != -1):
            neighbour = nodes.search_node(nb)
            if(neighbour != -1):
                node.add_neighbour(neighbour)
    # Root control traffic update
    matchrint = re.match(REGEXP_INTROOT, chomped_line)
    if(matchrint):
        dio_asn_ms1b = (int)(matchrint.group("dio_asn_ms1b"))
        dio_asn_ls4b = (int)(matchrint.group("dio_asn_ls4b"))
        ebgen_asn_ms1b = (int)(matchrint.group("eb_gen_asn_ms1b"))
        ebgen_asn_ls4b = (int)(matchrint.group("eb_gen_asn_ls4b"))
        ebtx_asn_ms1b = (int)(matchrint.group("eb_tx_asn_ms1b"))
        ebtx_asn_ls4b = (int)(matchrint.group("eb_tx_asn_ls4b"))
        node = nodes.search_node(ROOT)
        if(node != -1):
            node.lastdio = ((dio_asn_ls4b+dio_asn_ms1b*pow(2,32))*10)+384
            node.lastebgen = ((ebgen_asn_ls4b+ebgen_asn_ms1b*pow(2,32))*10)+384
            node.lastebtx = ((ebtx_asn_ls4b+ebtx_asn_ms1b*pow(2,32))*10)+384

def update_topology(realtime):
    if(realtime):
        logfile = open("topology.log","r")
        loglines = follow(logfile)
        nodes.count = 0
        for line in loglines:
            read_logline(line)
    else:
        while nodes.read and nodes.cont:
            line = nodes.logfile.readline()
            nodes.count = 0
            read_logline(line)
            if(nodes.logcount == nodes.logsize):
                nodes.cont = 0
            nodes.logcount += 1