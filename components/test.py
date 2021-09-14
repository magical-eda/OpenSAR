import Magical
import json
import gdspy
from device_generation import basic, Pin, switch
from device_generation.glovar import tsmc40_glovar as glovar

class magicalCircuit:
    # pins: dict[pins]      cell:gdspy.Cell
    # bound: list[list]
    def __init__(self, cirName, jsonFile):
        self.name = cirName
        self.json = jsonFile
        self.pins = {}
        self.symAxis = None
        self.imple = False
    def implement(self):
        self.imple = True
        magical = Magical.Magical(self.json)
        #magical.params.smallModuleArea = 100000 # large value waives powerstrip sizing
        #if self.name == "comp":
        #    magical.db.params.gnd = False # Do not connect guardring in comp cell
        magical.run()
        self.symAxis = magical.flow.pnrs[0].symAxis 
    def resize(self, w, gridStep=200):
        w = w * 0.8
        assert self.imple, "Resize failed. Cell not implemented " + self.name
        area = (self.bound[1][0] - self.bound[0][0]) * (self.bound[1][1] - self.bound[0][1])
        w = int(w/gridStep) * gridStep
        h = (int(area/w/gridStep/2) + 1) * gridStep
        bound = [-w,-h,w,h]
        magical = Magical.Magical(self.json)
        magical.params.smallModuleArea = 100000 # large value waives powerstrip sizing
        if self.name == "comp":
            magical.db.params.gnd = False # Do not connect guardring in comp cell
        magical.run(bound)
        self.symAxis = magical.flow.pnrs[0].symAxis
    def readInfo(self, int_pins=[]):
        self.imple = True
        jfile = json.load(open(self.json))
        self.gds_file = jfile['resultDir'] + self.name + ".route.gds"
        self.ioPin_file = jfile['resultDir'] + self.name + '.ioPin'
        self.IOPin_file = jfile['resultDir'] + self.name + '.IO'
        self.gr_file = jfile['resultDir'] + self.name + ".gr"
        lib = gdspy.GdsLibrary()
        lib.read_gds(self.gds_file)
        self.cell = lib.top_level()[0]
        self.cell.flatten()
        with open(self.ioPin_file) as fin:
            lines = fin.readlines()
            bboxLine = lines[0].split()
            bboxLine = basic.basic.BB_list(bboxLine)
            self.bound = [[bboxLine[0],bboxLine[1]],[bboxLine[2],bboxLine[3]]]
            for lineIdx in range(1,len(lines)):
                line = lines[lineIdx].split()
                if line[0] in int_pins:
                    self.pins[line[0]] = Pin.Pin(line[0])
                    shape_list = []
                    for i in range(2,6):
                        shape_list.append(int(line[i])/1000.0)
                    self.pins[line[0]].add_shape('M'+line[1], [[shape_list[0], shape_list[1]], [shape_list[2], shape_list[3]]])
        with open(self.IOPin_file) as fin:
            lines = fin.readlines()
            for lineIdx in range(len(lines)):
                line = lines[lineIdx].split()
                self.pins[line[0]] = Pin.Pin(line[0])
                shape_list = []
                for i in range(2,6):
                    shape_list.append(int(line[i])/1000.0)
                self.pins[line[0]].add_shape('M'+line[1], [[shape_list[0], shape_list[1]], [shape_list[2], shape_list[3]]])
        with open(self.gr_file) as fin:
            lines = fin.readlines()
            words = lines[2].split()
            self.symAxis = int(words[1])

magical = magicalCircuit("comp", "components/comp_10_100.json")
magical.implement()
magical.readInfo()
#magical.resize(79600)
