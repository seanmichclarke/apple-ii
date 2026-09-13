import sys, json, time
import os
ROMP=os.environ.get('ROM','Apple2_Plus.rom')  # AppleWin resource/Apple2_Plus.rom
sys.argv=['x',ROMP]
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import rnd_emu as E
rom=open(ROMP,'rb').read()
import hashlib; print('rom sha1', hashlib.sha1(rom).hexdigest())
b=lambda a,n: ' '.join('%02X'%x for x in rom[a-0xD000:a-0xD000+n])
print('$F123 seed table:', b(0xF123,5))
print('$F150 copy loop :', b(0xF150,12))
print('$EFA6 constants :', b(0xEFA6,8))
print('$F5CB..$F601    :', b(0xF5CB,0x37))
print('$F600 byte      :', b(0xF600,1), '(60 = RTS)')
# references to $F5CB and branches landing on $F600
refs=[hex(0xD000+i) for i in range(len(rom)-2) if rom[i] in (0x20,0x4C) and rom[i+1]==0xCB and rom[i+2]==0xF5]
print('JSR/JMP $F5CB refs in D000-FFFF:', refs)
br=[]
for i in range(len(rom)-1):
    if rom[i] in (0x10,0x30,0x50,0x70,0x90,0xB0,0xD0,0xF0):
        off=rom[i+1]; off=off-256 if off>127 else off
        if 0xD000+i+2+off==0xF600: br.append(hex(0xD000+i))
print('branch opcodes targeting $F600 (candidates):', br)
# first values
for cd in (0xFF,0xFE,0x00,0x58,0xAA):
    mpu,mem=E.make_mpu(); mem[0xC9:0xCE]=bytes([0x80,0x4F,0xC7,0x52,cd])
    E.call_rnd(mpu,mem,1); print('first RND(1) $CD=%02X -> %.9f'%(cd,E.fac_value(mem)))
distinct=set()
for cd in range(256):
    mpu,mem=E.make_mpu(); mem[0xC9:0xCE]=bytes([0x80,0x4F,0xC7,0x52,cd]); E.call_rnd(mpu,mem,1); distinct.add(round(E.fac_value(mem),9))
print('distinct first outputs over 256 $CD values:', len(distinct))
mpu,mem=E.make_mpu(); E.call_rnd(mpu,mem,-1); print('RND(-1) seed value %.9g'%E.fac_value(mem))
# cycle for $58
t=time.time()
for cd in (0x58,):
    mpu,mem=E.make_mpu(); mem[0xC9:0xCE]=bytes([0x80,0x4F,0xC7,0x52,cd])
    seen={E.seed(mem):0}
    for i in range(1,40000):
        E.call_rnd(mpu,mem,1); s=E.seed(mem)
        if s in seen: print('$CD=%02X preperiod %d period %d (%.0fs)'%(cd,seen[s],i-seen[s],time.time()-t)); break
        seen[s]=i
