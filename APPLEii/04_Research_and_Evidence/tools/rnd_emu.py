"""Run the genuine Applesoft RND ($EFAE) from an Apple ][+ ROM image under py65.
Usage: python rnd_emu.py <Apple2_Plus.rom>   (12K image, $D000-$FFFF)
State of the generator = RNDSEED, 5 bytes at $C9-$CD."""
import sys, time
from py65.devices.mpu6502 import MPU
from py65.memory import ObservableMemory

ROM = open(sys.argv[1], 'rb').read()
assert len(ROM) == 12288

def make_mpu():
    mem = bytearray(65536)
    mem[0xD000:0x10000] = ROM
    # harness at $0300: JSR $EFAE ; then trap at $0303
    mem[0x0300:0x0303] = bytes([0x20, 0xAE, 0xEF])
    mpu = MPU(memory=mem)
    return mpu, mem

def set_fac(mem, exp, m1, m2, m3, m4, sign):
    # FAC = $9D exp, $9E-$A1 mantissa, $A2 sign
    mem[0x9D], mem[0x9E], mem[0x9F], mem[0xA0], mem[0xA1] = exp, m1, m2, m3, m4
    mem[0xA2] = sign

def fac_from_int(n):
    """Encode a non-negative integer into FAC fields (exponent, 4 mantissa bytes)."""
    if n == 0:
        return (0, 0, 0, 0, 0)
    e = n.bit_length()
    mant = n << (32 - e) if e <= 32 else n >> (e - 32)
    return (0x80 + e, (mant >> 24) & 0xFF, (mant >> 16) & 0xFF, (mant >> 8) & 0xFF, mant & 0xFF)

def call_rnd(mpu, mem, arg):
    """arg: +1, 0, or negative integer. Returns instruction count."""
    if arg > 0:
        set_fac(mem, 0x81, 0x80, 0, 0, 0, 0x00)
    elif arg == 0:
        set_fac(mem, 0, 0, 0, 0, 0, 0)
    else:
        e, a, b, c, d = fac_from_int(-arg)
        set_fac(mem, e, a, b, c, d, 0xFF)
    mpu.pc = 0x0300
    mpu.sp = 0xFF
    n = 0
    while mpu.pc != 0x0303:
        mpu.step(); n += 1
        if n > 200000:
            raise RuntimeError('runaway at %04x' % mpu.pc)
    return n

def seed(mem):
    return bytes(mem[0xC9:0xCE])

def fac_value(mem):
    """Value of stored RNDSEED as a float (packed MBF, sign bit in m1)."""
    e = mem[0xC9]
    if e == 0:
        return 0.0
    m = ((mem[0xCA] | 0x80) << 24) | (mem[0xCB] << 16) | (mem[0xCC] << 8) | mem[0xCD]
    return m / 2**32 * 2.0 ** (e - 0x80)

if __name__ == '__main__':
    mpu, mem = make_mpu()
    mem[0xC9:0xCE] = bytes([0x80, 0x4F, 0xC7, 0x52, 0x00])
    t = time.time(); tot = 0
    for i in range(2000):
        tot += call_rnd(mpu, mem, 1)
    dt = time.time() - t
    print('2000 calls, %d instrs, %.2fs, %.0f instr/call' % (tot, dt, tot / 2000))
