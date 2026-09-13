#!/usr/bin/env python3
"""Reproduce the measured claims in applesoft-rnd.md §5 and integer-basic-rnd.md §3.

Usage: python3 experiments.py [sweep] [cycles] [fadd] [bits] [cost] [resets] [intbasic]
(no arguments = all; 'cycles' and 'fadd' take several minutes each under py65).
Run verify.py once first so the ROM images are downloaded.
"""
import sys
from collections import Counter
from harness import Apple, boot_applesoft, boot_integer, rnd_call, seed, set_fac_int

COLD = bytes([0x80, 0x4F, 0xC7, 0x52, 0x00])


def trajectory(a, start, n):
    a.mem[0xC9:0xCE] = list(start)
    out = []
    for _ in range(n):
        rnd_call(a, 1)
        out.append(seed(a))
    return out


def sweep():
    firsts = Counter()
    for cd in range(256):
        a = boot_applesoft(cd)
        vals = []
        for _ in range(5):
            rnd_call(a, 1); vals.append(seed(a))
        firsts[tuple(vals)] += 1
    print(f'sweep: 256 values of $CD -> {len(firsts)} distinct 5-output sequences')


def cycles():
    a = boot_applesoft()
    starts = [('cold $CD=00', lambda: a.mem.__setitem__(slice(0xC9, 0xCE), list(COLD))),
              ('cold $CD=FF', lambda: a.mem.__setitem__(slice(0xC9, 0xCE), list(COLD[:4]) + [0xFF]))]
    for k in (1, 2, 12345, 54321):
        starts.append((f'RND(-{k})', (lambda k: lambda: rnd_call(a, -k))(k)))
    for label, init in starts:
        init()
        seen = {seed(a): 0}
        i = 0
        while True:
            i += 1
            rnd_call(a, 1)
            s = seed(a)
            if s in seen:
                print(f'cycles: {label}: tail {seen[s]}, period {i - seen[s]}')
                break
            seen[s] = i


def fadd():
    a = boot_applesoft(); b = boot_applesoft()
    list.__setitem__(b.mem, slice(0xEFC9, 0xEFCC), [0xEA, 0xEA, 0xEA])  # JSR FADD -> NOPs
    ta = trajectory(a, COLD, 57021)
    tb = trajectory(b, COLD, len(ta))
    first = next((i + 1 for i in range(len(ta)) if ta[i] != tb[i]), None)
    changed = 0
    for s in [COLD] + ta[:-1]:
        a.mem[0xC9:0xCE] = list(s); rnd_call(a, 1)
        b.mem[0xC9:0xCE] = list(s); rnd_call(b, 1)
        changed += seed(a) != seed(b)
    print(f'fadd: sequence without FADD first diverges at call {first}; per-step changes {changed} of {len(ta)}')


def bits():
    a = boot_applesoft()
    t = trajectory(a, COLD, 57021)
    F = []
    for s in t:
        m = (s[1] | 0x80) << 24 | s[2] << 16 | s[3] << 8 | s[4]
        sh = 0x80 - s[0]
        F.append(m >> sh if sh < 32 else 0)
    b25 = [(f >> 7) & 1 for f in F]
    b24 = [(f >> 8) & 1 for f in F]
    w25 = [sum(b25[i:i + 200]) for i in range(len(F) - 200)]
    w24 = [sum(b24[i:i + 200]) for i in range(len(F) - 200)]
    print(f'bits: P(bit25)={sum(b25)/len(F):.4f}  200-windows bit25 {min(w25)}-{max(w25)}, bit24 {min(w24)}-{max(w24)}; first 200: {sum(b25[:200])}/{sum(b24[:200])}')
    x = [f / 2**32 for f in F]
    n = 16
    pairs = Counter((int(x[i] * n), int(x[i + 1] * n)) for i in range(len(x) - 1))
    e = (len(x) - 1) / n / n
    chi = sum((pairs.get((i, j), 0) - e) ** 2 / e for i in range(n) for j in range(n))
    print(f'bits: serial-pair chi2 for INT(RND*16) = {chi:.1f} on {n*n-1} df')


def cost():
    a = boot_applesoft()
    a.mem[0xC9:0xCE] = list(COLD)
    r = [rnd_call(a, 1) for _ in range(3000)]
    ins, cyc = [x[0] for x in r], [x[1] for x in r]
    print(f'cost: RND(1) instr {min(ins)}-{max(ins)} mean {sum(ins)//len(ins)}; cycles {min(cyc)}-{max(cyc)} mean {sum(cyc)//len(cyc)}')
    print(f'cost: RND(0) {rnd_call(a, 0)}; RND(-1) {rnd_call(a, -1)}')


def resets():
    a = boot_applesoft()
    a.run('PRINT RND(1)\rPRINT RND(1)\r')
    before = seed(a).hex(' ')
    a.mpu.pc = a.mem[0xFFFC] | a.mem[0xFFFD] << 8
    a.run('')
    print(f'resets: Ctrl-RESET seed {before} -> {seed(a).hex(" ")}')
    a.run('PRINT RND(1)\rCALL -151\rE000G\r')
    print(f'resets: after E000G seed = {seed(a).hex(" ")}')


def intbasic():
    def model_step(s):
        l, h = s & 255, s >> 8
        if h == 0:
            h = 1 if l == 0 else 0
        h &= 0x7F
        v = l | h << 8
        for _ in range(17):
            c = ((((h << 1) & 255) + 0x40) >> 7) & 1
            h = ((h << 1) | (l >> 7)) & 255
            l = ((l << 1) | c) & 255
        return v, l | h << 8
    cap = []
    a = boot_integer()
    n = len(a.out)
    a.run('10 FOR I=1 TO 300\r20 PRINT RND(32767)\r30 NEXT I\r40 END\r')
    n = len(a.out)
    a.run('RUN\r', hooks={0xEF51: lambda m: cap.append(m.mem[0x4E] | m.mem[0x4F] << 8)})
    printed = [int(t) for t in ''.join(a.out[n:]).split('\r') if t.strip().isdigit()]
    ok, s = 0, cap[0]
    for i, st in enumerate(cap):
        if st != s:
            break
        v, s = model_step(st)
        if v % 32767 != printed[i]:
            break
        ok += 1
    s, seen, i = 0x1234, {}, 0
    while s not in seen:
        seen[s] = i; _, s = model_step(s); i += 1
    print(f'intbasic: model matched ROM on {ok}/{len(cap)} calls; LFSR period from $1234 = {i - seen[s]}')


if __name__ == '__main__':
    todo = sys.argv[1:] or ['sweep', 'cost', 'resets', 'bits', 'intbasic', 'fadd', 'cycles']
    for name in todo:
        globals()[name]()
