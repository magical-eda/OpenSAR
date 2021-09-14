import Magical
import gdspy
import opensar
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-input', type=str, required=True, help='system spec json.')
parser.add_argument('-mode', type=int, required=True, help='0 for components, 1 for integration.')
parser.add_argument('-switch_space', type=float, default=1.4, help='space in switch for pin access. should multiples of 0.2')
parser.add_argument('-comp_space', type=float, default=2.0, help='comp_space for routability. should multiples of 0.2')
args = parser.parse_args()

sar = opensar.SAR_ADC(args.input)
if args.mode == 0:
    sar.customCell(True, False)
    sar.capSwitch()
    sar.customCell(False, True)
elif args.mode == 1:
    sar.customCell(False, False)
    sar.capSwitch(pg_space=args.switch_space)
    sar.sarLogic(False)
    sar.place(n_fac=args.comp_space)
    sar.run_route(True)
    sar.run_route(False)
    sar.wrapup()
else:
    sar.customCell(True, False)
    sar.capSwitch(pg_space=args.switch_space)
    sar.customCell(False, True)
    sar.customCell(False, False)
    sar.sarLogic(False)
    sar.place(n_fac=args.comp_space)
    sar.run_route(True)
    sar.run_route(False)
    sar.wrapup()

