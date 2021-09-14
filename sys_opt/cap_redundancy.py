from gekko import GEKKO
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument('-input', type=str, required=True, help='system spec json.')
parser.add_argument('-output', type=str, required=True, help='cap array config.')
parser.add_argument('-ignore', type=int, default=2, help='redundancy cycle.')
args = parser.parse_args()

setup = json.load(open(args.input,'r'))

m = GEKKO() # Initialize gekko
m.options.SOLVER=1  # APOPT is an MINLP solver

# optional solver settings with APOPT
m.solver_options = ['minlp_maximum_iterations 100000', \
                    # minlp iterations with integer solution
                    'minlp_max_iter_with_int_sol 5000', \
                    # treat minlp as nlp
                    'minlp_as_nlp 0', \
                    # nlp sub-problem max iterations
                    'nlp_maximum_iterations 500', \
                    # 1 = depth first, 2 = breadth first
                    'minlp_branch_method 1', \
                    # maximum deviation from whole number
                    'minlp_integer_tol 0.05', \
                    # covergence tolerance
                    'minlp_gap_tol 0.001']


col = setup["column_bit"]#4
bit = setup["bit"] - 1 #9
red = setup["redundant_cycle"]  #1
ignore = args.ignore #2 # 1 or 2
# Initialize variables

assert col>=2, "Column too small"
z = [0.5,1]
for i in range(2,col):
    z.append(m.Var(1,lb=1,ub=2**(col),integer=True))
# Dummy column
z.append(m.Var(1,lb=1,ub=2**(col),integer=True))
for i in range(col+2,bit+red):
    z.append(m.Var(1,lb=1,ub=2**(bit+red-col),integer=True))
print(len(z))

x = []
t = 1
for i in range(col+1):
    x.append(2*z[i])
    t = t + 2*z[i]
t = t - x[-1] # subtract out dummy column
x.append(t)
for i in range(col+1,bit+red-1):
    x.append(2*t*z[i])

assert len(x) == bit + red, len(x)

for i in range(2,bit+red):
    m.Equation(x[i]-x[i-1]>=0)

x_square = []
x_sum = []
x_square_sum = []
for i in range(bit+red):
    x_square.append(x[i]**2)
    x_sum.append(m.sum(x[:i+1]))
for i in range(bit+red):
    x_square_sum.append(m.sum(x_square[:i+1]))
# Coverage
sum_x = m.sum(x)
m.Equation(sum_x>=2**bit)
m.Equation(sum_x<=2**bit+2**(col+1))
temp = 1    
for i in range(ignore,bit+red):
    m.Equation(x_sum[i-1]-x[i]+1>=0)
    temp = m.min2(temp,(x_sum[i-1]-x[i]+1)**2/(1+x_square_sum[i]))   
m.Obj(-temp) # Objective
m.solve(disp=True) # Solve
solution = []
col_ary = []
row_ary = [1]
reference_bit_size = 0
c = 0
for item in z:
    if hasattr(item,'value'):
        solution.append(item.value[-1])
        if c < setup['column_bit']:
            col_ary.append(int(2*item.value[-1]))
        elif c == col:
            reference_bit_size = int(2*item.value[-1])
        else:
            row_ary.append(int(2*item.value[-1]))
    else:
        solution.append(item)
        if c < setup['column_bit']:
            col_ary.append(int(2*item))
        elif c == col:
            reference_bit_size = int(2*item)
        else:
            row_ary.append(int(2*item))
    c = c + 1
if bit > 9:
    output_dict = {"col_ary": col_ary, "row_ary": row_ary, "ref": reference_bit_size-2}
else:
    output_dict = {"col_ary": col_ary, "row_ary": row_ary, "ref": reference_bit_size}
with open(args.output,'w') as f:
    json.dump(output_dict,f)
sol_bits = []
t = 1
for i in range(col+1):
    sol_bits.append(int(2*solution[i]))
    t = t + 2*solution[i]
t = t - 2*solution[col] # subtract out dummy column
sol_bits.append(int(t))
for i in range(col+1,bit+red-1):
    sol_bits.append(int(2*t*solution[i]))
diff = []
for i in range(1,len(sol_bits)):
    diff.append(sum(sol_bits[:i])-sol_bits[i]+1)

print(solution)
print('Objective: ' + str(m.options.objfcnval))
print('Covered value: ', x_sum[-1].value)
print(sum(sol_bits))
print('Solutions:',sol_bits)
print('Diff:',diff)
