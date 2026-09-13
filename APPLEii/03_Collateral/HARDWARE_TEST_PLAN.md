# Hardware test plan: run before VCF Midwest 21

The emulator results in this folder come from running the **real ROM code**. They can't tell you what *your* machines do at power-on, or what the patch does. Those answers need real hardware. Fill in the matrix at the end and bring it as a backup slide.

Decimal addresses used below:
- `$C9–$CD` seed = **201–205**
- `$4E/$4F` counter = **78/79**
- `$EFAE` RND entry = **61358**
- `$F5CB` HFIND = **62923**

---

## T1. What does the demo machine print, and why?
Power **off**, wait 10 s, power **on**. Get to the `]` prompt without running anything else, then type:

```
]PRINT PEEK(201);" ";PEEK(202);" ";PEEK(203);" ";PEEK(204);" ";PEEK(205)
]PRINT RND(1)
```

Expected: the first four values are `128 79 199 82`, the ROM seed. **`PEEK(205)` is the uncopied byte.** Emulated first values for different contents of that byte:

| PEEK(205) | First RND(1) |
|---|---|
| 255 or 254 | .973136996 |
| 0 | .270011996 |
| 88 | .512199496 |
| 170 | .738761996 |

Repeat three power cycles. **Pass:** the same number every time. Record `PEEK(205)`.

Repeat each boot path: no disk (Ctrl-RESET to BASIC), DOS 3.3 System Master, ProDOS/BASIC.SYSTEM. Any of them might write to 205 before you type.

## T2. Why the demo must not use Ctrl-RESET or PR#6
After T1, run `PRINT RND(1)` a few times, then Ctrl-RESET, then `PRINT RND(1)`. Then try `PR#6` and `PRINT RND(1)`.
**Expected:** a different number each time. Emulation shows Ctrl-RESET preserves the seed. Aldridge (1987) says reboots don't repeat.

## T3. Is the patch installed?
With the language card in read mode, `PEEK(61358)` reads RND's first byte:

```
]PRINT PEEK(61358)
```
`32` means stock (`JSR SIGN`). `76` means patched (`JMP $F5CB`). Use this after every step below.

## T4. Tight loop, no keypress (patched)
```
10 FOR I = 1 TO 52 : PRINT RND(1) : NEXT
```
**Pass:** no run of identical or near-identical values. **Fail** means the patch reseeds from a counter that isn't moving.

## T5. The documented RND(−n) contract (stock and patched)
```
10 X = RND(-1)
20 FOR I = 1 TO 5 : PRINT RND(1) : NEXT
30 PRINT "PRESS A KEY" : GET A$
40 X = RND(-1)
50 FOR I = 1 TO 5 : PRINT RND(1) : NEXT
```
**Pass:** lines 20 and 50 print the same five numbers. Emulated stock values after `RND(-1)` start `.738207502 .272707136 .299733446`.
Then add `GET A$` *between* calls inside the loop. Record whether the sequence still repeats. The manual promises it does.

## T6. RND(0) returns the last value (stock and patched)
```
10 A = RND(1) : B = RND(0) : PRINT A, B, A = B
```
**Pass:** prints `1` for `A = B`.

## T7. Turnkey program (patched)
Save as HELLO on a DOS 3.3 disk that also installs the patch:
```
10 PRINT RND(1)
```
Power-cycle twice. **Record** whether the numbers differ. With no keypress before RND, the counter may hold the same leftover value.

## T8. Hi-res regression over HFIND (patched)
```
10 HGR : HCOLOR = 3
20 HPLOT 0,0 TO 279,159 TO 0,159 TO 279,0
30 PRINT "LINES OK"
```
Then load and `DRAW`/`XDRAW` a known shape table, and change `SCALE` and `ROT`. **Pass:** lines and shapes draw correctly with no hang. `$F600` is the RTS that HLIN branches to, so a patch that spills past `$F5FF` breaks line 20.

## T9. Language-card conflicts (patched)
| Step | Check |
|---|---|
| DOS 3.3 with Integer BASIC loaded into the card, then install | Does `INT` or `FP` remove the patch? (T3 after each) |
| ProDOS / BASIC.SYSTEM, then install | **Expect danger:** ProDOS lives in the language card. Does the loader refuse? |
| Original Apple II (Integer BASIC in ROM) | The loader must refuse: `$EFAE` is inside Integer BASIC there |
| IIe and IIc: Ctrl-RESET after install | T3: is it still `76`? |
| //e with /RAM, or a mouse card / IIc serial IRQ active | Any hang? |

---

## Results matrix (fill in)

| Machine / ROM | Boot path | T1 PEEK(205) | T1 repeats? | T4 | T5 | T6 | T7 | T8 | Ctrl-RESET keeps patch? | Tested on |
|---|---|---|---|---|---|---|---|---|---|---|
| ][+ | no DOS | | | | | | | | | real / emulator (name) / untested |
| ][+ + 16K card | DOS 3.3 | | | | | | | | | |
| //e | DOS 3.3 | | | | | | | | | |
| //e enhanced | ProDOS | | | | | | | | | |
| //c (ROM rev ___) | ProDOS | | | | | | | | | |
| IIgs (ROM ___) | ProDOS 8 | | | | | | | | | |

Mark every cell as **real hardware**, **emulator (name it)**, or **untested**. The audience will ask which.
