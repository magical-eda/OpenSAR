import Magical
import json
import gdspy
from device_generation import basic, Pin, switch
from device_generation.glovar import tsmc40_glovar as glovar
import ConstGenPy 
import copy
import opensarroutePy

# Give 0.21 spacing (reduct 0.1 spacing)
PARA_SP = 210 
# comparator blockage magin 5um
COMP_SP = 5000
# shield distance with analog nets in um
SHIELD_DST = 3000
# light block distance 
LT_DST = 1000

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
        if self.name == "comp":
            magical.db.params.gnd = False # Do not connect guardring in comp cell
        else:
            magical.db.params.powerWireWidthTable[0][1] = 0.2
        magical.run()
        self.symAxis = magical.flow.pnrs[0].symAxis 
    def resize(self, w, gridStep=200):
        print("Resizing with width", w)
        assert self.imple, "Resize failed. Cell not implemented " + self.name
        area = (self.bound[1][0] - self.bound[0][0]) * (self.bound[1][1] - self.bound[0][1])
        w = int(w/gridStep) * gridStep
        h = (int(area/w/gridStep/2) + 1) * gridStep
        bound = [-w,-h,w,h]
        magical = Magical.Magical(self.json)
        magical.params.smallModuleArea = 100000 # large value waives powerstrip sizing
        if self.name == "comp":
            magical.db.params.gnd = False # Do not connect guardring in comp cell, this allows CLKS to route directly through comp cell
        else:
            magical.db.params.powerWireWidthTable[0][1] = 0.2
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
    def blockage(self, offset, margin=0):
        assert self.bound[1][0] - self.bound[0][0] > 2*margin, "Not enough margin to add blockage"
        return [self.bound[0][0]+margin+offset[0]*1000, self.bound[0][1]+offset[1]*1000, self.bound[1][0]-margin+offset[0]*1000, self.bound[1][1]+offset[1]*1000]

class SAR_ADC:
    def __init__(self, jsonFile):
        self.json = jsonFile
        self.setup = json.load(open(self.json))
        self.custom = {}
        self.cell = gdspy.Cell("SAR_ADC")
        self.gridStep = int((glovar.min_w['M1'] + glovar.min_w['SP'])*1000)
        self.debug = True
    def customCell(self, imple=True, resize=False):
        for cell in self.setup['custom_cells']:
            if resize and cell in self.setup['resize']:
                w_size = (self.switch['bound'][2] - self.switch['bound'][0]) * self.setup['resize'][cell]
                self.custom[cell].resize(w_size)
            else:
                self.custom[cell] = magicalCircuit(cell, self.setup[cell]['jsonFile'])
            if imple:
                self.custom[cell].implement()
            self.custom[cell].readInfo(self.setup[cell]['int_pins'])
    def sarLogic(self, imple=False):
        if imple:
            pass
        lib = gdspy.GdsLibrary()
        lib.read_gds(self.setup['sar_logic']['gds'])
        self.sar_logic = {}
        self.sar_logic['cell'] = lib.top_level()[0]
        self.sar_logic['cell'].flatten()
        dp = ConstGenPy.DefParse()
        dp.readDefFile(self.setup['sar_logic']['def'])
        self.sar_logic['pins'] = {}
        bbox = self.sar_logic['cell'].get_bounding_box()
        self.sar_logic['bound'] = basic.basic.BB_list([bbox[0][0]*1000,bbox[0][1]*1000,bbox[1][0]*1000,bbox[1][1]*1000])
        for i in range(dp.numPins()):
            pin = Pin.Pin(dp.pinName(i))
            pin.add_shape('M'+str(dp.pinLayer(i)), [[dp.pinXLo(i)/1000,dp.pinYLo(i)/1000], [dp.pinXHi(i)/1000,dp.pinYHi(i)/1000]])
            self.sar_logic['pins'][dp.pinName(i)] = pin   
    def capSwitch(self, pg_space=4.0):
        self.switch = {} 
        cs = switch.cap_switch("cap_switch")
        cas = self.setup['cap_switch']['cap']
        cs.cap_array(cas['w'], cas['sp'], cas['nf'], cas['l'], cas['m_bot'], cas['m_top'], route_width=0.2)
        cas = self.setup['cap_switch']
        cas['bit'] = self.setup['bit'] + self.setup['redundant_cycle'] - 2
        cas['ref'] = int(self.setup['redundant_cycle'] > 0)
        cas2 = json.load(open(cas['config'],'r'))
        cs.impleCap(cas['bit'],self.setup['column_bit'],cas['ref'],cas2['col_ary'],cas2['row_ary'],cas2['ref'])
        cas = self.setup['cap_switch']['switch']
        cs.switch(cas['w'], cas['l'], cas['nf'], attr=cas['attr'], pg_space=pg_space)
        cs.switch.array_w = cas['array_w']
        cas = json.load(open(cas['array_nf'],'r'))
        cs.switch.array_nf = cas['nf']
        cs.layout()
        self.numBit = cs.bit+cs.ref
        self.switch['cell'] = cs.cell
        bbox = cs.cell.get_bounding_box()
        self.switch['bound'] = basic.basic.BB_list([bbox[0][0]*1000,bbox[0][1]*1000,bbox[1][0]*1000,bbox[1][1]*1000])
        self.switch['block'] = cs.cap.block
        self.switch['light_block'] = cs.block
        self.switch['pins'] = {}
        self.switch['pins']['power'] = cs.switch.power
        self.switch['pins']['gnd'] = cs.switch.gnd
        self.switch['pins']['vcm'] = cs.switch.vcm
        self.switch['pins']['vrefp'] = cs.switch.vrefp
        self.switch['pins']['vrefn'] = cs.switch.vrefn
        self.switch['pins']['vin'] = cs.cap.vin
        self.switch['pins']['vctrl'] = cs.switch.vctrl # array of dict
        gdspy.write_gds(self.setup['resultDir']+"cap_switch.gds", [cs.cell], unit=1.0e-6, precision=1.0e-9)
    def place(self, x_dist=1, y_dist=1, n_fac=4):
        y = 0
        offset = [0.5*glovar.min_w['M1'], 0.5*glovar.min_w['M1']]
        # bootstrap right
        bound = self.custom['bootstrap'].bound
        self.bootstrap_r_o = [x_dist-bound[0][0]/1000.0, y]
        bootstrap_r = gdspy.CellReference(self.custom['bootstrap'].cell, origin=self.bootstrap_r_o)
        self.cell.add(bootstrap_r)
        # bootstrap left
        self.bootstrap_l_o = [-x_dist+bound[0][0]/1000.0, y]
        bootstrap_l = gdspy.CellReference(self.custom['bootstrap'].cell, origin=self.bootstrap_l_o, rotation=180, x_reflection=True)
        self.cell.add(bootstrap_l)
        # cap_switch right
        y = y + bound[1][1]/1000.0
        b = self.switch['bound']
        bound = [[-b[3],b[0]],[-b[1],b[2]]] # rotation 90
        tempy = y
        y = y - bound[0][1]/1000.0 + y_dist
        self.switch_r_o = [x_dist-bound[0][0]/1000.0+offset[1], y-offset[0]]
        switch_r = gdspy.CellReference(self.switch['cell'], origin=self.switch_r_o, rotation=90)
        self.cell.add(switch_r)
        # cap_switch left
        self.switch_l_o = [-x_dist+bound[0][0]/1000.0-offset[1], y-offset[0]]
        switch_l = gdspy.CellReference(self.switch['cell'], origin=self.switch_l_o, rotation=90, x_reflection=True)
        self.cell.add(switch_l)
        # center clks routing guidance
        ll = [-glovar.min_w['M1']*0.5, tempy]
        ur = [glovar.min_w['M1']*0.5,y+bound[1][1]/1000.0]
        clks_shape = gdspy.Rectangle(ll,ur,glovar.layer['M2'])
        self.cell.add(clks_shape)
        self.clks_guide = Pin.Pin("CLKS")
        self.clks_guide.add_shape('M2',clks_shape.get_bounding_box())
        # comp
        y = y + bound[1][1]/1000.0
        bound = self.custom['comp'].bound
        #x_center = (bound[1][0] - bound[0][0]) / 2000.0
        x_center = self.custom['comp'].symAxis / 1000.0
        y = y - bound[0][1]/1000.0 + y_dist #+ SHIELD_DST # No need...
        self.comp_o = [-x_center, y]
        comp_c = gdspy.CellReference(self.custom['comp'].cell, origin=self.comp_o)
        self.cell.add(comp_c)
        # logic
        y = y + bound[1][1]/1000.0 
        b = self.sar_logic['bound']
        bound = [[b[0], b[1]], [b[2], b[3]]]
        y = y - bound[0][1]/1000.0 + n_fac*y_dist # Additional y_dist for routing 4
        x_center = (-bound[1][0] + bound[0][0]) / 2000.0
        self.logic_o = [x_center-self.setup['sar_logic']['offset'][0], y-self.setup['sar_logic']['offset'][1]]
        #logic_c = gdspy.CellReference(self.sar_logic['cell'], origin=self.logic_o)
        # Do not physically add logic cell but only pins
        #self.cell.add(logic_c)
        self.adjust_pins()
        self.addLogicPin()
        self.cell.flatten()
        gdspy.write_gds(self.setup['resultDir']+"SAR_ADC.place.gds", [self], unit=1.0e-6, precision=1.0e-9)
    def wrapup(self):
        # Add back logic circuit
        lib = gdspy.GdsLibrary()
        lib.read_gds(self.setup['resultDir']+"SAR_ADC.route.gds")
        temp_cell = lib.top_level()[0]
        logic_c = gdspy.CellReference(self.sar_logic['cell'], origin=[self.logic_o[0],self.logic_o[1]+1.27])
        temp_cell.add(logic_c)
        temp_cell.flatten()
        gdspy.write_gds(self.setup['resultDir']+"SAR_ADC.output.gds", [temp_cell], unit=1.0e-6, precision=1.0e-9)
    def addLogicPin(self):
        for pinName in self.sar_logic['pins']:
            if pinName in self.setup['outports']:
                continue
            pin = self.sar_logic['pins'][pinName]
            shape = gdspy.Rectangle((pin.shape[0][1][0],pin.shape[0][1][1]),(pin.shape[0][2][0],pin.shape[0][2][1]+1.0),glovar.layer[pin.shape[0][0]])
            self.cell.add(shape)
    def adjust_pins(self):
        # bootstrap 
        self.pins_bootstrap_r = {}
        self.pins_bootstrap_l = {}
        for pinName in self.custom['bootstrap'].pins:
            self.pins_bootstrap_r[pinName] = copy.deepcopy(self.custom['bootstrap'].pins[pinName])
            self.pins_bootstrap_r[pinName].adjust([-self.bootstrap_r_o[0], -self.bootstrap_r_o[1]])
            self.pins_bootstrap_l[pinName] = copy.deepcopy(self.pins_bootstrap_r[pinName])
            self.pins_bootstrap_l[pinName].flip_vert(0)
        # cap switch
        self.pins_cap_r = {}
        self.pins_cap_l = {}
        block_r = self.switch['block']
        block_r.adjust([-self.switch_r_o[0],-self.switch_r_o[1]],True)
        block_l = copy.deepcopy(block_r)
        block_l.flip_vert(0)
        self.block = [block_r, block_l]
        block_r = self.switch['light_block']
        block_r.adjust([-self.switch_r_o[0],-self.switch_r_o[1]],True)
        block_l = copy.deepcopy(block_r)
        block_l.flip_vert(0)
        self.light_block = [block_r, block_l]
        for pinName in self.switch['pins']:
            if pinName == 'vctrl':
                self.pins_cap_r['vctrl'] = []
                self.pins_cap_l['vctrl'] = []
                for i in range(self.numBit):
                    pin_l = {}
                    pin_r = {}
                    for name in self.switch['pins']['vctrl'][i]:
                        pin_r[name] = self.switch['pins']['vctrl'][i][name]
                        pin_r[name].adjust([-self.switch_r_o[0],-self.switch_r_o[1]],True)
                        pin_l[name] = copy.deepcopy(pin_r[name])
                        pin_l[name].flip_vert(0)
                    self.pins_cap_r['vctrl'].append(pin_r)
                    self.pins_cap_l['vctrl'].append(pin_l)
                continue
            self.pins_cap_r[pinName] = self.switch['pins'][pinName]
            self.pins_cap_r[pinName].adjust([-self.switch_r_o[0],-self.switch_r_o[1]],True)
            self.pins_cap_l[pinName] = copy.deepcopy(self.pins_cap_r[pinName])
            self.pins_cap_l[pinName].flip_vert(0)
        # Add clks guide
        self.pins_cap_r['clks'] = self.clks_guide
        self.pins_cap_l['clks'] = self.clks_guide
        # Add connections for VCM, VREFP/N
        for pin in ['vcm','vrefp','vrefn']:
            ll = [self.pins_cap_l[pin].shape[-1][2][0], self.pins_cap_l[pin].shape[-1][1][1]]
            ur = [self.pins_cap_r[pin].shape[-1][1][0], self.pins_cap_l[pin].shape[-1][2][1]]
            lay = self.pins_cap_l[pin].shape[-1][0]
            rec_shape = gdspy.Rectangle(ll,ur,glovar.layer[lay])
            self.cell.add(rec_shape)
        # long M3 metal blockage
        self.long_block = []
        self.long_block.append(self.pins_cap_r['vcm'])
        self.long_block.append(self.pins_cap_r['vrefp'])
        self.long_block.append(self.pins_cap_r['vrefn'])
        self.long_block.append(self.pins_cap_l['vcm'])
        self.long_block.append(self.pins_cap_l['vrefp'])
        self.long_block.append(self.pins_cap_l['vrefn'])
        #for name in self.pins_cap_l['vctrl'][0]:
        #    print(self.pins_cap_l['vctrl'][-1][name])
        # comp
        for pinName in self.custom['comp'].pins:
            self.custom['comp'].pins[pinName].adjust([-self.comp_o[0],-self.comp_o[1]])
        # sar_logic
        for pinName in self.sar_logic['pins']:
            self.sar_logic['pins'][pinName].adjust([-self.logic_o[0],-self.logic_o[1]])
    def findOrigin(self):
        bound = self.cell.get_bounding_box()
        self.origin = basic.basic.legal_coord(bound[0], [0,0], 1)
        self.origin = [round(self.origin[0]*1000), round(self.origin[1]*1000)]
    def compPin(self, pin, i=0):
        layer = int(pin.shape[i][0][1]) - 1
        return layer, round(pin.shape[i][1][0]*1000), round(1000*pin.shape[i][1][1]), round(1000*pin.shape[i][2][0]), round(1000*pin.shape[i][2][1])
    def parsePin(self, router, sen):
        if self.debug:
            outFile = open(self.setup['resultDir']+'SAR_ADC.gr','w')
            outFile.write('gridStep %d\n' % self.gridStep)
            outFile.write('Offset %d %d\n' % (self.origin[0],self.origin[1]))
            outFile.write('symAxis 0\n')
        router.init()
        all_nets = json.load(open(self.setup['pinfile']))
        # Get nets according to sensitivity
        nets = {}
        for netName in all_nets:
            if sen:
                if netName in self.setup['sensitive_nets']:
                    nets[netName] = all_nets[netName]
            else:
                if netName not in self.setup['sensitive_nets']:
                    nets[netName] = all_nets[netName] 
        pinIdx = 0
        netPinDict = {}
        for netName in nets:
            if netName[:3] == "CTL":
                pins = nets[netName]
                for i in range(self.numBit):
                    netPinDict[netName+str(i)] = []
                    for dev, pinName in pins:
                        router.addPin(str(pinIdx), False, False)
                        netPinDict[netName+str(i)].append(pinIdx)
                        if dev == "sar_logic":
                            pinName = pinName + '[' + str(i) + ']'
                            lay,a,b,c,d = self.compPin(self.sar_logic['pins'][pinName])
                        elif dev == "cap_switch_r":
                            lay,a,b,c,d = self.compPin(self.pins_cap_r['vctrl'][i][pinName])
                        elif dev == "cap_switch_l":
                            lay,a,b,c,d = self.compPin(self.pins_cap_l['vctrl'][i][pinName])
                        else:
                            assert False, "Unsupported component: " + dev
                        router.addShape2Pin(pinIdx, lay, a*2, b*2, c*2, d*2)
                        print("Adding pin", pinIdx, lay+1,a,b,c,d)
                        if self.debug:
                            string = "%s %s %d %d %d %d %d %d %d\n" % (netName+str(i), str(pinIdx), lay+1, a, b, c, d, False, False)
                            outFile.write(string)
                        pinIdx = pinIdx + 1
            else:
                netPinDict[netName] = []
                pins = nets[netName]
                for dev, pinName in pins:
                    router.addPin(str(pinIdx), False, False)
                    netPinDict[netName].append(pinIdx)
                    if dev == "bootstrap_r":
                        lay,a,b,c,d = self.compPin(self.pins_bootstrap_r[pinName])
                    elif dev == "bootstrap_l":
                        lay,a,b,c,d = self.compPin(self.pins_bootstrap_l[pinName])
                    elif dev == "sar_logic":
                        lay,a,b,c,d = self.compPin(self.sar_logic['pins'][pinName])
                    elif dev == "comp":
                        lay,a,b,c,d = self.compPin(self.custom['comp'].pins[pinName])
                    elif dev == "cap_switch_r":
                        lay,a,b,c,d = self.compPin(self.pins_cap_r[pinName])
                    elif dev == "cap_switch_l":
                        lay,a,b,c,d = self.compPin(self.pins_cap_l[pinName])
                    else:
                        assert False, "Unsupported component: " + dev
                    router.addShape2Pin(pinIdx, lay, a*2, b*2, c*2, d*2)
                    print("Adding pin", pinIdx, lay+1,a,b,c,d)
                    if self.debug:
                        string = "%s %s %d %d %d %d %d %d %d\n" % (netName, str(pinIdx), lay+1, a, b, c, d, False, False)
                        outFile.write(string)
                    pinIdx = pinIdx + 1 
        for netName in nets:
            if netName[:3] == "CTL":
                for i in range(self.numBit):
                    routerNetIdx = router.addNet(netName+str(i), 200, 2, False, 2, 1)
                    print("Adding net", netName, 200, 2, False, 2, 1, routerNetIdx)
                    for pIdx in netPinDict[netName+str(i)]:
                        router.addPin2Net(pIdx, routerNetIdx)
            else:
                if netName in ['INN','INP']:
                    routerNetIdx = router.addNet(netName, 800, 2, False, 1, 2)
                    print("Adding net", netName, 800, 1, False, 1, 2, routerNetIdx)
                else:
                    routerNetIdx = router.addNet(netName, 200, 2, False, 1, 2)
                    print("Adding net", netName, 200, 2, False, 1, 2, routerNetIdx)
                for pIdx in netPinDict[netName]:
                    router.addPin2Net(pIdx, routerNetIdx)
                    print("Adding pin to net", pIdx, routerNetIdx)
    def aggresive_blk(self, router, blkNum, add_blk):
        # Block middle part of cap
        for l in range(6):
            router.addBlk(blkNum,l,add_blk[1][2]*2,add_blk[1][1]*2,add_blk[0][0]*2,add_blk[0][3]*2)
            blkNum = blkNum + 1
        # Block comp cells, probably bootstrap no need
        blk = self.custom['comp'].blockage(self.comp_o)
        # Extend to cap_array blockage
        if blk[1] > self.block[0].shape[0][2][1]*1000:
            blk[1] = self.block[0].shape[0][2][1]*1000
        for l in range(6):
            router.addBlk(blkNum,l,round(blk[0])*2-COMP_SP*2,round(blk[1])*2,round(blk[2])*2+COMP_SP*2,round(blk[3])*2)
            blkNum = blkNum + 1
        bb = self.cell.get_bounding_box()
        blk = [bb[0][0],bb[0][1],bb[1][0],self.block[0].shape[0][1][1]]
        for l in range(6):
            router.addBlk(blkNum,l,round(blk[0]*1000)*2,round(blk[1]*1000)*2,round(blk[2]*1000)*2,round(blk[3]*1000)*2)
            blkNum = blkNum + 1
        for light_block in self.light_block:
            for i in range(len(light_block.shape)):
                l,a,b,c,d = self.compPin(light_block,i)
                router.addBlk(blkNum,l,a*2,b*2-LT_DST*2,c*2,d*2+LT_DST*2)
                #router.addBlk(blkNum,l,a*2,b*2,c*2,d*2)
                blkNum = blkNum + 1
    def run_route(self, sen=True):
        if sen:
            placeFile = self.setup['resultDir']+"SAR_ADC.place.gds"
        else:
            placeFile = self.setup['resultDir']+"SAR_ADC.sens.gds"
        router = opensarroutePy.SarroutePy()
        router.setCircuitName("SAR_ADC")
        router.parseLef(self.setup['lef'])
        router.parseTechfile(self.setup['techfile'])
        router.parseGds(placeFile)
        self.findOrigin()
        # blockage
        blkNum = 0
        add_blk = []
        for blk in self.block:
            lay,a,b,c,d = self.compPin(blk)
            add_blk.append([a,b,c,d])
            for l in range(6):
                if sen:
                    router.addBlk(blkNum,l,a*2,b*2,c*2,d*2)
                else:
                    router.addBlk(blkNum,l,a*2,b*2-SHIELD_DST*2,c*2,d*2+SHIELD_DST*2)
                blkNum = blkNum + 1
        for blk in self.long_block:
            lay,a,b,c,d = self.compPin(blk)
            a = a - PARA_SP
            c = c + PARA_SP
            for l in range(6): # Block all
                router.addBlk(blkNum,l,a*2,b*2,c*2,d*2)
                blkNum = blkNum + 1
        for l in range(6):
            a,b,c,d = self.sar_logic['bound']
            a = a + round(self.logic_o[0]*1000)
            b = b + round(self.logic_o[1]*1000) + 1000
            c = c + round(self.logic_o[0]*1000)
            d = d + round(self.logic_o[1]*1000) + 1000
            router.addBlk(blkNum,l,a*2,b*2,c*2,d*2)
            blkNum = blkNum + 1
        if not sen:
            self.aggresive_blk(router, blkNum, add_blk)
        # Define pins
        self.parsePin(router, sen)
        # End of pins
        router.setGridStep(2*self.gridStep)
        router.setSymAxisX(0)
        router.setGridOffsetX(2*(self.origin[0] - self.gridStep * 10))
        router.setGridOffsetY(2*(self.origin[1] - self.gridStep * 10))
        routerPass = router.solve(False)
        router.evaluate()
        #if not routerPass:
        #    assert False, "Routing Failed"
        if sen:
            router.writeLayoutGds(placeFile, self.setup['resultDir']+"SAR_ADC.sens.gds", True)
        else:
            router.writeLayoutGds(placeFile, self.setup['resultDir']+"SAR_ADC.route.gds", True)
    def to_gds(self, *args):
        if len(args) == 1:
            return self.cell.to_gds(args[0])
        elif len(args) == 2:
            return self.cell.to_gds(args[0], args[1])
            
