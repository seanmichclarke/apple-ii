# The `$4E/$4F` keyboard-wait counter (RNDL/RNDH)

**Status: VERIFIED.** The monitor bytes match two ROM dumps for each monitor:
original monitor in AppleWin `Apple2.rom` and apple2js `intbasic.ts`; Autostart monitor
in AppleWin `Apple2_Plus.rom` and apple2js `fpbasic.ts`. The listing text is reconciled
against the 1978 *Apple II Reference Manual* ("Red Book") listing, the 1979 *Apple II
Reference Manual* listing and prose, and McFadden's `OrigF8ROM`/`AutoF8ROM` and James
Davis's II+ disassemblies. `tools/verify.py` re-checks the bytes.

Scope: Apple II (original monitor) and Apple ][+ (Autostart monitor), where `RDKEY` and
`KEYIN` are byte-identical. **The //e is different.** Its `KEYIN` at `$FD1B` begins
`A0 06 LDY #6` (McFadden `Unenh_IIe_F8ROM`) and was not analyzed here. The //e still
bumps `$4E/$4F` in its own firmware wait loops. Byte patterns `E6 4E D0 … E6 4F`/`A5 4F`
appear at `$C2D5` and `$CB15` in the unenhanced //e and at `$C27D` and `$C83B` in the
enhanced //e (AppleWin images, `deck-code-audit.md`). Their loop timing was not analyzed.

Labels: **(a)** documented, **(E)** emulated, **(b)** consensus, **(c)** inference.

---

## 1. Zero page

From the monitor listing equates (Red Book 1978: `RNDL EPZ $4E`; McFadden
`RNDL .eq $4e`, `RNDH .eq $4f`) **(a)**:

| Address | Label | Decimal (for `PEEK`) |
|---|---|---|
| `$4E` | `RNDL` | 78 |
| `$4F` | `RNDH` | 79 |
| `$38-$39` | `KSWL/KSWH` | input vector, normally → `KEYIN` |

## 2. Listing

```
; ROM: autostart
; ROM: original
;                    Apple II System Monitor, (C) 1977 Apple — S. Wozniak / A. Baum
FD0C: A4 24        RDKEY     LDY CH            ; column of cursor
FD0E: B1 28                  LDA (BASL),Y      ; char under cursor
FD10: 48                     PHA
FD11: 29 3F                  AND #$3F          ; "SET SCREEN TO FLASH"
FD13: 09 40                  ORA #$40
FD15: 91 28                  STA (BASL),Y
FD17: 68                     PLA               ; A = original char (restored by KEYIN)
FD18: 6C 38 00               JMP (KSWL)        ; "GO TO USER KEY-IN" -> normally $FD1B
FD1B: E6 4E        KEYIN     INC RNDL          ; 5 cyc  "INCR RND NUMBER"
FD1D: D0 02                  BNE KEYIN2        ; 2/3
FD1F: E6 4F                  INC RNDH          ; 5    (only when RNDL wraps)
FD21: 2C 00 C0     KEYIN2    BIT KBD           ; 4    "KEY DOWN?"  bit 7 of $C000 -> N flag
FD24: 10 F5                  BPL KEYIN         ; 2/3  no key: loop
FD26: 91 28                  STA (BASL),Y      ; "REPLACE FLASHING SCREEN"
FD28: AD 00 C0               LDA KBD           ; "GET KEYCODE"
FD2B: 2C 10 C0               BIT KBDSTRB       ; "CLR KEY STROBE"
FD2E: 60                     RTS
```

Quoted comments are from the original monitor listing: Red Book 1978, archive.org scan
leaf 89; McFadden `OrigF8ROM`. The Autostart listing has the same code with shorter
comments (`;read keyboard`). **(a)**

## 3. What it does

Apple's own description, from the *Apple II Reference Manual* (1979), p. 32,
"Random Number Seeding" (OCR, archive.org `apple-ii-ref-manual`, leaves 41–42). **(a)**

> While it waits for the user to press a key, RDKEY is continually adding 1 to a pair of
> numbers in memory. When a key is finally pressed, these two locations together
> represent a number from 0 to 65,535, the exact value of which is quite unpredictable.
> Many programs and languages use this number as the base of a random number generator.
> The two locations which are randomized during RDKEY are numbers 78 and 79 (hexadecimal
> $4E and $4F).

The same manual's `$FD1B KEYIN` entry says it "randomizes the random number seed". **(a)**

**Loop timing (c)**, from the NMOS 6502 cycle table:
* Normal iteration: `INC zp` 5 + `BNE` taken 3 + `BIT abs` 4 + `BPL` taken 3 = **15 cycles**.
* When `RNDL` wraps (1 in 256 iterations): 5 + 2 + 5 + 4 + 3 = 19 cycles.
* Mean ≈ 15.016 cycles per increment. At a nominal ≈1.02 MHz that is **≈68,000
  increments per second**, so the 16-bit counter wraps about **once per second**.
  (Clock rate is the commonly cited figure, not measured here.)

**Properties that follow from the code (a):**
1. The counter only advances **while `KEYIN` is waiting** for a key. It is frozen while
   a program runs, so it measures *how long a human waited before a keypress* (mod 65,536).
2. It covers every keypress that goes through `RDKEY` → `KSW` → `KEYIN`. In the
   emulation, Applesoft line entry at `]` and `GET` both reached `$FD1B` **(E)**.
   `INPUT` uses the same `GETLN`/`RDKEY` path (per the manual's `GETLN` description),
   but it was not separately exercised.
3. It holds at most **65,536** distinct values. Once a program uses it as a seed, the
   whole "random" future is one of ≤65,536 fixed sequences.
4. Nothing else in the monitor writes it. The counter is **not initialized** at reset.
   After an emulated boot with zeroed RAM it read `$0002` at the Integer BASIC prompt
   (Integer BASIC entered from the monitor with Ctrl-B, then RETURN) **(E)**. On real
   hardware its starting value is whatever RAM held.
5. With a slot-6 DOS hooked into `KSW`, input still reaches `KEYIN`
   through DOS's input handler. **(c) — not emulated.**

## 4. Who consumes it

| Consumer | Reads `$4E/$4F`? | Evidence |
|---|---|---|
| **Integer BASIC `RND`** ($EF4E) | **Yes.** It *is* the generator state (see `integer-basic-rnd.md`) | `EF51: A5 4E LDA RNDL`, `EF56: A5 4F LDA RNDH` **(a)**. Same program gave different output under different key timing **(E)** |
| **Applesoft `RND`** ($EFAE) | **No** | No reference in the Applesoft cross-reference. Identical `RND(1)` output with counter `$0041` vs `$3E97` **(a)+(E)** |
| Programs | only if they `PEEK(78)`/`PEEK(79)` | e.g. `X = RND(-(PEEK(78) + 256*PEEK(79)))`, `demos.md` Demo 4 |

For the thesis, the "entropy source" is **human reaction time folded into 16 bits**, and
only Integer BASIC uses it automatically. In Applesoft it exists only as a programming
idiom. How widespread that idiom was is **not** established by sources gathered here.
Treat it as (b) at best until the research agent cites it.

## 5. Weaknesses a presenter can state safely

* 16 bits, so ≤65,536 seeds. **(a)**
* Adjacent counter values are unrelated after Applesoft's reseed. Seeds 4792 and 4793
  gave first `RND(1)` values .69903216 and .521940801 **(E)**. The weakness is the size
  of the seed space, not smoothness between neighbouring seeds.
* `S = 0` makes `RND(-S)` into `RND(0)`: no reseed, just the last value. **(a)**
* Every seed tested fell into one of two short Applesoft cycles, of 37,758 and 32,366
  states (`applesoft-rnd.md` §5.2). So even the 65,536 seeds do not buy 65,536
  independent long streams. **(E)** for the seeds tested.
* A program that auto-runs from a boot disk with no keypress sees an uninitialized or
  boot-time-determined counter. **(c)**
