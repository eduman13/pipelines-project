#!/usr/bin/python

import sys
import getopt as g
import pandas as pd
import functions as f

try:
    opts, args = g.getopt(sys.argv[1:], 'prmc', ["name=", "playoffs", "totals", "graph", "mailto"])
except getopt.GetoptError:
    print("Fallo")
    sys.exit(2)
flags = []
names = []
for i in opts:
    flags.append(i[0])
    names.append(i[1])
for i in args:
    if "-" in i or "--" in i:
        flags.append(i)
    else:
        names.append(i)
#print(f"opts: {names}")
#print(f"args: {flags}")
playoffs = True if "--playoffs" in flags else False
totals = True if "--totals" in flags else False
mvp = True if "-m" in flags else False
champion = True if "-c" in flags else False
graph = True if "--graph" in flags else False
email = True if "--mailto" in flags else False
allStats = f.dataFrame(names)
if graph:
    f.graphs(allStats, playoffs, email)
    sys.exit(0)
playerStats = f.simpleStats(allStats, names, playoffs, mvp, champion, totals)
print(f"points: {round(playerStats[0], 1)}\nassists: {round(playerStats[1], 1)}\nrebound: {round(playerStats[2], 1)}")
sys.exit(0)

