import csv
import numpy as np
import matplotlib.pyplot as plt
import sys

class node:
    def __init__(self, id):
        self.id = id
        self.times = []
        self.txeb = []
        self.txeack = []
        self.txdio = []
        self.txdao = []
        self.txdao_ack = []
        self.txcoap = []
        self.txtotal = []
        self.rxeb = []
        self.rxeack = []
        self.rxdio = []
        self.rxdao = []
        self.rxdao_ack = []
        self.rxcoap = []
        self.rxtotal = []
        self.total =[]
        self.intbytes = [[],[]]

predictions = []
actual = []

with open('predictions.csv', newline='') as csvfile:
    predreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in predreader:
        predictions.append(row)

with open('actual.csv', newline='') as csvfile:
    actreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in actreader:
        actual.append(row)

def get_nodes(preds):
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

def search_node(nodes,n):
    if(len(nodes) != 0):
        for np in nodes:
            if(np.id == n):
                return np
    return -1

def get_total_nodes(nodes):
    total_node = node(0)
    if(len(nodes) > 0):
        total_node.times = nodes[0].times.copy()
        total_node.txeb = nodes[0].txeb.copy()
        total_node.rxeb = nodes[0].rxeb.copy()
        total_node.txeack = nodes[0].txeack.copy()
        total_node.rxeack = nodes[0].rxeack.copy()
        total_node.txdio = nodes[0].txdio.copy()
        total_node.rxdio = nodes[0].rxdio.copy()
        total_node.txdao = nodes[0].txdao.copy()
        total_node.rxdao = nodes[0].rxdao.copy()
        total_node.txdao_ack = nodes[0].txdao_ack.copy()
        total_node.rxdao_ack = nodes[0].rxdao_ack.copy()
        total_node.txcoap = nodes[0].txcoap.copy()
        total_node.rxcoap = nodes[0].rxcoap.copy()
        total_node.txtotal = nodes[0].txtotal.copy()
        total_node.rxtotal = nodes[0].rxtotal.copy()
        total_node.total = nodes[0].total.copy()
        for i in range(0,len(nodes[0].times)):
            for p in range(1,len(nodes)-1):
                total_node.txeb[i] += nodes[p].txeb[i]
                total_node.rxeb[i] += nodes[p].rxeb[i]
                total_node.txeack[i] += nodes[p].txeack[i]
                total_node.rxeack[i] += nodes[p].rxeack[i]
                total_node.txdio[i] += nodes[p].txdio[i]
                total_node.rxdio[i] += nodes[p].rxdio[i]
                total_node.txdao[i] += nodes[p].txdao[i]
                total_node.rxdao[i] += nodes[p].rxdao[i]
                total_node.txdao_ack[i] += nodes[p].txdao_ack[i]
                total_node.rxdao_ack[i] += nodes[p].rxdao_ack[i]
                total_node.txcoap[i] += nodes[p].txcoap[i]
                total_node.rxcoap[i] += nodes[p].rxcoap[i]
                total_node.txtotal[i] += nodes[p].txtotal[i]
                total_node.rxtotal[i] += nodes[p].rxtotal[i]
                total_node.total[i] += nodes[p].total[i]
    return total_node

def calculate_error(actual, prediction):
    if(actual != 0):
        return min(abs(actual-prediction)/actual,1)
    elif(prediction == 0):
        return 0
    else:
        return 1
    # return abs(prediction-actual)

def plot_node(nodes_e, n, type, t_min, t_max, dest):
    node = search_node(nodes_e,n)
    plt.figure(type + " node " + str(n))
    dest = dest + type + "_node" + str(n)
    if(type == "EB"):
        plt.plot(node.times[t_min:t_max],node.txeb[t_min:t_max],label="TX")
        plt.plot(node.times[t_min:t_max],node.rxeb[t_min:t_max],label="RX")
    elif(type == "EACK"):
        plt.plot(node.times[t_min:t_max],node.txeack[t_min:t_max],label="TX")
        plt.plot(node.times[t_min:t_max],node.rxeack[t_min:t_max],label="RX")
    elif(type == "DIO"):
        plt.plot(node.times[t_min:t_max],node.txdio[t_min:t_max],label="TX")
        plt.plot(node.times[t_min:t_max],node.rxdio[t_min:t_max],label="RX")
    elif(type == "DAO"):
        plt.plot(node.times[t_min:t_max],node.txdao[t_min:t_max],label="TX")
        plt.plot(node.times[t_min:t_max],node.rxdao[t_min:t_max],label="RX")
    elif(type == "DAO ACK"):
        plt.plot(node.times[t_min:t_max],node.txdao_ack[t_min:t_max],label="TX")
        plt.plot(node.times[t_min:t_max],node.rxdao_ack[t_min:t_max],label="RX")
    elif(type == "CoAP"):
        plt.plot(node.times[t_min:t_max],node.txcoap[t_min:t_max],label="TX")
        plt.plot(node.times[t_min:t_max],node.rxcoap[t_min:t_max],label="RX")
    elif(type == "Total"):
        plt.plot(node.times[t_min:t_max],node.txtotal[t_min:t_max], label="TX")
        plt.plot(node.times[t_min:t_max],node.rxtotal[t_min:t_max], label="RX")
    else:
        print("Unsupported frame type!\n")
        return
    #plt.yscale("log")
    plt.legend()
    plt.xlabel("Time [s]")
    plt.ylabel("Error")
    #plt.show()
    plt.savefig(dest)

def print_analysis(nodes_e, type, t_min, t_max):
    t = search_node(nodes_e,0)
    if(type == "EB"):
        meantx = np.mean(t.txeb[t_min:t_max])
        meanrx = np.mean(t.rxeb[t_min:t_max])
        maxtx = np.max(t.txeb[t_min:t_max])
        maxrx = np.max(t.rxeb[t_min:t_max])
        mintx = np.min(t.txeb[t_min:t_max])
        minrx = np.min(t.rxeb[t_min:t_max])
        stdevtx = pow(np.std(t.txeb[t_min:t_max]),2)
        stdevrx = pow(np.std(t.rxeb[t_min:t_max]),2)
    elif(type == "EACK"):
        t = search_node(nodes_err,0)
        meantx = np.mean(t.txeack[t_min:t_max])
        meanrx = np.mean(t.rxeack[t_min:t_max])
        maxtx = np.max(t.txeack[t_min:t_max])
        maxrx = np.max(t.rxeack[t_min:t_max])
        mintx = np.min(t.txeack[t_min:t_max])
        minrx = np.min(t.rxeack[t_min:t_max])
        stdevtx = pow(np.std(t.txeack[t_min:t_max]),2)
        stdevrx = pow(np.std(t.rxeack[t_min:t_max]),2)
    elif(type == "DIO"):
        t = search_node(nodes_err,0)
        meantx = np.mean(t.txdio[t_min:t_max])
        meanrx = np.mean(t.rxdio[t_min:t_max])
        maxtx = np.max(t.txdio[t_min:t_max])
        maxrx = np.max(t.rxdio[t_min:t_max])
        mintx = np.min(t.txdio[t_min:t_max])
        minrx = np.min(t.rxdio[t_min:t_max])
        stdevtx = pow(np.std(t.txdio[t_min:t_max]),2)
        stdevrx = pow(np.std(t.rxdio[t_min:t_max]),2)
    elif(type == "DAO"):
        t = search_node(nodes_err,0)
        meantx = np.mean(t.txdao[t_min:t_max])
        meanrx = np.mean(t.rxdao[t_min:t_max])
        maxtx = np.max(t.txdao[t_min:t_max])
        maxrx = np.max(t.rxdao[t_min:t_max])
        mintx = np.min(t.txdao[t_min:t_max])
        minrx = np.min(t.rxdao[t_min:t_max])
        stdevtx = pow(np.std(t.txdao[t_min:t_max]),2)
        stdevrx = pow(np.std(t.rxdao[t_min:t_max]),2)
    elif(type == "DAO ACK"):
        t = search_node(nodes_err,0)
        meantx = np.mean(t.txdao_ack[t_min:t_max])
        meanrx = np.mean(t.rxdao_ack[t_min:t_max])
        maxtx = np.max(t.txdao_ack[t_min:t_max])
        maxrx = np.max(t.rxdao_ack[t_min:t_max])
        mintx = np.min(t.txdao_ack[t_min:t_max])
        minrx = np.min(t.rxdao_ack[t_min:t_max])
        stdevtx = pow(np.std(t.txdao_ack[t_min:t_max]),2)
        stdevrx = pow(np.std(t.rxdao_ack[t_min:t_max]),2)
    elif(type == "CoAP"):
        t = search_node(nodes_err,0)
        meantx = np.mean(t.txcoap[t_min:t_max])
        meanrx = np.mean(t.rxcoap[t_min:t_max])
        maxtx = np.max(t.txcoap[t_min:t_max])
        maxrx = np.max(t.rxcoap[t_min:t_max])
        mintx = np.min(t.txcoap[t_min:t_max])
        minrx = np.min(t.rxcoap[t_min:t_max])
        stdevtx = pow(np.std(t.txcoap[t_min:t_max]),2)
        stdevrx = pow(np.std(t.rxcoap[t_min:t_max]),2)
    elif(type == "Total"):
        meantx = np.mean(t.txtotal[t_min:t_max])
        meanrx = np.mean(t.rxtotal[t_min:t_max])
        maxtx = np.max(t.txtotal[t_min:t_max])
        maxrx = np.max(t.rxtotal[t_min:t_max])
        mintx = np.min(t.txtotal[t_min:t_max])
        minrx = np.min(t.rxtotal[t_min:t_max])
        stdevtx = pow(np.std(t.txtotal[t_min:t_max]),2)
        stdevrx = pow(np.std(t.rxtotal[t_min:t_max]),2)
    else:
        print("Unsupported frame type!\n")
        return
    
    print("Mean TX error: " + str(float(meantx)) + " / Mean RX error: " + str(float(meanrx)))
    print("Stdev TX error " + str(float(stdevtx)) + " / Stdev RX error: " + str(float(stdevrx)))
    print("Max TX error: " + str(float(maxtx)) + " / Max RX error: " + str(float(maxrx)))
    print("Min TX error: " + str(float(mintx)) + " / Min RX error: " + str(float(minrx)))

def print_boxplot(nodes_e, type, t_min, t_max):
    t = search_node(nodes_e,0)
    if(type == "Total"):
        with open('ns_box_stable_prr80_15min_def', 'w', newline='') as csvfile:
            boxwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for i in range(t_min,t_max):
                boxwriter.writerow([(1-t.txtotal[i])*100,(1-t.rxtotal[i])*100,(1-t.total[i])*100])

if(len(sys.argv) < 3):
    print("Missing parameter!")
else:
    destination = sys.argv[1]
    m_type = sys.argv[2]

    nodes_pred = get_nodes(predictions)
    nodes_act = get_nodes(predictions)
    nodes_err = get_nodes(predictions)

    for p in predictions:
        if((p[0] != '0') and (p[0] != 'Time')):
            n = search_node(nodes_pred,int(p[1]))
            n.times.append(int(p[0])/1000)
            n.txeb.append(float(p[2]))
            n.rxeb.append(float(p[3]))
            n.txeack.append(int(p[4]))
            n.rxeack.append(int(p[5]))
            n.txdio.append(int(p[6]))
            n.rxdio.append(int(p[7]))
            n.txdao.append(int(p[8]))
            n.rxdao.append(int(p[9]))
            n.txdao_ack.append(int(p[10]))
            n.rxdao_ack.append(int(p[11]))
            n.txcoap.append(int(p[12]))
            n.rxcoap.append(int(p[13]))
            n.txtotal.append(int(p[14]))
            n.rxtotal.append(int(p[15]))
            n.total.append(int(p[16]))

    for a in actual:
        if((a[0] != '0') and (a[0] != 'Time')):
            n = search_node(nodes_act,int(a[1]))
            n.times.append(int(a[0])/1000)
            n.txeb.append(int(a[2]))
            n.rxeb.append(int(a[3]))
            n.txeack.append(int(a[4]))
            n.rxeack.append(int(a[5]))
            n.txdio.append(int(a[6]))
            n.rxdio.append(int(a[7]))
            n.txdao.append(int(a[8]))
            n.rxdao.append(int(a[9]))
            n.txdao_ack.append(int(a[10]))
            n.rxdao_ack.append(int(a[11]))
            n.txcoap.append(int(a[12]))
            n.rxcoap.append(int(a[13]))
            n.txtotal.append(int(a[14]))
            n.rxtotal.append(int(a[15]))
            n.total.append(int(a[16]))
    
    total_pred_node = get_total_nodes(nodes_pred)
    total_act_node = get_total_nodes(nodes_act)
    nodes_act.append(total_act_node)
    nodes_pred.append(total_pred_node)
    nodes_err.append(node(0))

    for n in nodes_err:
        p = search_node(nodes_pred,n.id)
        a = search_node(nodes_act,n.id)
        n.times = p.times
        for i in range(0,len(n.times)):
            n.txeb.append(calculate_error(a.txeb[i],p.txeb[i]))
            n.rxeb.append(calculate_error(a.rxeb[i],p.rxeb[i]))
            n.txeack.append(calculate_error(a.txeack[i],p.txeack[i]))
            n.rxeack.append(calculate_error(a.rxeack[i],p.rxeack[i]))
            n.txdio.append(calculate_error(a.txdio[i],p.txdio[i]))
            n.rxdio.append(calculate_error(a.rxdio[i],p.rxdio[i]))
            n.txdao.append(calculate_error(a.txdao[i],p.txdao[i]))
            n.rxdao.append(calculate_error(a.rxdao[i],p.rxdao[i]))
            n.txdao_ack.append(calculate_error(a.txdao_ack[i],p.txdao_ack[i]))
            n.rxdao_ack.append(calculate_error(a.rxdao_ack[i],p.rxdao_ack[i]))
            n.txcoap.append(calculate_error(a.txcoap[i],p.txcoap[i]))
            n.rxcoap.append(calculate_error(a.rxcoap[i],p.rxcoap[i]))
            n.txtotal.append(calculate_error(a.txtotal[i],p.txtotal[i]))
            n.rxtotal.append(calculate_error(a.rxtotal[i],p.rxtotal[i]))
            n.total.append(calculate_error(a.total[i],p.total[i]))

    begin = 4500
    end = 2500
    # begin = 6000    # topology tests
    # end = 1500      # topology tests

    for n in nodes_err:
        plot_node(nodes_err,n.id,m_type,begin,len(nodes_err[0].times)-end,destination + "/Figures/")
    # print(nodes_err[0].times[begin])
    # print(nodes_err[0].times[len(nodes_err[0].times)-end])
    print_analysis(nodes_err,m_type,begin,len(nodes_err[0].times)-end)
    # print_boxplot(nodes_err,m_type,begin,len(nodes_err[0].times)-end)