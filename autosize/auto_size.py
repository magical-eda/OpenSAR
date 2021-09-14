import subprocess
import sys, os, time
import argparse
import json
import math

from ax.service.managed_loop import optimize
from ax.service.ax_client import AxClient

class AutoSize:
    def __init__(self, cirFile, sysFile, resFile, logFile='./log/perf.txt'):
        # mos type are in um, cap type are in fF
        # This is hardencoded as in cirFile and legalized according to resolution
        self.cir = json.load(open(cirFile))
        self.sys = json.load(open(sysFile))
        self.par = self.cir['parameters']
        # unit is to convert raw result to appropriate range
        self.unit = self.cir['unit']
        self.w_res = self.cir['w_res'] # resolution of width in nm
        self.logDir = './log/'
        self.log = open(logFile, 'w')
        self.save_freq = 200
        self.time = time.time()
        self.result = resFile
        # Formulate ax parameters
        self.ax_para = []
        for name in self.par:
            p = {"name": name, "type":"range", "value_type":"float"}
            d = self.par[name]['default']
            p["bounds"] = [d*self.cir['range'][0],d*self.cir['range'][1]]
            if "log" in self.par[name]:
                p["log_scale"] = self.par[name]["log"]
            self.ax_para.append(p)
        self.ax_const = []
        self.const_val = {}
        # System to block performance translate
        for name in self.cir['constraints']:
            temp = name + " " + self.cir['constraints'][name] + " "
            if name == "input_ref_noise":
                lsb = self.sys['vdd'] * self.unit[name] / (2 ** (self.sys['bit']-1)) #* math.sqrt(2))
                v = lsb / 4 # This is hard encoded
            elif name == "delay":
                v = 0.5 * self.unit[name]/ (self.sys['rate'] * self.sys['cycle'])
            else:
                assert False, "Unsupported constraint: " + name
            if self.cir['constraints'][name][0] == "<":
                print(name, name in self.cir['overhead'], v)
                if name in self.cir['overhead']:
                    v = v* (1-self.cir['overhead'][name])
                self.const_val[name] = v
                temp = "{} {} {:.2f}".format(name, self.cir['constraints'][name], v)
            elif self.cir['constraints'][name][0] == ">":
                if name in self.cir['overhead']:
                    v = v* (1+self.cir['overhead'][name])
                self.const_val[name] = v
                temp = "{} {} {:.2f}".format(name, self.cir['constraints'][name], v)
            else:
                assert False, "Unsupported type for constraint: " + name
            self.ax_const.append(temp)
        print(self.ax_para)
        print(self.ax_const)
        # Handling errors
        self.worst_obj = None
        self.worst_const = {}
        for name in self.cir['constraints']:
            self.worst_const[name] = None
    def to_str(self, value, name):
        if self.par[name]['type'] == "mos":
            n = int(value) + 1
            w = int(value*1000/n) # in nm
            w = int(round(w/self.w_res)) * self.w_res # legalize
            return "w{name} = {w}n\nn{name} = {n}\n".format(name=name,w=w,n=n)
        elif self.par[name]['type'] == "cap":
            return "{} = {:.2f}f\n".format(name,value)
    def write_ocn(self, par_dict):
        log = "{:.2f}: ".format(time.time()-self.time)
        self.ocn = open(self.cir['ocn'], 'w')
        temp_str = "vdd = {}\n".format(self.sys['vdd'])
        self.ocn.write(temp_str)
        for par in par_dict:
            temp_str = self.to_str(par_dict[par],par)
            self.ocn.write(temp_str)
            log = log + "{}:{:.5f} ".format(par,par_dict[par])
        self.log.write(log+'\n')
        f = open(self.cir['template'],'r')
        self.ocn.write(f.read())
        f.close()
        self.ocn.close()
    def run(self):
        subprocess.run(["/bin/bash", self.cir['script'], self.cir['ocn']])
    def res(self):
        result = {}
        log = "{:.2f}: ".format(time.time()-self.time)
        with open(self.cir['result'],'r') as f:
            lines = f.readlines()
            for l in lines:
                l = l.rstrip()
                log = log + l + ' '
                w = l.split('=')
                result[w[0]] = (float(w[1])*self.unit[w[0]], 0.0)
        self.log.write(log+'\n')
        return result
    def assesment(self, res):
        error = False
        obj_name = self.cir['objective']['name']
        if obj_name in res:
            if self.worst_obj:
                if self.cir['objective']['minimize']:
                    self.worst_obj = max(self.worst_obj, res[obj_name][0])
                else:
                    self.worst_obj = min(self.worst_obj, res[obj_name][0])
            else:
                self.worst_obj = res[obj_name][0]
        else:
            error = True
            res[obj_name] = (self.worst_obj, 0.0)
        log = "obj: {:.2f} ".format(res[obj_name][0])
        for name in self.cir['constraints']:
            if name in res:
                if self.worst_const[name]:
                    if self.cir['constraints'][name][0] == "<":
                        self.worst_const[name] = max(self.worst_const[name], res[name][0])
                    else:
                        self.worst_const[name] = min(self.worst_const[name], res[name][0])
                else:
                    self.worst_const[name] = res[name][0]
            else:
                error = True
                res[name] = (self.worst_const[name], 0.0)
            if self.cir['constraints'][name][0] == "<":
                status = res[name][0] <= self.const_val[name]
            else:
                status = res[name][0] >= self.const_val[name]
            log = log + "{}: {} ".format(name,status)
        log = log + "error: {}".format(error) + '\n'
        self.log.write(log)
        self.log.flush()
        os.fsync(self.log)
    def simulation(self, par_dict):
        self.write_ocn(par_dict)
        self.run()
        res = self.res()
        self.assesment(res)
        return res
    def opt_simple(self):
        best_parameters, values, experiment, model = optimize(
            parameters=self.ax_para, 
            experiment_name="auto circuit sizing",
            objective_name=self.cir["objective"]["name"],
            evaluation_function=lambda p : self.simulation(p),
            minimize=self.cir["objective"]["minimize"],
            outcome_constraints=self.ax_const,
            total_trials=self.cir["iteration"]
            )
        means, _ = values
        result = {"parameters":best_parameters, "values":means}
        with open(self.result,'w') as f:
            json.dump(result,f)
    def opt(self):
        ax_client = AxClient()
        ax_client.create_experiment(
            name='analog_sizing',
            parameters=self.ax_para,
            objective_name=self.cir["objective"]["name"],
            minimize=self.cir["objective"]["minimize"],
            outcome_constraints=self.ax_const
            )
        for i in range(self.cir["iteration"]):
            p, trial_index = ax_client.get_next_trial()
            ax_client.complete_trial(trial_index=trial_index, raw_data=self.simulation(p))
            if i % self.save_freq == 0:
                file_name = self.logDir + 'run_' + str(i) + '.json'
                ax_client.save_to_json_file(file_name)
            i += 1
        ax_client.save_to_json_file(file_name)
        best_parameters, value = ax_client.get_best_parameters()
        means, _ = value
        result = {"parameters":best_parameters, "values":means}
        with open(self.result,'w') as f:
            json.dump(result,f)
        file_name = self.logDir + 'run_' + str(i) + '.json'
    def load(self, filename):
        ax_client = AxClient()
        ax_client = ax_client.load_from_json_file(filename)
        for i in range(self.cir["iteration"]):
            p, trial_index = ax_client.get_next_trial()
            ax_client.complete_trial(trial_index=trial_index, raw_data=self.simulation(p))
            if i % self.save_freq == 0:
                file_name = self.logDir + 'run_' + str(i) + '.json'
                ax_client.save_to_json_file(file_name)
            i += 1
        best_parameters, value = ax_client.get_best_parameters()
        means, _ = value
        result = {"parameters":best_parameters, "values":means}
        with open(self.result,'w') as f:
            json.dump(result,f)
        file_name = self.logDir + 'run_' + str(i) + '.json'
        ax_client.save_to_json_file(file_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-circuit', type=str, required=True, help='circuit json.')
    parser.add_argument('-system', type=str, required=True, help='system json.')
    parser.add_argument('-result', type=str, required=True, help='result json.')
    parser.add_argument('-log', type=str, default=None, help='log directory.')
    parser.add_argument('-load', type=str, default=None, help='load json experiment.')
    args = parser.parse_args()
    if args.log:
        sizer = AutoSize(args.circuit,args.system,args.result,args.log)
    else:
        sizer = AutoSize(args.circuit,args.system,args.result)
    if args.load:
        sizer.load(args.load)
    else:
        sizer.opt()
