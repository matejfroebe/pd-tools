#!/usr/bin/env python3

import argparse
import numpy as np

parser = argparse.ArgumentParser(description='Make pure data circular sequencer abstraction.')
parser.add_argument('filename', type=str, help='abstraction filename')
parser.add_argument('N', type=int, help='number of steps')
args = parser.parse_args()

nSteps = args.N
tglSize = 15
x0 = 200
y0 = 200
r = 155

xLin = x0 * 2 + 20
yLin0 = 10
yLinStep = 30

objLines = []
connectionLines = []
nObj = 0

# add "select" object
objLines.append("#X obj {0} {1} select {2};\n".format(20, y0*2+ 50, ' '.join(str(i) for i in range(nSteps))))
nSelect = nObj; nObj += 1;

# add inlet
objLines.append("#X obj {0} {1} inlet;\n".format(20, y0*2+ 50))
nInlet = nObj; nObj += 1;
connectionLines.append("#X connect {0} 0 {1} 0;\n".format(nInlet, nSelect))

# add outlet
objLines.append("#X obj {0} {1} outlet;\n".format(x0*4, y0*2 + 100))
nOutlet = nObj; nObj += 1;
for nPoint, fi in zip(range(nSteps), np.linspace(0, 2*np.pi, nSteps, endpoint=False)):
    x = x0 - tglSize/2 + np.sin(fi) * r
    y = y0 - tglSize/2 - np.cos(fi) * r
    objLines.append("#X obj {0} {1} tgl {2} 0 empty empty empty 17 7 0 10 -4032 -1 -1 1 1;\n".format(int(x), int(y), tglSize))
    objLines.append("#X obj {0} {1} spigot;\n".format(xLin, yLin0 + yLinStep * nObj))
    # toggle->spigot
    connectionLines.append("#X connect {0} 0 {1} 1;\n".format(nObj, nObj+1))
    # select->spigot
    connectionLines.append("#X connect {0} {1} {2} 0;\n".format(nSelect, nPoint, nObj+1))
    # spigot->outlet
    connectionLines.append("#X connect {0} 0 {1} 0;\n".format(nObj+1, nOutlet))
    nObj = nObj+2


with open(args.filename, 'w') as f:
    f.write("#N canvas 20 20 900 900 10;\n")
    f.writelines(objLines)
    f.writelines(connectionLines)
    f.writelines("#X coords 0 -1 1 1 400 400 1 0 0;")
