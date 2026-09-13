#!/usr/bin/env python3
"""Re-check every number the decks put on screen by running the genuine Apple ][+ ROM.

Usage: python verify_headline_numbers.py <Apple2_Plus.rom>
Needs: py65 (pip install py65). The ROM is the 12K image ($D000-$FFFF) shipped with
AppleWin (resource/Apple2_Plus.rom, SHA-1 33a24f5489ba9195b44be77d9afb2252594cb5c7).
Runs in about 15 seconds.
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROM_PATH = sys.argv[1]
sys.argv = [sys.argv[0], ROM_PATH]      # rnd_emu reads the ROM path from argv at import
import rnd_emu as E                     # noqa: E402

rom = open(ROM_PATH, 'rb').read()


def rom_bytes(addr, n):
    return ' '.join('%02X' % b for b in rom[addr - 0xD000:addr - 0xD000 + n])


def cold(cd):
    mpu, mem = E.make_mpu()
    mem[0xC9:0xCE] = bytes([0x80, 0x4F, 0xC7, 0x52, cd])
    return mpu, mem


print('ROM SHA-1            ', hashlib.sha1(rom).hexdigest())
print('$F123 seed table     ', rom_bytes(0xF123, 5), '  (fifth byte $58 is never copied)')
print('$F150 copy loop      ', rom_bytes(0xF150, 12), '  (LDX #$1C: one short)')
print('$EFA6 RND constants  ', rom_bytes(0xEFA6, 8), '  (two 4-byte constants)')
print('$F600                ', rom_bytes(0xF600, 1), '  (60 = RTS)')

refs = ['$%04X' % (0xD000 + i) for i in range(len(rom) - 2)
        if rom[i] in (0x20, 0x4C) and rom[i + 1] == 0xCB and rom[i + 2] == 0xF5]
print('JSR/JMP to $F5CB     ', refs or 'none in $D000-$FFFF')
branches = []
for i in range(len(rom) - 1):
    if rom[i] in (0x10, 0x30, 0x50, 0x70, 0x90, 0xB0, 0xD0, 0xF0):
        off = rom[i + 1] - 256 if rom[i + 1] > 127 else rom[i + 1]
        if 0xD000 + i + 2 + off == 0xF600:
            branches.append('$%04X' % (0xD000 + i))
print('branches to $F600    ', branches, '  (HLIN exits through it)')
print()

for cd in (0xFF, 0xFE, 0x00, 0x58, 0xAA):
    mpu, mem = cold(cd)
    E.call_rnd(mpu, mem, 1)
    print('first RND(1), $CD=$%02X  %.9f' % (cd, E.fac_value(mem)))

firsts = set()
for cd in range(256):
    mpu, mem = cold(cd)
    E.call_rnd(mpu, mem, 1)
    firsts.add(round(E.fac_value(mem), 9))
print('distinct first values over all 256 $CD values:', len(firsts))

mpu, mem = E.make_mpu()
E.call_rnd(mpu, mem, -1)
print('PRINT RND(-1)          %.9g' % E.fac_value(mem))

for cd in (0x58,):
    mpu, mem = cold(cd)
    seen = {E.seed(mem): 0}
    for i in range(1, 40000):
        E.call_rnd(mpu, mem, 1)
        st = E.seed(mem)
        if st in seen:
            print('$CD=$%02X enters a %d-number loop after %d calls' % (cd, i - seen[st], seen[st]))
            break
        seen[st] = i
