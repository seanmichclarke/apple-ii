#!/usr/bin/env python3
"""Experiments behind deck-code-audit.md. Every die face is computed by the ROM itself.

Usage: python3 deck_audit.py [rom] [cycle-cdff] [cycle-neg2] [cycle-cd58] [negsweep] [intbasic] [lattice]

  rom         ROM facts the deck relies on: dispatch table, RND instruction count, $F5CB/$F600
              layout, callers of HFIND, first RND(1) for every $CD, NEW/CLEAR vs the seed,
              and a check that direct ROM calls reproduce BASIC's INT(RND(1)*6)+1.
  cycle-*     Iterate RND(1) until the 5-byte seed repeats. For every output, compute the die
              face as INT(RND(1)*6)+1 using the ROM's own FMULT and INT, and compare it with
              the exact rational floor(6x)+1. Report face counts, chi-square, and pair/triple tables.
  negsweep    RND(-K) for K = 1..65535: distinct seeds, and the face INT(RND(-K)*6)+1.
  intbasic    Integer BASIC RND(6) over one full LFSR period (model validated in experiments.py).
  lattice     Exact truncation-bias arithmetic for an ideal 32-bit fraction.
"""
import sys
from collections import Counter
from fractions import Fraction
from py65.disassembler import Disassembler
from harness import Apple, boot_applesoft, rnd_call, seed

SIX = 0x0300                                   # packed 6.0 = 83 40 00 00 00
CHI2_CRIT = {5: (11.07, 15.09), 35: (49.80, 57.34), 215: (250.0, 265.0)}  # p=.05, p=.01


def chi2(counts, n_cells):
    n = sum(counts.values()) if isinstance(counts, Counter) else sum(counts)
    vals = list(counts.values()) if isinstance(counts, Counter) else list(counts)
    vals += [0] * (n_cells - len(vals))
    e = n / n_cells
    return sum((c - e) ** 2 / e for c in vals)


def exact(s):
    if s[0] == 0:
        return Fraction(0)
    m = (s[1] | 0x80) << 24 | s[2] << 16 | s[3] << 8 | s[4]
    return Fraction(m, 1 << 32) * Fraction(2) ** (s[0] - 0x80)


def fac_value(mem):
    if mem[0x9D] == 0:
        return Fraction(0)
    m = mem[0x9E] << 24 | mem[0x9F] << 16 | mem[0xA0] << 8 | mem[0xA1]
    v = Fraction(m, 1 << 32) * Fraction(2) ** (mem[0x9D] - 0x80)
    return -v if mem[0xA2] & 0x80 else v


def int_addr(mem):
    return mem[0xD082] | mem[0xD083] << 8


def rom_face(a):
    """FAC holds RND's result. Run FMULT by 6.0, then INT, both in ROM. Return the face."""
    mem = a.mem
    mem[SIX:SIX + 5] = [0x83, 0x40, 0, 0, 0]
    a.mpu.a, a.mpu.y = SIX & 0xFF, SIX >> 8
    a.call(0xE97F)
    a.call(int_addr(mem))
    return int(fac_value(mem)) + 1


def cycle(label, init):
    a = boot_applesoft()
    init(a)
    seen = {seed(a): 0}
    outs = []                                  # (exact x, rom face)
    i = 0
    while True:
        i += 1
        rnd_call(a, 1)
        s = seed(a)
        x = exact(s)
        outs.append((x, rom_face(a)))
        if s in seen:
            tail, period = seen[s], i - seen[s]
            break
        seen[s] = i
    cyc = outs[tail:tail + period]             # outputs number tail+1 .. tail+period
    faces = [f for _, f in cyc]
    mism = sum(1 for x, f in outs if int(6 * x) + 1 != f)
    over1 = sum(1 for x, _ in outs if x >= 1)
    c1 = Counter(faces)
    c2 = Counter(zip(faces, faces[1:] + faces[:1]))
    c3 = Counter(zip(faces, faces[1:] + faces[:1], faces[2:] + faces[:2]))
    print(f'{label}: tail {tail}, period {period}')
    print(f'  faces 1..6 over one full cycle: {[c1[k] for k in range(1, 7)]}  '
          f'expected {period/6:.1f} each; chi2 {chi2(c1, 6):.2f} on 5 df (crit .05 {CHI2_CRIT[5][0]})')
    print(f'  max |share-1/6| = {max(abs(c1[k]/period - 1/6) for k in range(1, 7)):.5f}; '
          f'1-sigma for {period} fair rolls = {((1/6)*(5/6)/period) ** .5:.5f}')
    if period >= 1000:
        print(f'  consecutive pairs chi2 {chi2(c2, 36):.2f} on 35 df (crit .05 {CHI2_CRIT[35][0]}); '
              f'triples chi2 {chi2(c3, 216):.1f} on 215 df (crit .05 {CHI2_CRIT[215][0]})')
    first = [f for _, f in outs[:20]]
    print(f'  first 20 faces from this start: {"".join(map(str, first))}')
    print(f'  ROM face vs exact floor(6x)+1 mismatches over all {len(outs)} outputs: {mism}; outputs >= 1: {over1}')
    if period < 1000:
        print(f'  full cycle faces: {"".join(map(str, faces))}')


def cold(cd):
    return lambda a: a.mem.__setitem__(slice(0xC9, 0xCE), [0x80, 0x4F, 0xC7, 0x52, cd])


def rom():
    a = Apple('Apple2_Plus.rom')
    mem = a.mem
    print('dispatch $D080..$D093:', ' '.join(f'${mem[0xD080+2*i] | mem[0xD081+2*i] << 8:04X}' for i in range(10)))
    print(f'INT entry (table slot 1) = ${int_addr(mem):04X}; RND (slot 9) = ${mem[0xD092] | mem[0xD093] << 8:04X}')
    d = Disassembler(a.mpu)
    pc, n = 0xEFAE, 0
    while pc <= 0xEFE7:
        ln, txt = d.instruction_at(pc)
        pc += ln; n += 1
    print(f'RND $EFAE..$EFE7 (through JMP STORE.FAC.AT.YX.ROUNDED): {n} instructions')
    print('bytes $EFAE..$EFB0 (overwritten by a 3-byte JMP):', bytes(mem[0xEFAE:0xEFB1]).hex(' '))
    print(f'$F600 = {mem[0xF600]:02X}; $F59C..$F59D = {mem[0xF59C]:02X} {mem[0xF59D]:02X} '
          f'-> target ${(0xF59E + (mem[0xF59D] - 256 if mem[0xF59D] > 127 else mem[0xF59D])):04X}; '
          f'HFIND room $F5CB..$F5FF = {0xF600 - 0xF5CB} bytes')
    refs = []
    for p in range(0xD000, 0xFFFE):
        if mem[p + 1] == 0xCB and mem[p + 2] == 0xF5 and mem[p] in (0x20, 0x4C, 0x6C):
            refs.append(f'${p:04X}:{mem[p]:02X}')
    print('JSR/JMP $F5CB anywhere in $D000-$FFFF:', refs or 'none')
    zp = [f'${p:04X}:{mem[p]:02X} {mem[p+1]:02X}' for p in range(0xD000, 0xFFFF)
          if mem[p] in (0x85, 0x86, 0x84, 0xE6, 0xC6) and 0xC9 <= mem[p + 1] <= 0xCD]
    print('byte patterns STA/STX/STY/INC/DEC zp $C9-$CD (may include data false positives):', zp or 'none')
    firsts = {}
    for cd in range(256):
        b = Apple('Apple2_Plus.rom')
        cold(cd)(b)
        rnd_call(b, 1)
        firsts[cd] = seed(b)
    target = firsts[0xFF]
    print(f'first RND(1) = .973136996 (seed {target.hex(" ")}) for $CD in',
          [f'${cd:02X}' for cd, s in firsts.items() if s == target],
          f'; distinct first outputs over 256 $CD values: {len(set(firsts.values()))}')
    b = boot_applesoft(0xFF)
    b.run('PRINT RND(1)\r')
    s1 = seed(b)
    b.run('NEW\rCLEAR\r10 PRINT 1\rRUN\rNEW\r')
    print(f'seed after RND(1): {s1.hex(" ")}; after NEW, CLEAR, RUN, NEW: {seed(b).hex(" ")}; unchanged: {s1 == seed(b)}')
    # direct-call faces must equal what BASIC prints for INT(RND(1)*6)+1
    c = boot_applesoft(0xFF)
    n0 = len(c.out)
    c.run('FOR I=1 TO 40: PRINT INT(RND(1)*6)+1;: NEXT\r')
    lines = ''.join(c.out[n0:]).split('\r')
    basic = next(l for l in lines if l.isdigit() and len(l) == 40)
    e = boot_applesoft(0xFF)
    direct = ''.join(str(rnd_call(e, 1) and rom_face(e)) for _ in range(40))
    print(f'BASIC INT(RND(1)*6)+1 x40 after cold start $CD=$FF: {basic}')
    print(f'direct ROM RND+FMULT+INT x40, same start:        {direct}  match={basic == direct}')


def negsweep():
    a = boot_applesoft()
    seeds, faces = set(), Counter()
    for k in range(1, 65536):
        rnd_call(a, -k)
        seeds.add(seed(a))
        faces[rom_face(a)] += 1
    print(f'negsweep: RND(-K), K=1..65535: {len(seeds)} distinct seeds; '
          f'INT(RND(-K)*6)+1 faces: {dict(sorted(faces.items()))}')


def intbasic():
    def step(s):
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
    s, vals = 0x1234, []
    start = None
    seen = {}
    while s not in seen:
        seen[s] = len(vals)
        v, s = step(s)
        vals.append(v)
    per = vals[seen[s]:]
    faces = Counter(v % 6 + 1 for v in per)
    print(f'intbasic: period {len(per)}, distinct values {len(set(per))}, range {min(per)}..{max(per)}; '
          f'RND(6)+1 faces over one period: {[faces[k] for k in range(1, 7)]}')
    big = Counter(v % 20000 for v in per)
    print(f'intbasic: RND(20000): residue 5 appears {big[5]}x, residue 15000 appears {big[15000]}x (range-bias example)')


def lattice():
    M = 1 << 32
    cnt = [0] * 6
    bounds = [-(-f * M // 6) for f in range(7)]          # ceil(f*2^32/6)
    cnt = [bounds[f + 1] - bounds[f] for f in range(6)]
    print(f'lattice: k/2^32, k=0..2^32-1, faces floor(6k/2^32)+1 counts: {cnt}; '
          f'max relative deviation {max(abs(c - M/6) for c in cnt)/(M/6):.2e}')


if __name__ == '__main__':
    todo = sys.argv[1:] or ['rom', 'lattice', 'intbasic', 'negsweep', 'cycle-cdff', 'cycle-neg2', 'cycle-cd58']
    for t in todo:
        if t == 'cycle-cdff':
            cycle('cold start $CD=$FF (the .973136996 machine)', cold(0xFF))
        elif t == 'cycle-neg2':
            cycle('RND(-2)', lambda a: rnd_call(a, -2))
        elif t == 'cycle-cd58':
            cycle('cold start $CD=$58 (the byte the ROM meant to copy)', cold(0x58))
        else:
            globals()[t]()
