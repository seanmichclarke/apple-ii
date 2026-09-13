"""Run the genuine Integer BASIC RND seed-update code (original Apple II ROM, $EF51) under py65,
using the calling convention from Sander-Cederlof, Apple Assembly Line, Aug 1981:
LDX #$20 ; arg in $CE/$CF ; LDY #0 ; JSR $EF51 ; result lo=$50,X hi=$A0,X.
No keyboard wait between calls, so $4E/$4F evolve only through RND itself.
python intbasic_rnd_emu.py <Apple2.rom> [calls] [seed_hex] [arg]"""
import sys
from collections import Counter
from py65.devices.mpu6502 import MPU

rom = open(sys.argv[1], 'rb').read(); assert len(rom) == 12288
N = int(sys.argv[2]) if len(sys.argv) > 2 else 32768
seed = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0x1234
arg = int(sys.argv[4]) if len(sys.argv) > 4 else 1000
mem = bytearray(65536); mem[0xD000:] = rom
harness = [0xA2, 0x20, 0xA9, arg & 0xFF, 0x85, 0xCE, 0xA9, arg >> 8, 0x85, 0xCF,
           0xA0, 0x00, 0x20, 0x51, 0xEF, 0x00]
mem[0x0300:0x0300 + len(harness)] = bytes(harness)
mpu = MPU(memory=mem)
mem[0x4E], mem[0x4F] = seed & 0xFF, seed >> 8
values, outs = [], []
for i in range(N):
    s = mem[0x4E] | (mem[0x4F] << 8)
    h = (s >> 8) & 0x7F
    if s == 0: h = 1  # ROM changes 0000 to 0100 before use
    values.append((h << 8) | (s & 0xFF))
    mpu.pc = 0x0300; mpu.sp = 0xFF
    n = 0
    while mpu.pc != 0x030F:
        mpu.step(); n += 1
        if n > 100000: raise RuntimeError('runaway at %04X' % mpu.pc)
    x = mpu.x
    outs.append(mem[0x50 + x] | (mem[0xA0 + x] << 8))
c = Counter(values)
missing = [v for v in range(1, 0x8000) if v not in c]
print('calls', N, 'distinct 15-bit working values', len(c), 'missing (1..7FFF)', len(missing),
      'first missing', ['%04X' % v for v in missing[:5]], 'max repeat', max(c.values()))
print('block $2000-$20FF hits:', sum(c[v] for v in range(0x2000, 0x2100)),
      ' block $6000-$60FF hits:', sum(c[v] for v in range(0x6000, 0x6100)))
oc = Counter(o // 100 for o in outs)
print('RND(%d) outputs: min %d max %d; counts per 100-bucket: %s' % (arg, min(outs), max(outs), [oc[k] for k in range(10)]))
print('first seeds:', ['%04X' % v for v in values[:6]])
