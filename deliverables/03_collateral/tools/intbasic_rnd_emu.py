#!/usr/bin/env python3
# Evidence for DESIGN_INTENT.md section 2.3. Run: python3 intbasic_rnd_emu.py
# Exact emulation of Integer BASIC RND state update at $EF4E-$EF72 (Santa-Maria disassembly)
def rnd_step(L, H):
    out_lo = L
    A = H
    if A == 0:
        C = 1 if 0 >= L else 0      # CMP RNDL: carry set iff A >= RNDL
        A = (A + 0 + C) & 0xFF      # ADC #$00
    A &= 0x7F                       # AND #$7F
    H = A
    out = (H << 8) | out_lo
    for _ in range(0x11):           # LDY #$11 ... DEY/BNE
        A = (H << 1) & 0xFF          # LDA RNDH ; ASL A (carry discarded by CLC)
        A = A + 0x40                 # CLC ; ADC #$40
        A &= 0xFF
        C = (A >> 7) & 1             # ASL A -> carry = bit7
        nl = ((L << 1) | C)          # ROL RNDL
        C2 = (nl >> 8) & 1
        L = nl & 0xFF
        H = ((H << 1) | C2) & 0xFF   # ROL RNDH
    return out, L, H

# 1) is feedback bit == bit14 XOR bit13 of the 16-bit register?
ok = True
for s in range(1 << 16):
    H, L = s >> 8, s & 0xFF
    fb = ((((H << 1) & 0xFF) + 0x40) & 0xFF) >> 7
    if fb != (((s >> 14) ^ (s >> 13)) & 1):
        ok = False; break
print("feedback == b14 xor b13:", ok)

# 2) period of successive RND outputs with no keypress, from several starts
for start in [(0,0),(1,0),(0x34,0x12),(0xFF,0xFF)]:
    L, H = start
    seen = {}
    i = 0
    while True:
        out, L, H = rnd_step(L, H)
        key = (L, H & 0x7F)
        if key in seen:
            print("start", start, "first out", hex(rnd_step(*start)[0]), "cycle length", i - seen[key], "after", seen[key]); break
        seen[key] = i; i += 1
# 3) KEYIN loop rate
clk = 1020484  # Hz, 14.31818MHz*65/912 average per McFadden/awanderin
print("increments/sec at 15 cycles/loop:", clk/15, " seconds per 16-bit wrap:", 65536/(clk/15))
