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

# Loss tests
s_loss_100_etx = read_boxfile('Boxplots/s_box_loss_100_etx.csv',2)
s_loss_75_etx = read_boxfile('Boxplots/s_box_loss_75_etx.csv',2)
s_loss_100 = read_boxfile('Boxplots/s_box_loss_100.csv',2)
s_loss_75 = read_boxfile('Boxplots/s_box_loss_75.csv',2)

ns_loss_100_etx = read_boxfile('Boxplots/ns_box_loss_100_etx.csv',2)
ns_loss_75_etx = read_boxfile('Boxplots/ns_box_loss_75_etx.csv',2)
ns_loss_100 = read_boxfile('Boxplots/ns_box_loss_100.csv',2)
ns_loss_75 = read_boxfile('Boxplots/ns_box_loss_75.csv',2)

# Topology change tests
s_dyn_adapt = read_boxfile('Boxplots/s_box_dynamic_adapt.csv',2)
s_dyn_15m = read_boxfile('Boxplots/s_box_dynamic_15min.csv',2)
s_dyn_30m = read_boxfile('Boxplots/s_box_dynamic_30min.csv',2)
s_dyn_45m = read_boxfile('Boxplots/s_box_dynamic_45min.csv',2)
s_dyn_60m = read_boxfile('Boxplots/s_box_dynamic_60min.csv',2)

ns_dyn_3m = read_boxfile('Boxplots/ns_box_dynamic_3min.csv',2)
ns_dyn_15m = read_boxfile('Boxplots/ns_box_dynamic_15min.csv',2)
ns_dyn_30m = read_boxfile('Boxplots/ns_box_dynamic_30min.csv',2)
ns_dyn_45m = read_boxfile('Boxplots/ns_box_dynamic_45min.csv',2)
ns_dyn_60m = read_boxfile('Boxplots/ns_box_dynamic_60min.csv',2)

ints = [47.6, 71.9, 165.3, 189.1]
ints_ns = [48.0, 92.9, 148.2, 489.9]
ints_h = [23.8,35.95,82.65,94.55]
ints_ns_h = [24,46.45,74.1,244.95]

# Stable tests
s_stab_1min_opt = read_boxfile('Boxplots/s_box_stable_pdr100_1min_opt.csv',2)
s_stab_1min_def = read_boxfile('Boxplots/s_box_stable_pdr100_1min_def.csv',2)
s_stab_15min_opt = read_boxfile('Boxplots/s_box_stable_pdr100_15min_opt.csv',2)
s_stab_15min_def = read_boxfile('Boxplots/s_box_stable_pdr100_15min_def.csv',2)
s_stab_1h_opt = read_boxfile('Boxplots/s_box_stable_pdr100_1h_opt.csv',2)
s_stab_1h_def = read_boxfile('Boxplots/s_box_stable_pdr100_1h_def.csv',2)

ns_stab_1min_opt = read_boxfile('Boxplots/ns_box_stable_pdr100_1min_opt.csv',2)
ns_stab_1min_def = read_boxfile('Boxplots/ns_box_stable_pdr100_1min_def.csv',2)
ns_stab_15min_opt = read_boxfile('Boxplots/ns_box_stable_pdr100_15min_opt.csv',2)
ns_stab_15min_def = read_boxfile('Boxplots/ns_box_stable_pdr100_15min_def.csv',2)
ns_stab_1h_opt = read_boxfile('Boxplots/ns_box_stable_pdr100_1h_opt.csv',2)
ns_stab_1h_def = read_boxfile('Boxplots/ns_box_stable_pdr100_1h_def.csv',2)

# Packet loss tests
s_100_def = read_boxfile('Boxplots/s_box_stable_pdr100_15min_opt.csv',2)
s_100_netx = read_boxfile('Boxplots/s_box_stable_pdr100_15min_netx.csv',2)
s_90_def = read_boxfile('Boxplots/s_box_stable_prr90_15min_opt.csv',2)
s_90_netx = read_boxfile('Boxplots/s_box_stable_prr90_15min_netx.csv',2)
s_80_def = read_boxfile('Boxplots/s_box_stable_prr80_15min_opt.csv',2)
s_80_netx = read_boxfile('Boxplots/s_box_stable_prr80_15min_netx.csv',2)

ns_100_def = read_boxfile('Boxplots/ns_box_stable_pdr100_15min_opt.csv',2)
ns_100_netx = read_boxfile('Boxplots/ns_box_stable_pdr100_15min_netx.csv',2)
ns_90_def = read_boxfile('Boxplots/ns_box_stable_prr90_15min_opt.csv',2)
ns_90_netx = read_boxfile('Boxplots/ns_box_stable_prr90_15min_netx.csv',2)
ns_80_def = read_boxfile('Boxplots/ns_box_stable_prr80_15min_opt.csv',2)
ns_80_netx = read_boxfile('Boxplots/ns_box_stable_prr80_15min_netx.csv',2)

# Storing dynamic boxplot
fig, ax1 = plt.subplots()
array = [s_dyn_60m, s_dyn_30m, s_dyn_15m, s_dyn_adapt]
labels = ["60 min", "30 min", "15 min", "Adapt"]
bplot = ax1.boxplot(array, labels=labels, patch_artist=True)
me1 = np.median(array, axis=1)
for i, line in enumerate(bplot['medians']):
    x, y = line.get_xydata()[1]
    text1 = 'η={:.2f} \n'.format(me1[i])
    ax1.annotate(text1, xy=(i+1, 100), ha='center', va='bottom')
colors = ['#4D9900', '#4D9900', '#4D9900', '#4D9900']
for patch, color in zip(bplot['boxes'], colors):
    patch.set_facecolor(color)
ax2 = ax1.twinx()
ax1.set_ylabel('Accuracy [%]')
ax2.set_ylabel('INT bytes / node / hour')
ax1.set_xlabel("INT update interval")
ticks = ax1.get_xticks()
ax2.set_yticks([24, 36, 83, 95])
ax2.plot(ticks, ints_h)
plt.show()

# Storing dynamic time
plt.plot(s_dyn_60m, label="60 min")
plt.plot(s_dyn_30m, label="30 min")
plt.plot(s_dyn_15m, label="15 min")
plt.plot(s_dyn_adapt, label="Adapt")
plt.xlabel("Time")
plt.ylabel("Accuracy [%]")
plt.xticks([0,900,1800,2700,3600,4500,5400,6200], labels=["0", "15m", "30m", "45m", "60m", "1h15m", "1h30m","1h45m"])
plt.legend()
plt.show()

# Non-storing dynamic boxplot
fig, ax1 = plt.subplots()
array = [ns_dyn_60m, ns_dyn_30m, ns_dyn_15m, ns_dyn_3m]
labels = ["60 min", "30 min", "15 min", "3 min"]
bplot = ax1.boxplot(array, labels=labels, patch_artist=True)
me1 = np.median(array, axis=1)
for i, line in enumerate(bplot['medians']):
    x, y = line.get_xydata()[1]
    text1 = 'η={:.2f} \n'.format(me1[i])
    ax1.annotate(text1, xy=(i+1, 100), ha='center', va='bottom')
colors = ['#990000', '#990000', '#990000', '#990000']
for patch, color in zip(bplot['boxes'], colors):
    patch.set_facecolor(color)
ax2 = ax1.twinx()
ax1.set_ylabel('Accuracy [%]')
ax2.set_ylabel('INT bytes / node / hour')
ax1.set_xlabel("INT update interval")
ticks = ax1.get_xticks()
ax2.set_yticks([24, 46, 74, 245])
ax2.plot(ticks, ints_ns_h)
plt.show()

# Non-storing dynamic time
plt.plot(ns_dyn_60m, label="60 min")
plt.plot(ns_dyn_30m, label="30 min")
plt.plot(ns_dyn_15m, label="15 min")
plt.plot(ns_dyn_3m, label="3 min")
plt.xlabel("Time")
plt.ylabel("Accuracy [%]")
plt.xticks([0,900,1800,2700,3600,4500,5400,6200], labels=["0", "15m", "30m", "45m", "60m", "1h15m", "1h30m","1h45m"])
plt.legend()
plt.show()

# Stable tests
fig, (ax1,ax2,ax3) = plt.subplots(ncols=3)
a1min = [s_stab_1min_def[2374:], s_stab_1min_opt[2374:], ns_stab_1min_def, ns_stab_1min_opt]
l1min = ["Default", "Opt. INT", "Default", "Opt. INT"]
a15min = [s_stab_15min_def[2374:], s_stab_15min_opt[2374:], ns_stab_15min_def, ns_stab_15min_opt]
l15min = ["Default", "Opt. INT", "Default", "Opt. INT"]
a1h = [s_stab_1h_def[3374:], s_stab_1h_opt[3374:], ns_stab_1h_def, ns_stab_1h_opt]
l1h = ["Default", "Opt. INT", "Default", "Opt. INT"]
bplot1 = ax1.boxplot(a1min, labels=l1min, patch_artist=True)
me1 = np.median(a1min, axis=1)
for i, line in enumerate(bplot1['medians']):
    x, y = line.get_xydata()[1]
    text1 = 'η={:.2f} \n'.format(me1[i])
    ax1.annotate(text1, xy=(i+1, 100), ha='center', va='bottom')
ax1.set_ylabel("Accuracy [%]")
bplot2 = ax2.boxplot(a15min, labels=l15min, patch_artist=True)
me2 = np.median(a15min, axis=1)
for i, line in enumerate(bplot2['medians']):
    x, y = line.get_xydata()[1]
    text2 = 'η={:.2f} \n'.format(me2[i])
    ax2.annotate(text2, xy=(i+1, 100), ha='center', va='bottom')
bplot3 = ax3.boxplot(a1h, labels=l1h, patch_artist=True)
me3 = np.median(a1h, axis=1)
for i, line in enumerate(bplot3['medians']):
    x, y = line.get_xydata()[1]
    text3 = 'η={:.2f} \n'.format(me3[i])
    ax3.annotate(text3, xy=(i+1, 100), ha='center', va='bottom')
ax1.set_title("1 min\n")
ax2.set_title("15 min\n")
ax3.set_title("1 h\n")
ax3.plot([],label="Storing mode", color="#4D9900", marker="s", linewidth=0)
ax3.plot([],label="Non-storing mode", color="#990000", marker="s", linewidth=0)
ax3.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
colors = ['#4D9900', '#4D9900', '#990000', '#990000']
for bplot in (bplot1, bplot2, bplot3):
    for patch, color in zip(bplot['boxes'], colors):
        patch.set_facecolor(color)
plt.show()

# Path loss tests
fig, (ax1,ax2,ax3) = plt.subplots(ncols=3)
a1min = [s_100_netx[2374:], s_100_def[2374:], ns_100_netx, ns_100_def]
l1min = ["No ETX", "ETX", "No ETX", "ETX"]
a15min = [s_90_netx[231:], s_90_def[231:], ns_90_netx, ns_90_def]
l15min = ["No ETX", "ETX", "No ETX", "ETX"]
a1h = [s_80_netx, s_80_def, ns_80_netx[0:len(ns_80_netx)-11002], ns_80_def[0:len(ns_80_netx)-11002]]
l1h = ["No ETX", "ETX", "No ETX", "ETX"]
bplot1 = ax1.boxplot(a1min, labels=l1min, patch_artist=True)
me1 = np.median(a1min, axis=1)
for i, line in enumerate(bplot1['medians']):
    x, y = line.get_xydata()[1]
    text1 = 'η={:.2f} \n'.format(me1[i])
    ax1.annotate(text1, xy=(i+1, 100), ha='center', va='bottom')
ax1.set_ylabel("Accuracy [%]")
bplot2 = ax2.boxplot(a15min, labels=l15min, patch_artist=True)
me2 = np.median(a15min, axis=1)
for i, line in enumerate(bplot2['medians']):
    x, y = line.get_xydata()[1]
    text2 = 'η={:.2f} \n'.format(me2[i])
    ax2.annotate(text2, xy=(i+1, 100), ha='center', va='bottom')
bplot3 = ax3.boxplot(a1h, labels=l1h, patch_artist=True)
me3 = np.median(a1h, axis=1)
for i, line in enumerate(bplot3['medians']):
    x, y = line.get_xydata()[1]
    text3 = 'η={:.2f} \n'.format(me3[i])
    ax3.annotate(text3, xy=(i+1, 100), ha='center', va='bottom')
ax1.set_title("PRR 100%\n")
ax2.set_title("PRR 90%\n")
ax3.set_title("PRR 80%\n")
ax3.plot([],label="Storing mode", color="#4D9900", marker="s", linewidth=0)
ax3.plot([],label="Non-storing mode", color="#990000", marker="s", linewidth=0)
ax3.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
colors = ['#4D9900', '#4D9900', '#990000', '#990000']
for bplot in (bplot1, bplot2, bplot3):
    for patch, color in zip(bplot['boxes'], colors):
        patch.set_facecolor(color)
plt.show()