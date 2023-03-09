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

adapt = sum(read_boxfile('3min.log',1))/9
m15 = sum(read_boxfile('15min.log',1))/9
m30 = sum(read_boxfile('30min.log',1))/9
m60 = sum(read_boxfile('60min.log',1))/9

print([adapt,m15,m30,m60])
