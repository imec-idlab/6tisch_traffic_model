import csv
import numpy as np
import matplotlib.pyplot as plt

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

def get_predictions(preds):
    new = []
    temp = []
    for i in range(1,len(preds)):
        if(preds[i][1] == '0'):
            new.append(temp)
            temp = []
        else:
            temp.append(preds[i])
    return new

def get_actual(acts):
    new = []
    temp = []
    for i in range(1,len(acts)):
        if(acts[i][0] == '0'):
            new.append(temp)
            temp = []
        else:
            temp.append(acts[i])
    return new

def get_pred_total(preds):
    new = []
    for i in range(0,len(preds)):
        temp = []
        temp.append(int(preds[i][1]))
        predsum = 0
        for j in range(2,len(preds[i])):
            predsum += int(preds[i][j])
        temp.append(predsum)
        new.append(temp)
    return new

def get_act_total(acts):
    new = []
    for i in range(0,len(acts)):
        temp = []
        temp.append(int(acts[i][0]))
        actsum = 0
        for j in range(1,len(acts[i])):
            actsum += int(float(acts[i][j]))
        temp.append(actsum)
        new.append(temp)
    return new

def get_errors(acts, preds):
    errors = []
    for i in range(0, len(preds)):
        error = []
        error.append(preds[i][0])
        e = float(abs(preds[i][1] - acts[preds[i][0]-1][1]))/acts[preds[i][0]-1][1]
        error.append(e)
        errors.append(error)
    return errors

def print_errors(errors):
    for e in errors:
        print("Node:\t" + str(e[0]) + "\terror:\t" + str(e[1]))
    es = [row[1] for row in errors]
    print("------------------------------------------")
    print("\t\tmean:\t" + str(np.mean(es)))
    print("\t\tmax:\t" + str(np.max(es)))

# preds = get_pred_total(predictions)
# acts = get_act_total(actual)
# errors = get_errors(acts,preds)
# print_errors(errors)

preds = get_predictions(predictions)
acts = get_actual(actual)

errors = []
total_predictions = [[[],[]],[[],[]],[[],[]],[[],[]],[[],[]],[[],[]],[[],[]],[[],[]],[[],[]],[[],[]]]
for i in range(1,len(preds)):
    p = get_pred_total(preds[i])
    for pr in p:
        total_predictions[pr[0]-1][0].append(pr[1])
    a = get_act_total(acts[i])
    for ac in a:
        total_predictions[ac[0]-1][1].append(ac[1])
    e = get_errors(a,p)
    errors.append(e)

# node1 = []
# mean = []
# for i in range(0,len(errors)):
#     node1.append(errors[i][2][1])
#     temp = 0
#     for j in range(0,len(errors[i])):
#         temp += errors[i][j][1]
#     temp = temp/len(errors[i])
#     mean.append(temp)
plt.figure()
plt.plot(range(0,len(total_predictions[0][0])),total_predictions[9][0])
plt.plot(range(0,len(total_predictions[0][0])),total_predictions[9][1])
plt.show()