import matplotlib.pyplot as plt
import csv
import numpy as np

def read_boxfile(file, column):
    array = []
    with open(file, newline='') as csvfile:
        boxreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for box in boxreader:
            array.append(float(box[column]))
    return array

adapt = sum(read_boxfile('adapt_ints.log',1))/9
m15 = sum(read_boxfile('15min_ints.log',1))/9
m30 = sum(read_boxfile('30min_ints.log',1))/9
m45 = sum(read_boxfile('45min_ints.log',1))/9
m60 = sum(read_boxfile('60min_ints.log',1))/9

print([adapt,m15,m30,m45,m60])