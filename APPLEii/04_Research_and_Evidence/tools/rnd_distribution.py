"""Distribution/uniformity checks on genuine Applesoft RND output (Apple ][+ ROM, py65).
python rnd_distribution.py <rom>
1) First RND(1) value after cold start for every $CD in 0..255.
2) For cold start $CD=$FF (the case that prints .973136996): die-roll INT(RND(1)*6)+1 counts and
   chi-square over (a) the first 600 calls, (b) the first 6000, (c) exactly one full 37,758-value cycle;
   byte-level and 10-bin chi-square over the cycle; lag-1 serial correlation.
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rnd_emu as E

rom = sys.argv[1]
firsts = {}
for cd in range(256):
    mpu, mem = E.make_mpu()
    mem[0xC9:0xCE] = bytes([0x80, 0x4F, 0xC7, 0x52, cd])
    E.call_rnd(mpu, mem, 1)
    firsts[cd] = round(E.fac_value(mem), 9)
target = [cd for cd, v in firsts.items() if abs(v - 0.973136996) < 5e-10]
print(json.dumps({'first_value_cd_FF': firsts[0xFF], 'cd_values_giving_.973136996': target,
                  'distinct_first_values': len(set(firsts.values())),
                  'first_value_cd_00': firsts[0], 'first_value_cd_58': firsts[0x58]}))

PRE, CYC = 6818, 37758  # from rnd_experiments cold FF
mpu, mem = E.make_mpu()
mem[0xC9:0xCE] = bytes([0x80, 0x4F, 0xC7, 0x52, 0xFF])
vals = []
for i in range(PRE + CYC + 1):
    E.call_rnd(mpu, mem, 1)
    vals.append((E.fac_value(mem), E.seed(mem)))
assert vals[PRE][1] == vals[PRE + CYC][1], 'cycle bounds wrong'
seq = [v for v, _ in vals]
cycle = seq[PRE:PRE + CYC]

def chi(counts):
    n = sum(counts); k = len(counts); e = n / k
    return sum((c - e) ** 2 / e for c in counts), k - 1

def die(xs):
    c = [0] * 6
    for x in xs:
        c[int(x * 6)] += 1
    return c

out = {}
for name, xs in [('first600', seq[:600]), ('first6000', seq[:6000]), ('one_full_cycle', cycle)]:
    c = die(xs); x2, df = chi(c)
    out[name] = {'n': len(xs), 'die_counts_1to6': c, 'chi2': round(x2, 2), 'df': df}
bins10 = [0] * 10
for x in cycle:
    bins10[int(x * 10)] += 1
out['cycle_10bins'] = {'counts': bins10, 'chi2': round(chi(bins10)[0], 2), 'df': 9}
b256 = [0] * 256
for x in cycle:
    b256[int(x * 256)] += 1
out['cycle_256bins_chi2'] = round(chi(b256)[0], 1)
m = sum(cycle) / len(cycle)
num = sum((cycle[i] - m) * (cycle[(i + 1) % len(cycle)] - m) for i in range(len(cycle)))
den = sum((x - m) ** 2 for x in cycle)
out['cycle_mean'] = round(m, 5)
out['cycle_lag1_serial_corr'] = round(num / den, 5)
out['distinct_values_in_cycle'] = len(set(cycle))
# the 202-cycle (cold $CD=$58, preperiod 15382)
mpu, mem = E.make_mpu()
mem[0xC9:0xCE] = bytes([0x80, 0x4F, 0xC7, 0x52, 0x58])
for i in range(15382):
    E.call_rnd(mpu, mem, 1)
c202 = []
for i in range(202):
    E.call_rnd(mpu, mem, 1)
    c202.append(E.fac_value(mem))
d = die(c202)
out['cycle202_die_counts'] = d
out['cycle202_chi2'] = round(chi(d)[0], 2)
print(json.dumps(out))
