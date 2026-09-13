# Verification log: headline numbers re-run on 12 Sep 2026

These are independent re-runs of the numbers the decks depend on, made while building this package. They don't reuse the research agents' results.

**Setup**
- py65 NMOS 6502 emulator.
- Genuine Applesoft `RND` at `$EFAE`, called through `tools/rnd_emu.py`.
- ROM image `Apple2_Plus.rom` from AppleWin, SHA-1 `33a24f5489ba9195b44be77d9afb2252594cb5c7`. The image isn't redistributed here; get it from the AppleWin repository's `resource/` directory.

**Commands**
```
python3 -m venv v && v/bin/pip install py65
ROM=/path/to/Apple2_Plus.rom v/bin/python tools/verify_headline.py
v/bin/python tools/intbasic_rnd_emu.py
```

**Output (verbatim)**
```
rom sha1 33a24f5489ba9195b44be77d9afb2252594cb5c7
$F123 seed table: 80 4F C7 52 58
$F150 copy loop : A2 1C BD 0A F1 95 B0 86 F1 CA D0 F6
$EFA6 constants : 98 35 44 7A 68 28 B1 46
$F5CB..$F601    : A5 26 0A A5 27 29 03 2A 05 26 0A 0A 0A 85 E2 A5 27 4A 4A 29 07 05 E2 85 E2 A5 E5 0A 65 E5 0A AA CA A5 30 29 7F E8 4A D0 FC 85 E1 8A 18 65 E5 90 02 E6 E1 85 E0 60 86
$F600 byte      : 60 (60 = RTS)
JSR/JMP $F5CB refs in D000-FFFF: []
branch opcodes targeting $F600 (candidates): ['0xf59c']
first RND(1) $CD=FF -> 0.973136996
first RND(1) $CD=FE -> 0.973136996
first RND(1) $CD=00 -> 0.270011996
first RND(1) $CD=58 -> 0.512199496
first RND(1) $CD=AA -> 0.738761996
distinct first outputs over 256 $CD values: 181
RND(-1) seed value 2.99196472e-08
$CD=58 preperiod 15382 period 202 (10s)
feedback == b14 xor b13: True
start (0, 0) first out 0x100 cycle length 32767 after 0
start (1, 0) first out 0x1 cycle length 32767 after 0
start (52, 18) first out 0x1234 cycle length 32767 after 0
start (255, 255) first out 0x7fff cycle length 32767 after 0
increments/sec at 15 cycles/loop: 68032.26666666666  seconds per 16-bit wrap: 0.9633076069786494
```

**Notes**
- The HFIND bytes end at `$F5FF` with `85 E0`. `$F600` is `60` (RTS), and `$F601` begins DRAW.
- The one branch that lands on `$F600` is at `$F59C`, inside HLIN. So the safe patch space is `$F5CB–$F5FF`, which is 53 bytes. DESIGN_INTENT.md quoted 54 bytes; that figure counts the shared RTS and is superseded by this check.
- The scan found no absolute `JSR` or `JMP` to `$F5CB` in `$D000–$FFFF`. Indirect calls, and calls from software outside ROM, can't be ruled out this way.
- Not re-run here: the full 256-value loop sweep (`tools/cd_sweep_results.jsonl`), the add-removal experiment, and the Ctrl-RESET behavior. Those numbers come from the research agents' logged runs.
