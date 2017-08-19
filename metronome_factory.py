#!/usr/bin/env python3

import argparse
import numpy as np

parser = argparse.ArgumentParser(description='Make pure data circular sequencer abstraction.')
parser.add_argument('filename', type=str, help='abstraction filename')
parser.add_argument('N', type=int, help='number of steps')
args = parser.parse_args()

class Abstraction:
    def __init__(self):
        self.nObj = 0
        self.objLines = []
        self.connectionLines = []
    
    def addObject(self, x, y, name, params=[]):
        self.objLines.append("#X obj {0} {1} {2} {3};\n".format(x, y, name, ' '.join(str(p) for p in params)))
        self.nObj = self.nObj + 1
        return self.nObj - 1

    def addConnection(self, nObj1, nOut1, nObj2, nIn2):
        self.connectionLines.append("#X connect {0} {1} {2} {3};\n".format(nObj1, nOut1, nObj2, nIn2))


nSteps = args.N
tglSize = 15
x0 = 200
y0 = 200
r = 155

xLin = x0 * 2 + 20
yLin0 = 10
yLinStep = 60

abst = Abstraction()

# add "select" object
nSelect = abst.addObject(20, y0*2+ 50, 'select', range(nSteps))

# add inlet
nInlet = abst.addObject(20, y0*2+ 50, 'inlet')
abst.addConnection(nInlet, 0, nSelect, 0)

# add outlet
nOutlet = abst.addObject(x0*4, y0*2 + 100, 'outlet')
for nPoint, fi in zip(range(nSteps), np.linspace(0, 2*np.pi, nSteps, endpoint=False)):
    x = x0 - tglSize/2 + np.sin(fi) * r
    y = y0 - tglSize/2 - np.cos(fi) * r
    nTgl = abst.addObject(int(x), int(y), 'tgl', [tglSize, 0, 'empty', 'empty', 'empty', 17, 7, 0, 10, -4032, -1, -1, 1, 1])
    nSpigot = abst.addObject(xLin, yLin0 + yLinStep * nPoint, 'spigot')
    # toggle->spigot
    abst.addConnection(nTgl, 0, nSpigot, 1)
    # select->spigot
    abst.addConnection(nSelect, nPoint, nSpigot, 0)
    # spigot->outlet
    abst.addConnection(nSpigot, 0, nOutlet, 0)


with open(args.filename, 'w') as f:
    f.write("#N canvas 20 20 900 900 10;\n")
    f.writelines(abst.objLines)
    f.writelines(abst.connectionLines)
    f.writelines("#X coords 0 -1 1 1 400 400 1 0 0;")
