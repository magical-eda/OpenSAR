import subprocess
import sys
import argparse

class BufferSize:
    def __init__(self, capsize, vdd=1.2, stype='digital', nf=0):
    # capsize in fF
        self.capsize = capsize
        if stype == 'digital':
            self.script = './rise_fall_digital.sh'
            self.nf = int(nf)
            assert self.nf > 0, "nf or capsize not set for digital sim."
        else:
            self.script = './rise_fall_analog.sh'
        self.result = './rise_fall.txt'
        self.type = stype
        self.digital = [0.31, 0.41]
        self.analog = [0.3, 0.69]
        self.vdd = vdd
    def run(self):
        if self.type == 'digital':
            print("Running buffer sizing simulation on load nf:", self.nf, self.capsize, self.type)
            subprocess.run(["/bin/bash", self.script, str(self.nf), str(self.capsize), str(self.vdd), self.type])
        else:
            print("Running buffer sizing simulation on capsize:", self.capsize, self.type)
            subprocess.run(["/bin/bash", self.script, str(self.capsize), str(self.vdd), self.type])
        self.res()
    def res(self):
        self.time = []
        with open(self.result,'r') as f:
            lines = f.readlines()
            for l in lines:
                w = l.split()
                self.time.append([int(w[0]), max(float(w[1]),float(w[2]))])
    def rec(self, delay):
        print("Determing size based on delay: ", delay)
        for i in range(len(self.time)):
            if self.time[i][1] > delay:
                continue
            if self.type == 'digital':
                nmos = self.digital[0] * self.time[i][0]
                pmos = self.digital[1] * self.time[i][0]
            else:
                nmos = self.analog[0] * self.time[i][0]
                pmos = self.analog[1] * self.time[i][0]
            print("Resulting buffering size of ", self.time[i][0])
            return self.time[i][0], round(nmos,2), round(pmos,2)
        assert False, "Error, max size does not achieve delay requirement"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-capsize', type=str, required=True, help='unit cap size.')
    parser.add_argument('-type', type=str, required=True)
    parser.add_argument('-delay', type=float, required=True, help='delay in ns.')
    args = parser.parse_args()
    assert args.type in ['digital','analog']
    size = BufferSize(args.capsize, args.type)
    size.run()
    n, n_w, p_w = size.rec(args.delay)
    print(n, n_w, p_w)
