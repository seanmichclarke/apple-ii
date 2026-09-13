#!/usr/bin/env python3
"""Re-verify the source/ deliverables against real ROM images.

1. Every listing line "XXXX: bb bb bb  ..." inside a code block that carries a
   "; ROM: <set>" marker is compared byte-for-byte with two independent ROM dumps.
2. Every demo program in demos.md is typed into the emulated machine and its
   output is diffed against the expected-output block(s).

Usage:  pip install py65 && python3 verify.py
ROM images are downloaded to $A2ROMDIR (default /tmp/a2rng-roms).
"""
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
ROMDIR = os.environ.setdefault('A2ROMDIR', '/tmp/a2rng-roms')
URLS = {
    'Apple2_Plus.rom': 'https://raw.githubusercontent.com/AppleWin/AppleWin/master/resource/Apple2_Plus.rom',
    'Apple2.rom': 'https://raw.githubusercontent.com/AppleWin/AppleWin/master/resource/Apple2.rom',
    'fpbasic.ts': 'https://raw.githubusercontent.com/whscullin/apple2js/main/js/roms/system/fpbasic.ts',
    'intbasic.ts': 'https://raw.githubusercontent.com/whscullin/apple2js/main/js/roms/system/intbasic.ts',
}
ROMSETS = {
    'applesoft': ['Apple2_Plus.rom', 'fpbasic.ts'],
    'autostart': ['Apple2_Plus.rom', 'fpbasic.ts'],
    'original': ['Apple2.rom'],
    'integer': ['Apple2.rom', 'intbasic.ts'],
}
EXTRA = [  # (romset, address, bytes) facts cited in prose rather than in a listing block
    ('applesoft', 0xD092, 'AE EF'),      # statement/function address table entry for RND
    ('applesoft', 0xD226, '52 4E C4'),   # "RND" keyword text, last char high-bit
    ('applesoft', 0xF10B, 'E6 B8 D0 02 E6 B9 AD 60 EA C9 3A B0 0A C9 20 F0 EF 38 E9 30 38 E9 D0 60 80 4F C7 52 58'),
    ('applesoft', 0xFFFC, '62 FA'),      # Autostart RESET vector
    ('original', 0xFFFC, '59 FF'),       # original monitor RESET vector
]
LINE = re.compile(r'^([0-9A-F]{4}):((?: [0-9A-F]{2})+)(?:\s{2,}|$)')


def fetch():
    os.makedirs(ROMDIR, exist_ok=True)
    for name, url in URLS.items():
        path = os.path.join(ROMDIR, name)
        if not os.path.exists(path):
            urllib.request.urlretrieve(url, path)


def load_images():
    imgs = {}
    for name in ('Apple2_Plus.rom', 'Apple2.rom'):
        imgs[name] = (open(os.path.join(ROMDIR, name), 'rb').read(), 0xD000)
    for name in ('fpbasic.ts', 'intbasic.ts'):
        t = open(os.path.join(ROMDIR, name)).read()
        i = t.find('new Uint8Array(['); j = t.find(']', i)
        b = bytes(int(x, 16) for x in re.findall(r'0x([0-9a-fA-F]{2})\b', t[i:j]))
        imgs[name] = (b, 0x10000 - len(b))
    return imgs


def compare(imgs, roms, addr, bs, where):
    fails = 0
    for r in roms:
        img, base = imgs[r]
        got = img[addr - base:addr - base + len(bs)]
        if got != bs:
            fails += 1
            print(f'  MISMATCH {where} ${addr:04X}: listed {bs.hex(" ").upper()}, {r} has {got.hex(" ").upper()}')
    return fails


def check_listings(imgs):
    checks = fails = 0
    for md in ('applesoft-rnd.md', 'keyboard-seed.md', 'integer-basic-rnd.md'):
        inblock, roms = False, []
        for ln, line in enumerate(open(os.path.join(SRC, md)), 1):
            if line.startswith('```'):
                inblock, roms = not inblock, []
                continue
            if not inblock:
                continue
            m = re.match(r';\s*ROM:\s*(\w+)', line)
            if m:
                roms += ROMSETS[m.group(1)]
                continue
            m = LINE.match(line)
            if not m:
                continue
            if not roms:
                print(f'  {md}:{ln}: listing line in a block with no ROM marker'); fails += 1
                continue
            bs = bytes(int(x, 16) for x in m.group(2).split())
            checks += len(roms)
            fails += compare(imgs, roms, int(m.group(1), 16), bs, f'{md}:{ln}')
    for rs, addr, hexs in EXTRA:
        checks += len(ROMSETS[rs])
        fails += compare(imgs, ROMSETS[rs], addr, bytes.fromhex(hexs), 'EXTRA')
    return checks, fails


def sections(text):
    secs, cur = {}, None
    for line in text.split('\n'):
        m = re.match(r'^#{2,3} (Demo \w+|Integer BASIC contrast)', line)
        if m:
            cur = m.group(1); secs[cur] = []
            continue
        if cur:
            secs[cur].append(line)
    out = {}
    for k, lines in secs.items():
        blocks, i = [], 0
        while i < len(lines):
            m = re.match(r'^```(\w+)', lines[i])
            if m:
                j = i + 1; body = []
                while not lines[j].startswith('```'):
                    body.append(lines[j]); j += 1
                blocks.append((m.group(1), body)); i = j + 1
            else:
                i += 1
        if blocks:
            out[k] = blocks
    return out


def screen_lines(s, prompt):
    res = []
    for line in s.replace('\r', '\n').split('\n'):
        line = line.replace('\x07', '').rstrip()
        if line and not line.startswith(prompt):
            res.append(line)
    return res


def run_program(rom, prog, runs, final_wait=None):
    from harness import boot_applesoft, boot_integer
    a = boot_applesoft() if rom == 'applesoft' else boot_integer()
    prompt = ']' if rom == 'applesoft' else '>'
    a.run(''.join(l + '\r' for l in prog))
    got = []
    for _ in range(runs):
        n = len(a.out)
        if final_wait is None:
            a.run('RUN\r')
        else:
            cnt = [0]
            def w():
                cnt[0] += 1
                return final_wait if cnt[0] == 5 else 1  # R,U,N,CR then the GET key
            a.wait = w
            a.run('RUN\rX')
        lines = screen_lines(''.join(a.out[n:]), prompt)
        assert lines and lines[0] == 'RUN', lines[:3]
        got += lines[1:]
    return got


def check_demos():
    sys.path.insert(0, HERE)
    secs = sections(open(os.path.join(SRC, 'demos.md')).read())
    specs = {'Demo 1A': {}, 'Demo 1B': {}, 'Demo 2': {}, 'Demo 3': {},
             'Demo 4': {'waits': [4660, 4661, 30000]},
             'Integer BASIC contrast': {'rom': 'integer'}}
    fails = 0
    for name, spec in specs.items():
        blocks = secs[name]
        basic = [b for k, b in blocks if k == 'basic'][0]
        texts = [b for k, b in blocks if k == 'text']
        prog = [l for l in basic if l.strip() and l.strip() != 'RUN']
        runs = sum(1 for l in basic if l.strip() == 'RUN')
        rom = spec.get('rom', 'applesoft')
        cases = [(w, texts[i]) for i, w in enumerate(spec['waits'])] if 'waits' in spec else [(None, texts[0])]
        for w, expected in cases:
            got = run_program(rom, prog, runs, w)
            exp = [l.rstrip() for l in expected if l.strip()]
            ok = got == exp
            fails += not ok
            print(f'  {name}{"" if w is None else f" (key wait {w})"}: {"OK" if ok else "DIFFERS"}')
            if not ok:
                print('    expected:', exp)
                print('    got:     ', got)
    return fails


if __name__ == '__main__':
    fetch()
    imgs = load_images()
    print('Listings:')
    checks, lf = check_listings(imgs)
    print(f'  {checks} line/ROM comparisons, {lf} mismatches')
    print('Demos:')
    df = check_demos()
    sys.exit(1 if lf or df else 0)
