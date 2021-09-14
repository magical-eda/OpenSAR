import pyverilog.vparser.ast as vast
import pyverilog.ast_code_generator.codegen as pycodegen
import json, sys
import argparse
import math

# Change to my template
pycodegen.DEFAULT_TEMPLATE_DIR = './template/'

name_dict = json.load(open('./input/name_dict.json'))

class instance:
    def __init__(self, idx=0, strength=0, inst_type='', portdict={}):
        self.portdict = portdict
        if strength >= 0:
            self.name = name_dict[inst_type] + str(strength) + 'BWP ' + 'I' + str(idx)
        else:
            self.name = name_dict[inst_type] + 'BWP I' + str(idx)
        self.portlist()
    def portlist(self):
        self.ports = []
        for name in self.portdict:
            tempName = '.' + name + ' (' + self.portdict[name] + ')'
            self.ports.append(vast.Identifier(tempName))
        self.inst = vast.Instance(None,self.name, self.ports, None)

class sar_logic:
    def __init__(self, jsonFile='./input/10bit.json'):
        self.setup = json.load(open(jsonFile))
        self.sys = json.load(open(self.setup['sys'],'r'))
        self.bit = self.sys['bit'] + self.sys['redundant_cycle'] - 1
        portlist = []
        self.items = []
        for name in self.setup['all_ports']:
            portlist.append(vast.Identifier(name))
            if name in self.setup['in_ports']:
                self.items.append(vast.Ioport(vast.Input(name)))
            elif name in self.setup['clk_ports']:
                self.items.append(vast.Ioport(vast.Output(name)))
            elif name == self.setup['result_port']:
                self.items.append(vast.Ioport(vast.Output(name, vast.Width(vast.IntConst(self.bit),vast.IntConst(0)))))
            else:
                self.items.append(vast.Ioport(vast.Output(name, vast.Width(vast.IntConst(self.bit-1),vast.IntConst(0)))))
        self.ports = vast.Portlist(portlist)
        self.add_wire()
        self.add_fixed_inst()
        self.add_sized_inst()
    def add_wire(self):
        self.items.append(vast.Ioport(vast.Wire('QB')))
        self.items.append(vast.Ioport(vast.Wire('Q', vast.Width(vast.IntConst(self.bit+2), vast.IntConst(1)))))
        for name in ['refp','refn']:
            self.items.append(vast.Ioport(vast.Wire(name, vast.Width(vast.IntConst(self.bit-1), vast.IntConst(0)))))
        for name in ['N','P']:
            self.items.append(vast.Ioport(vast.Wire(name, vast.Width(vast.IntConst(self.bit), vast.IntConst(0)))))
        for name in ['N_B','P_B','N_Q','N_QB','P_Q','P_QB']:
            self.items.append(vast.Ioport(vast.Wire(name, vast.Width(vast.IntConst(self.bit), vast.IntConst(1)))))
    def add_fixed_inst(self):
        self.cnt = 0
        self.items.append( instance(self.cnt, 1 , "dff", {"Q":"Q[1]", "QN":"QB", "CDN":"INT_RST", "CP":"RDY", "D":"Q[2]"}).inst )
        self.items.append( instance(self.cnt+1, 1 , "dffq", {"Q":"N[0]", "CDN":"INT_RST", "CP":"Q[1]", "D":"OUTM"}).inst )
        self.items.append( instance(self.cnt+2, 1 , "dffq", {"Q":"P[0]", "CDN":"INT_RST", "CP":"Q[1]", "D":"OUTP"}).inst )
        self.items.append( instance(self.cnt+3, 2 , "inv", {"ZN":"clock_output", "I":"net039"}).inst )
        #self.items.append( instance(self.cnt, 1 , "delay", {"Z":"net07", "I":"net039"}).inst )
        self.items.append( instance(self.cnt+4, 1 , "dffq", {"Q":"INT_RST", "CDN":"reset_n", "CP":"SYS_CLKB", "D":"QB"}).inst )
        self.items.append( instance(self.cnt+5, 1 , "dff", {"Q":"Q["+str(self.bit+2)+"]", "QN": "QB_"+str(self.bit+2),"CDN":"INT_RST", "CP":"clock", "D":"high_net"}).inst )
        self.items.append( instance(self.cnt+6, 2 , "inv", {"ZN":"clk_sample_b", "I":"QB_"+str(self.bit+2)}).inst )
        self.items.append( instance(self.cnt+7, -1 , "tieh", {"Z":"high_net"}).inst )
        self.items.append( instance(self.cnt+8, 0 , "inv", {"ZN":"SYS_CLKB", "I":"clock"}).inst )
        self.items.append( instance(self.cnt+9, 0 , "nand2", {"ZN":"OUTP_I", "A1":"cmp_p", "A2":"OUTM_I"}).inst )
        self.items.append( instance(self.cnt+10, 0 , "nand2", {"ZN":"OUTM_I", "A1":"OUTP_I", "A2":"cmp_n"}).inst )
        self.items.append( instance(self.cnt+11, 2 , "buff", {"Z":"OUTP", "I":"OUTP_I"}).inst )
        self.items.append( instance(self.cnt+12, 2 , "buff", {"Z":"OUTM", "I":"OUTM_I"}).inst )
        self.items.append( instance(self.cnt+13, 0 , "nor2", {"ZN":"net039", "A1":"P[0]", "A2":"N[0]"}).inst )
        self.items.append( instance(self.cnt+14, 4 , "inv", {"ZN":"RDY", "I":"net08"}).inst )
        self.items.append( instance(self.cnt+15, 4 , "nor2", {"ZN":"net010", "A1":"cmp_p", "A2":"cmp_n"}).inst )
        self.items.append( instance(self.cnt+16, 1 , "delay2", {"Z":"net08", "I":"net010"}).inst )
        self.cnt += 17
        for i in range(self.bit):
            #self.items.append( instance(self.cnt, 1 , "nand2", {"ZN":"refn_b["+str(i)+"]", "A1":"P_QB["+str(i+1)+"]", "A2":"N_QB["+str(i+1)+"]"}).inst )
            #self.items.append( instance(self.cnt+1, 4 , "inv", {"ZN":"refn["+str(i)+"]", "I":"refn_b["+str(i)+"]"}).inst )
            #self.items.append( instance(self.cnt+2, 1 , "nor2", {"ZN":"refp_b["+str(i)+"]", "A1":"P_Q["+str(i+1)+"]", "A2":"N_Q["+str(i+1)+"]"}).inst )
            #self.items.append( instance(self.cnt+3, 4 , "inv", {"ZN":"refp["+str(i)+"]", "I":"refp_b["+str(i)+"]"}).inst )
            self.items.append( instance(self.cnt, 1 , "dffq", {"Q":"Q["+str(i+2)+"]", "CDN":"INT_RST", "CP":"RDY", "D":"Q["+str(i+3)+"]"}).inst )
            self.items.append( instance(self.cnt+1, 1 , "dff", {"Q":"N_Q["+str(i+1)+"]", "QN":"N_QB["+str(i+1)+"]", "CDN":"INT_RST", "CP":"Q["+str(i+2)+"]", "D":"OUTM"}).inst )
            #self.items.append( instance(self.cnt+6, 2 , "inv", {"ZN":"N_B["+str(i+1)+"]", "I":"N_Q["+str(i+1)+"]"}).inst )
            #self.items.append( instance(self.cnt+7, 2 , "inv", {"ZN":"N["+str(i+1)+"]", "I":"N_QB["+str(i+1)+"]"}).inst )
            self.items.append( instance(self.cnt+2, 1 , "dff", {"Q":"P_Q["+str(i+1)+"]", "QN":"P_QB["+str(i+1)+"]", "CDN":"INT_RST", "CP":"Q["+str(i+2)+"]", "D":"OUTP"}).inst )
            #self.items.append( instance(self.cnt+9, 2 , "inv", {"ZN":"P_B["+str(i+1)+"]", "I":"P_Q["+str(i+1)+"]"}).inst )
            #self.items.append( instance(self.cnt+10, 2 , "inv", {"ZN":"P["+str(i+1)+"]", "I":"P_QB["+str(i+1)+"]"}).inst )
            self.cnt += 3

        self.items.append( instance(self.cnt, 1 , "inv", {"I":"N[0]", "ZN":"result[0]"}).inst )
        self.cnt += 1
        for i in range(1, self.bit+1):
            self.items.append( instance(self.cnt, 1 , "inv", {"I":"N_Q["+str(i)+"]", "ZN":"result["+str(i)+"]"}).inst )
            self.cnt += 1
    def add_sized_inst(self):
        buffer_size = self.setup['buffer_size']
        self.items.append( instance(self.cnt, 1 , "dffs", {"Q":"QB_clk", "SDN":"reset_n", "CP":"clock_d", "D":"QB"}).inst )
        self.items.append( instance(self.cnt+1, 1 , "nand2", {"ZN":"clkc_en", "A1":"clk_sample_b", "A2":"QB_clk"}).inst )
        self.items.append( instance(self.cnt+2, math.ceil(buffer_size['clkc']/4), "or2", {"Z":"clkc_b", "A1":"clock", "A2": "clkc_en"}).inst )
        self.items.append( instance(self.cnt+3, buffer_size['clkc'] , "inv", {"ZN":"clkc", "I":"clkc_b"}).inst )
        self.items.append( instance(self.cnt+4, buffer_size['clk_sample'] , "inv", {"ZN":"clk_sample", "I":"clk_sample_b"}).inst )
        self.items.append( instance(self.cnt+5, 1 , "delay_large", {"Z":"clock_1", "I":"clock"}).inst )
        self.items.append( instance(self.cnt+6, 1 , "delay_large", {"Z":"clock_2", "I":"clock_1"}).inst )
        self.items.append( instance(self.cnt+7, 1 , "delay_large", {"Z":"clock_d", "I":"clock_2"}).inst )
        self.cnt += 8
        switch_size = json.load(open(buffer_size['switch']))
        for i in range(self.bit):
            self.items.append( instance(self.cnt, switch_size[i] , "inv", {"ZN":"switch_refn_l["+str(i)+"]", "I":"refn["+str(i)+"]"}).inst )
            self.items.append( instance(self.cnt+1, switch_size[i] , "inv", {"ZN":"switch_refn_r["+str(i)+"]", "I":"refn["+str(i)+"]"}).inst )
            self.items.append( instance(self.cnt+2, switch_size[i] , "inv", {"ZN":"switch_refp_l["+str(i)+"]", "I":"refp["+str(i)+"]"}).inst )
            self.items.append( instance(self.cnt+3, switch_size[i] , "inv", {"ZN":"switch_refp_r["+str(i)+"]", "I":"refp["+str(i)+"]"}).inst )
            if switch_size[i] <= 2:
                self.items.append( instance(self.cnt+4, switch_size[i] , "inv", {"ZN":"switch_p["+str(i)+"]", "I":"N_QB["+str(i+1)+"]"}).inst )
                self.items.append( instance(self.cnt+5, switch_size[i] , "inv", {"ZN":"switch_n["+str(i)+"]", "I":"P_QB["+str(i+1)+"]"}).inst )
                self.items.append( instance(self.cnt+6, switch_size[i] , "inv", {"ZN":"switch_bp["+str(i)+"]", "I":"N_Q["+str(i+1)+"]"}).inst )
                self.items.append( instance(self.cnt+7, switch_size[i] , "inv", {"ZN":"switch_bn["+str(i)+"]", "I":"P_Q["+str(i+1)+"]"}).inst )
                self.items.append( instance(self.cnt+8, 1 , "nand2", {"ZN":"refn_b["+str(i)+"]", "A1":"P_QB["+str(i+1)+"]", "A2":"N_QB["+str(i+1)+"]"}).inst )
                self.items.append( instance(self.cnt+9, 1 , "nor2", {"ZN":"refp_b["+str(i)+"]", "A1":"P_Q["+str(i+1)+"]", "A2":"N_Q["+str(i+1)+"]"}).inst )
            else:
                self.items.append( instance(self.cnt+4, switch_size[i] , "inv", {"ZN":"switch_p["+str(i)+"]", "I":"N_B["+str(i+1)+"]"}).inst )
                self.items.append( instance(self.cnt+5, switch_size[i] , "inv", {"ZN":"switch_n["+str(i)+"]", "I":"P_B["+str(i+1)+"]"}).inst )
                self.items.append( instance(self.cnt+6, switch_size[i] , "inv", {"ZN":"switch_bp["+str(i)+"]", "I":"N["+str(i+1)+"]"}).inst )
                self.items.append( instance(self.cnt+7, switch_size[i] , "inv", {"ZN":"switch_bn["+str(i)+"]", "I":"P["+str(i+1)+"]"}).inst )
                self.items.append( instance(self.cnt+8, 1 , "nand2", {"ZN":"refn_b["+str(i)+"]", "A1":"P_B["+str(i+1)+"]", "A2":"N_B["+str(i+1)+"]"}).inst )
                self.items.append( instance(self.cnt+9, 1 , "nor2", {"ZN":"refp_b["+str(i)+"]", "A1":"P["+str(i+1)+"]", "A2":"N["+str(i+1)+"]"}).inst )
            self.items.append( instance(self.cnt+10, int(math.ceil(switch_size[i]/2)), "inv", {"ZN":"refn["+str(i)+"]", "I":"refn_b["+str(i)+"]"}).inst )
            self.items.append( instance(self.cnt+11, int(math.ceil(switch_size[i]/2)), "inv", {"ZN":"refp["+str(i)+"]", "I":"refp_b["+str(i)+"]"}).inst )
            self.cnt += 12
            if switch_size[i] > 2:
                self.items.append( instance(self.cnt, int(math.ceil(switch_size[i]/4)) , "inv", {"ZN":"P_B["+str(i+1)+"]", "I":"P_Q["+str(i+1)+"]"}).inst )
                self.items.append( instance(self.cnt+1, int(math.ceil(switch_size[i]/4)) , "inv", {"ZN":"P["+str(i+1)+"]", "I":"P_QB["+str(i+1)+"]"}).inst )
                self.items.append( instance(self.cnt+2, int(math.ceil(switch_size[i]/4)) , "inv", {"ZN":"N_B["+str(i+1)+"]", "I":"N_Q["+str(i+1)+"]"}).inst )
                self.items.append( instance(self.cnt+3, int(math.ceil(switch_size[i]/4)) , "inv", {"ZN":"N["+str(i+1)+"]", "I":"N_QB["+str(i+1)+"]"}).inst )
                self.cnt += 4

    def print(self, outfile=None):
        module = vast.ModuleDef("sar_logic", None, self.ports, self.items)
        rst = pycodegen.ASTCodeGenerator().visit(module)
        if outfile:
            original_stdout = sys.stdout
            with open(outfile,'w') as f:
                sys.stdout = f
                print(rst)
                sys.stdout = original_stdout
        else:
            print(rst)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-input', type=str, default=None, help='input json.')
    parser.add_argument('-output', type=str, default=None, help='output netlist.')
    args = parser.parse_args()
    if args.input:
        logic = sar_logic(args.input)
    else:
        logic = sar_logic()
    logic.print(args.output)
