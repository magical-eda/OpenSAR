import subprocess
import sys, os, time
import argparse
import json

from ax.service.managed_loop import optimize

class AutoSize:
    def __init__(self, cirFile, sysFile, resFile):
        # mos type are in um, cap type are in fF
        # This is hardencoded as in cirFile and legalized according to resolution
        self.cir = json.load(open(cirFile))
        self.sys = json.load(open(sysFile))
        self.par = self.cir['parameters']
        self.unit = self.cir['unit']
        self.w_res = self.cir['w_res'] # resolution of width in nm
        self.result = resFile
    def to_str(self, value, name):
        if self.par[name]['type'] == "mos":
            n = int(value) + 1
            w = int(value*1000/n) # in nm
            w = int(round(w/self.w_res)) * self.w_res # legalize
            self.final_param['w'+name] = str(w) + 'n'
            self.final_param['n'+name] = str(n) 
            return "w{name} = {w}n\nn{name} = {n}\n".format(name=name,w=w,n=n)
        elif self.par[name]['type'] == "cap":
            self.final_param[name] = "{:.2f}f".format(value)
            return "{} = {:.2f}f\n".format(name,value)
    def write_ocn(self, par_dict):
        self.final_param = {}
        self.ocn = open(self.cir['ocn'], 'w')
        temp_str = "vdd = {}\n".format(self.sys['vdd'])
        self.ocn.write(temp_str)
        for par in par_dict:
            temp_str = self.to_str(par_dict[par],par)
            self.ocn.write(temp_str)
        f = open(self.cir['template'],'r')
        self.ocn.write(f.read())
        f.close()
        self.ocn.close()
    def run(self):
        subprocess.run(["/bin/bash", self.cir['script'], self.cir['ocn']])
    def res(self):
        result = {}
        with open(self.cir['result'],'r') as f:
            lines = f.readlines()
            for l in lines:
                l = l.rstrip()
                w = l.split('=')
                result[w[0]] = float(w[1]) # write in original unit
        return result
    def simulation(self, par_dict):
        self.write_ocn(par_dict)
        self.run()
        res = self.res()
        return res
    def replay(self, playFile):
        size = json.load(open(self.result,'r'))
        res = self.simulation(size['parameters'])
        out = {"parameters":self.final_param , "result": res}
        with open(playFile,'w') as f:
            json.dump(out, f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-circuit', type=str, required=True, help='circuit json.')
    parser.add_argument('-system', type=str, required=True, help='system json.')
    parser.add_argument('-replay', type=str, required=True, help='result json.')
    parser.add_argument('-output', type=str, default=True, help='output json.')
    args = parser.parse_args()
    sizer = AutoSize(args.circuit,args.system,args.replay)
    sizer.replay(args.output)
