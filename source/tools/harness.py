"""Run real Apple II ROM code under the py65 NMOS 6502 emulator.

- RAM below $C000 is writable; writes to I/O and ROM are ignored.
- KEYIN ($FD1B) is trapped: it adds a configurable wait count to $4E/$4F (as the real
  wait loop would), restores the character under the cursor, and returns the next
  queued keystroke.
- COUT1 ($FDF0) entry is logged as screen output, then the ROM code runs normally.

ROM images are read from $A2ROMDIR (see verify.py for download URLs).
"""
import os
from py65.devices.mpu6502 import MPU

ROMDIR = os.environ.get('A2ROMDIR', '/tmp/a2rng-roms')


class Mem(list):
    def __setitem__(self, a, v):
        if isinstance(a, slice):
            return list.__setitem__(self, a, v)
        if a < 0xC000:
            list.__setitem__(self, a, v)


class Apple:
    def __init__(self, rom='Apple2_Plus.rom', ram_fill=None, wait=lambda: 1):
        self.mem = Mem([0] * 0x10000)
        data = open(os.path.join(ROMDIR, rom), 'rb').read()
        list.__setitem__(self.mem, slice(0xD000, 0x10000), list(data))
        if ram_fill is not None:
            for a in range(0xC000):
                list.__setitem__(self.mem, a, ram_fill(a))
        self.mpu = MPU(memory=self.mem)
        self.mpu.pc = self.mem[0xFFFC] | self.mem[0xFFFD] << 8
        self.mpu.sp = 0xFF
        self.out = []
        self.wait = wait
        self.steps = 0

    def _rts(self):
        m = self.mpu
        m.sp = (m.sp + 1) & 0xFF
        lo = self.mem[0x100 + m.sp]
        m.sp = (m.sp + 1) & 0xFF
        hi = self.mem[0x100 + m.sp]
        m.pc = ((hi << 8) | lo) + 1

    def run(self, keys, max_steps=200_000_000, hooks=None):
        q = list(keys)
        m, mem = self.mpu, self.mem
        while self.steps < max_steps:
            pc = m.pc
            if hooks and pc in hooks:
                hooks[pc](self)
            if pc == 0xFD1B:  # KEYIN
                if not q:
                    return 'input-exhausted'
                ch = q.pop(0)
                c = (mem[0x4E] | mem[0x4F] << 8) + self.wait()
                mem[0x4E], mem[0x4F] = c & 0xFF, (c >> 8) & 0xFF
                basl = mem[0x28] | mem[0x29] << 8
                mem[(basl + m.y) & 0xFFFF] = m.a
                m.a = ord(ch) | 0x80
                m.p = (m.p & ~0x82) | 0x80
                self._rts()
                continue
            if pc == 0xFDF0:  # COUT1
                self.out.append(chr(m.a & 0x7F))
            m.step()
            self.steps += 1
        return 'step-limit'

    def call(self, addr, max_steps=5_000_000):
        """JSR to addr with a sentinel return address; returns instructions executed."""
        m, mem = self.mpu, self.mem
        sentinel = 0x02F0
        ret = sentinel - 1
        mem[0x100 + m.sp] = (ret >> 8) & 0xFF; m.sp = (m.sp - 1) & 0xFF
        mem[0x100 + m.sp] = ret & 0xFF; m.sp = (m.sp - 1) & 0xFF
        m.pc = addr
        n = 0
        while m.pc != sentinel:
            m.step(); n += 1
            if n > max_steps:
                raise RuntimeError('call did not return')
        return n


def boot_applesoft(cd=0x00, wait=lambda: 1):
    """Power on an Apple ][+ with zeroed RAM except $CD, run to the ] prompt."""
    a = Apple('Apple2_Plus.rom', wait=wait)
    a.mem[0xCD] = cd
    assert a.run('') == 'input-exhausted'
    return a


def boot_integer(wait=lambda: 1):
    """Power on an Apple II (original monitor), Ctrl-B RETURN into Integer BASIC."""
    a = Apple('Apple2.rom', wait=wait)
    a.run('\x02\r')
    return a


def set_fac_int(mem, k):
    """Unpacked FAC = integer k (nonzero)."""
    s = 0xFF if k < 0 else 0x00
    k = abs(k)
    bl = k.bit_length()
    mant = k << (32 - bl)
    mem[0x9D] = 0x80 + bl
    mem[0x9E], mem[0x9F], mem[0xA0], mem[0xA1] = (mant >> 24) & 255, (mant >> 16) & 255, (mant >> 8) & 255, mant & 255
    mem[0xA2] = s
    mem[0xAC] = 0


def rnd_call(a, k=1):
    """Call Applesoft RND ($EFAE) with FAC = k; returns (instructions, cycles)."""
    set_fac_int(a.mem, k) if k else a.mem.__setitem__(0x9D, 0)
    c0 = a.mpu.processorCycles
    n = a.call(0xEFAE)
    return n, a.mpu.processorCycles - c0


def seed(a):
    return bytes(a.mem[0xC9:0xCE])
