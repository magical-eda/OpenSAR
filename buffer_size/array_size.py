from buffer_size import BufferSize
import json
import argparse

class ArraySize:
    def __init__(self, jsonFile):
        self.setup = json.load(open(jsonFile,'r'))
        self.sys = json.load(open(self.setup['sys_spec'],'r'))
        self.vdd = self.sys['vdd']
        self.capconf = json.load(open(self.setup['cap_config'],'r'))
        self.array = self.capconf['col_ary']
        unit_col = 1 + sum(self.capconf['row_ary'])
        self.array.append(self.capconf['ref'])
        for i in self.capconf['row_ary']:
            self.array.append(i*unit_col)
        self.test_array = []
        self.min_bit = self.setup['min_bit']
        for idx in self.min_bit:
            self.test_array.append(self.array[idx])
        self.test_array = self.test_array + self.array[self.min_bit[-1]+1:]
        print(self.test_array)
        self.cal_delay()
        self.getsize()
        self.getbuffer(self.setup['oversize'])
    def cal_delay(self, opt=False):
        print("Starting characterizing design.")
        delay = 0.5/(self.sys['rate']*self.sys['cycle']) 
        print("Half clock cycle is {:.2e}".format(delay))
        if opt:
            delay = delay - self.setup['prefix_delay']
        delay = 0.5 * delay * self.setup['overhead']
        print("Applying reduction of {} result in quater {:.2e}".format(self.setup['overhead'],delay))
        # ln2 ~ 0.69 ~ 0.7
        # ln(1.1/1.2) - ln(0.1/1.2) ~ 2.4
        if self.setup['mode'] == "Optimisitic":
            factor = 1
        else:
            factor = (self.sys['bit'] * 0.7) / 2.4
        self.setup['analog_delay'] = delay / factor
        print("Analog DAC delay is {:.2e} with {:.2f} factor".format(self.setup['analog_delay'], factor))
        if opt:
            self.setup['digital_delay'] = delay
        else:
            self.setup['digital_delay'] = delay - self.setup['prefix_delay']
        assert self.setup['digital_delay'] > 0, "Sampling rate too high, can not achieve timing closure."
        print("buffering delay is {:.2e}".format(self.setup['digital_delay']))
    def getsize(self):
        print("start analog switch sizing")
        nmos = []
        pmos = []
        nf = []
        res = []
        for mult in self.test_array:
            size = float(self.setup['capsize'][:-1]) * mult
            size = str(size) + self.setup['capsize'][-1]
            sizer = BufferSize(size,self.vdd,"analog")
            sizer.run()
            b, n, p = sizer.rec(float(self.setup['analog_delay']))
            res.append([n,p,b])
        print(res)
        idx = 0
        for num in self.min_bit:
            while len(nmos)<=num:
                nmos.append(res[idx][0])
                pmos.append(res[idx][1])
                nf.append(res[idx][2])
            idx += 1
        for i in range(idx,len(res)):
            nmos.append(res[i][0])
            pmos.append(res[i][1])
            nf.append(res[i][2])
        self.result = {'nmos':nmos, 'pmos':pmos, 'nf':nf}
        self.res = res
        return nmos, pmos
    def getbuffer(self, oversize=2.0):
        print("start sar logic buffer sizing")
        res = []
        nf = []
        size = float(self.setup['routecap'][:-1]) * self.setup['routelen']
        size = str(size) + self.setup['routecap'][-1]
        print("Estimated routing capacitor:", size)
        for idx in range(len(self.res)):
            sizer = BufferSize(size,self.vdd,"digital",self.res[idx][2]*oversize)
            sizer.run()
            b, n, p = sizer.rec(float(self.setup['digital_delay']))
            res.append(b)
        idx = 0
        for num in self.min_bit:
            while len(nf)<=num:
                nf.append(res[idx])
            idx += 1
        for i in range(idx,len(res)):
            nf.append(res[i])
        self.nf = nf
        return nf
    def write_array(self, outfilea, outfiled):
        print("writing analog sizing in ", outfilea)
        with open(outfilea,'w') as f:
            json.dump(self.result,f)
        print("writing logic buffer in ", outfiled)
        with open(outfiled,'w') as f:
            json.dump(self.nf,f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-input', type=str, required=True, help='input json.')
    parser.add_argument('-outputa', type=str, required=True, help='output analog json.')
    parser.add_argument('-outputd', type=str, required=True, help='output logic json.')
    args = parser.parse_args()
    array = ArraySize(args.input)
    array.write_array(args.outputa, args.outputd)
