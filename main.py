#!/usr/bin/python

import sys
import getopt
import pandas as pd
import functions as f

argv = sys.argv[1:]
player = {
    "kobe": "Kobe Bryant",
    "jordan": "Michael Jordan",
    "lebron": "Lebron James"
}
try:
    opts, args = getopt.getopt(argv, 'n:paotr', ["name="])
except getopt.GetoptError:
    print("Fallo")
    sys.exit(2)
flags = [i[0] for i in opts]
if opts[0][0] == "-n":
    if "-p" in flags:
        points = f.points(player[opts[0][1]], f.dataFrame(), True if "-o" in flags else False, True if "-t" in flags else False)
        print(f"points: {round(points, 1)}")
    if "-a" in flags:
        assists = f.assists(player[opts[0][1]], f.dataFrame(), True if "-o" in flags else False, True if "-t" in flags else False)
        print(f"assists: {round(assists, 1)}")
    if "-r" in flags:
        rebounds = f.rebounds(player[opts[0][1]], f.dataFrame(), True if "-o" in flags else False,
                            True if "-t" in flags else False)
        print(f"rebounds: {round(rebounds, 1)}")


