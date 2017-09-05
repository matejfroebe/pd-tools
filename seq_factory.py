#!/usr/bin/env python3

import argparse
import numpy as np

parser = argparse.ArgumentParser(description='Make pure data circular sequencer abstraction.')
parser.add_argument('filename', type=str, help='abstraction filename')
parser.add_argument('N', type=int, help='number of steps')
parser.add_argument('nStates', type=int, help='number of states for each step')
parser.add_argument('--conga', '-c', action='store_true', help='use conga buttons')
parser.add_argument('--bell', '-b', action='store_true', help='use cowbell buttons')
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

    def addFloatAtom(self, x, y, width, rcvSym):
        return self.addBox('floatatom', x, y, [width, 0, 0, 0, '-', rcvSym, '-', 'f', 10])
    
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
xLinStep = 60
yLin0 = 10
yLinStep = 60

abst = Abstraction()

# add "select" object
nSelect = abst.addObject(20, y0*2 + 100, 'select', list(range(nSteps)))

# add counter inlet
nInlet = abst.addObject(20, y0*2 + 50, 'inlet')
abst.addConnection(nInlet, 0, nSelect, 0)

# add inlet for setting the toggles
nSetInlet = abst.addObject(100, y0*2 + 50, 'inlet')
nListPrepend = abst.addObject(100, y0*2 + 70, 'list', ['prepend'])
nUnpack = abst.addObject(150, y0*2 + 150, 'unpack', ['s'] + ['0']*nSteps)
abst.addConnection(nListPrepend, 0, nUnpack, 0)
# prepend a dummy element to the list
nLoadBang = abst.addObject(150, y0*2 + 30, 'loadbang')
nDummyList = abst.addBox('msg', 150, y0*2+50, ['dummy'])
abst.addConnection(nSetInlet, 0, nListPrepend, 0)
abst.addConnection(nLoadBang, 0, nDummyList, 0)
abst.addConnection(nDummyList, 0, nListPrepend, 1)

# add forward rotation with pack and split
nPackFwd = abst.addObject(150, y0*2 + 50, 'pack', ['s'] + ['0']*nSteps)
abst.addConnection(nPackFwd, 0, nUnpack, 0)
nFwdRotBng = abst.addObject(x0*2-15, 0, 'bng', [15, 250, 50, 0, 'empty', 'empty', 'empty', 17, 7, 0, 10, -262144, -1, -1])
abst.addConnection(nFwdRotBng, 0, nPackFwd, 0)

# backward rotation
nPackBck = abst.addObject(400, y0*2 + 50, 'pack', ['s'] + ['0']*nSteps)
abst.addConnection(nPackBck, 0, nUnpack, 0)
nBckRotBng = abst.addObject(x0*2-15-15, 0, 'bng', [15, 250, 50, 0, 'empty', 'empty', 'empty', 17, 7, 0, 10, -262144, -1, -1])
abst.addConnection(nBckRotBng, 0, nPackBck, 0)


# add outlet
nOutlet = abst.addObject(x0*4, y0*2 + 100, 'outlet')
for nStep, fi in zip(range(nSteps), np.linspace(0, 2*np.pi, nSteps, endpoint=False)):
    xTgl = x0 - tglSize/2 + np.sin(fi) * rTgl 
    yTgl = y0 - tglSize/2 - np.cos(fi) * rTgl 
    xBng = x0 - bngSize/2 + np.sin(fi) * rBng 
    yBng = y0 - bngSize/2 - np.cos(fi) * rBng
    if args.conga:
        nTgl = abst.addObject(int(xTgl), int(yTgl), 'conga-button',
                              [args.nStates,
                               'rcv_tgl_'+str(nStep)+'_$0'])
    elif args.bell:
        nTgl = abst.addObject(int(xTgl), int(yTgl), 'cowbell-button',
                              ['rcv_tgl_'+str(nStep)+'_$0'])
    else:
        nTgl = abst.addObject(int(xTgl), int(yTgl), 'tgl',
                              [tglSize, 0, 'empty', 'rcv_tgl_'+str(nStep)+'_$0',
                               'empty', 17, 7, 0, 10, -4032, -1, -1, 1, 1])

    nBng = abst.addObject(int(xBng), int(yBng), 'bng', [bngSize, 250, 50, 0, 'empty', 'empty', 'empty', 17, 7, 0, 10, -262144, -1, -1])
    nSpigot = abst.addObject(xLin, yLin0 + yLinStep * nStep, 'spigot')
    nFloat = abst.addObject(xLin + 100, yLin0 + yLinStep * nStep, 'float')
    nSend = abst.addObject(xLin + xLinStep*nStep, 2*y0 + 200, 'send', ['rcv_tgl_'+str(nStep)+'_$0'])
    # toggle->spigot
    abst.addConnection(nTgl, 0, nSpigot, 1)
    # toggle->float object
    abst.addConnection(nTgl, 0, nFloat, 1)
    # spigot->float object
    abst.addConnection(nSpigot, 0, nFloat, 0)
    # toggle->forward rotation pack
    abst.addConnection(nTgl, 0, nPackFwd, (nStep+1)%nSteps + 1) # first +1 is for rotation
    # toggle->backward rotation pack
    abst.addConnection(nTgl, 0, nPackBck, (nStep-1)%nSteps + 1)
    # unpack->send
    abst.addConnection(nUnpack, nStep+1, nSend, 0)
    # select->bng
    abst.addConnection(nSelect, nStep, nBng, 0)
    # bng->spigot
    abst.addConnection(nBng, 0, nSpigot, 0)
    # float->outlet
    abst.addConnection(nFloat, 0, nOutlet, 0)


with open(args.filename, 'w') as f:
    f.write("#N canvas 20 20 900 900 10;\n")
    f.writelines(abst.objLines)
    f.writelines(abst.connectionLines)
    f.writelines("#X coords 0 -1 1 1 400 400 1 0 0;")
