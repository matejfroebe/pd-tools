#!/usr/bin/env python3

import argparse
import numpy as np

parser = argparse.ArgumentParser(description='Make pure data circular sequencer abstraction.')
parser.add_argument('filename', type=str, help='abstraction filename')
parser.add_argument('N', type=int, help='number of steps')
args = parser.parse_args()

class Abstraction:
    def __init__(self):
        self.nBox = 0
        self.objLines = []
        self.connectionLines = []

    def addBox(self, boxType, x, y, params):
        self.objLines.append("#X {0} {1} {2} {3};\n".format(boxType, x, y, ' '.join(str(p) for p in params)))
        self.nBox = self.nBox + 1
        return self.nBox - 1
        
    def addObject(self, x, y, name, params=[]):
        return self.addBox('obj', x, y, [name] + params)

    def addWirelessMessage(self, x, y, msgs=[]):
        "msgs: list of tuples (address, message)"
        def flatten(l):
            return [item for sublist in l for item in sublist]
        return self.addBox('msg', x, y, flatten([('\\;', m[0], m[1]) for m in msgs]))

    def addConnection(self, nBox1, nOut1, nBox2, nIn2):
        self.connectionLines.append("#X connect {0} {1} {2} {3};\n".format(nBox1, nOut1, nBox2, nIn2))


nSteps = args.N
tglSize = 30
bngSize = 15
x0 = 200
y0 = 200
rTgl = 170
rBng = 145

xLin = x0 * 2 + 20
yLin0 = 10
yLinStep = 60

abst = Abstraction()

# add "select" object
nSelect = abst.addObject(20, y0*2 + 100, 'select', list(range(nSteps)))

# add counter inlet
nInlet = abst.addObject(20, y0*2 + 50, 'inlet')
abst.addConnection(nInlet, 0, nSelect, 0)

# add inlet add message for setting the toggles
nSetInlet = abst.addObject(100, y0*2 + 50, 'inlet')
nMsg = abst.addWirelessMessage(100, y0*2 + 100,
                               [('rcv_tgl_{0}'.format(n), '\\${0}'.format(n+1))
                                for n in range(nSteps)])
abst.addConnection(nSetInlet, 0, nMsg, 0)

# add forward rotation with pack and split
nPack = abst.addObject(150, y0*2 + 50, 'pack', ['s'] + ['0']*nSteps)
nSplit = abst.addObject(150, y0*2 + 80, 'list split', ['1'])
abst.addConnection(nPack, 0, nSplit, 0)
abst.addConnection(nSplit, 1, nMsg, 0) # tail of the list
nFwdRotBng = abst.addObject(x0*2-15, 0, 'bng', [15, 250, 50, 0, 'empty', 'empty', 'empty', 17, 7, 0, 10, -262144, -1, -1])
abst.addConnection(nFwdRotBng, 0, nPack, 0)


# add outlet
nOutlet = abst.addObject(x0*4, y0*2 + 100, 'outlet')
for nStep, fi in zip(range(nSteps), np.linspace(0, 2*np.pi, nSteps, endpoint=False)):
    xTgl = x0 - tglSize/2 + np.sin(fi) * rTgl 
    yTgl = y0 - tglSize/2 - np.cos(fi) * rTgl 
    xBng = x0 - bngSize/2 + np.sin(fi) * rBng 
    yBng = y0 - bngSize/2 - np.cos(fi) * rBng 
    nTgl = abst.addObject(int(xTgl), int(yTgl), 'tgl',
                          [tglSize, 0, 'empty', 'rcv_tgl_'+str(nStep),
                           'empty', 17, 7, 0, 10, -4032, -1, -1, 1, 1])
    nBng = abst.addObject(int(xBng), int(yBng), 'bng', [bngSize, 250, 50, 0, 'empty', 'empty', 'empty', 17, 7, 0, 10, -262144, -1, -1])
    nSpigot = abst.addObject(xLin, yLin0 + yLinStep * nStep, 'spigot')
    # toggle->spigot
    abst.addConnection(nTgl, 0, nSpigot, 1)
    # toggle->forward rotation pack
    abst.addConnection(nTgl, 0, nPack, (nStep+1)%nSteps + 1) # first +1 is for rotation
    # select->bng
    abst.addConnection(nSelect, nStep, nBng, 0)
    # bng->spigot
    abst.addConnection(nBng, 0, nSpigot, 0)
    # spigot->outlet
    abst.addConnection(nSpigot, 0, nOutlet, 0)


with open(args.filename, 'w') as f:
    f.write("#N canvas 20 20 900 900 10;\n")
    f.writelines(abst.objLines)
    f.writelines(abst.connectionLines)
    f.writelines("#X coords 0 -1 1 1 400 400 1 0 0;")
