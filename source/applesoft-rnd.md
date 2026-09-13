# AppleSoft II `RND` — annotated 6502 listing

**Status: VERIFIED.** Every byte below matches two independently hosted ROM dumps
(AppleWin `Apple2_Plus.rom` and apple2js `fpbasic.ts`). Mnemonics, labels and operands
are reconciled against S-C DocuMentor (Bob Sander-Cederlof), the McFadden SourceGen
listing and the James Davis II+ listing. Logic and constants are also reconciled against
Microsoft's released 1978 source (`m6502.asm`). Behavioral claims come from executing
these exact ROM bytes in a 6502 emulator. See `PROVENANCE.md` for details and for how
independent those sources really are. `tools/verify.py` re-checks every listing line in
this file against both ROM dumps.

Applies to: Applesoft II in the Apple ][+ ROM. The same bytes sit at the same addresses
in the Apple //e and enhanced //e ROM images (apple2js). The //c was not checked.

Evidence labels used below:
**(a)** documented fact: ROM bytes, published listing, or published manual.
**(E)** measured by running the actual ROM code in emulation (documented, reproducible).
**(b)** community consensus. **(c)** inference.

---

## 1. Floating-point representation

Labels from S-C DocuMentor `definitions.html` (McFadden's names in brackets):

| Address | S-C label | Contents |
|---|---|---|
| `$9D` | `FAC` | exponent, excess-`$80`; `$00` means the value is 0 |
| `$9E-$A1` | `FAC+1..FAC+4` | 32-bit mantissa, MSB first, **top bit explicit** (normalized = 1) |
| `$A2` | `FAC.SIGN` [`FAC_SIGN`] | sign in bit 7 |
| `$AC` | `FAC.EXTENSION` [`FAC_EXTENSION`] | guard byte below the mantissa, used for rounding |
| `$A5-$A9`, `$AA` | `ARG`, `ARG.SIGN` | second accumulator, same layout |
| `$92` | `ARG.EXTENSION` | |
| `$C9-$CD` | `RNDSEED` | the 5-byte **packed** seed |

**Packed (5-byte) form**, used for variables, ROM constants and `RNDSEED`:

```
byte 0      exponent  e   (value = 0 if e = $00)
byte 1      sign bit (bit 7) + mantissa bits 30..24   (the implicit leading 1 is replaced by the sign)
byte 2..4   mantissa bits 23..0
value = (-1)^sign × 0.1mmmm…(binary) × 2^(e − $80)
```

`LOAD_FAC_FROM_YA` ($EAF9) unpacks by copying byte 1 to `FAC.SIGN` and then `ORA #$80`
into `FAC+1`. `STORE_FAC_AT_YX_ROUNDED` ($EB2B) rounds, then repacks with
`(FAC.SIGN OR $7F) AND FAC+1`. Both listings are in §6. **(a)**

---

## 2. The constants (and the missing fifth byte)

```
; ROM: applesoft
EFA6: 98 35 44 7A  CON.RND.1   .HS 9835447A   ; S-C: "<<< THESE ARE MISSING ONE BYTE >>>"
EFAA: 68 28 B1 46  CON.RND.2   .HS 6828B146   ; S-C: "<<< FOR FP VALUES >>>"
EFAE: 20 82 EB     RND         JSR SIGN       ; (first byte of RND — see below)
```

Each constant is 4 bytes, but the FP loader always reads **5**. Microsoft's code dates
from 4-byte-float BASIC and was never widened for the 9-digit `ADDPRC` build. **(a)**
So the loaders pick up the next byte in ROM:

| Constant as actually read | Bytes read | Exact value | Decimal |
|---|---|---|---|
| multiplier (`FMULT` reads $EFA6–$EFAA) | `98 35 44 7A 68` | 380145485/32 | **11879546.40625** |
| addend (`FADD` reads $EFAA–$EFAE) | `68 28 B1 46 20` | 88443441/2^51 | **3.92767778×10⁻⁸** |
| multiplier as a 4-byte constant (intent) | `98 35 44 7A` | 11879546 | 11879546 |
| addend as a 4-byte constant (intent) | `68 28 B1 46` | 5527715/2^47 | 3.92767774×10⁻⁸ |

The multiplier's stray fifth byte `$68` is the first byte of `CON.RND.2`. The addend's
stray fifth byte `$20` is the `JSR` opcode at the start of `RND`. The values are computed
exactly from the bytes with rational arithmetic. **(a)**

Microsoft source (`m6502.asm`, lines 6344–6351) has the same four bytes each. The
math package is assembled in **octal** (`RADIX 8`, line 4847), so
`230 065 104 172` = `$98 $35 $44 $7A` and `150 050 261 106` = `$68 $28 $B1 $46`. **(a)**

---

## 3. The routine

Cycle counts are the standard NMOS 6502 figures for each instruction alone (branches:
not taken / taken, no page crossings occur here). Subroutine bodies are not included;
§5 has measured whole-call costs.

```
; ROM: applesoft
;                            ---- S-C DocuMentor S.EE8D, lines 2830-3110 ----
EFA5: 60           RTS.19    RTS                    ; 6   (shared exit, end of POLYNOMIAL)
EFAE: 20 82 EB     RND       JSR SIGN               ; 6   A = $FF / $00 / $01 for FAC <0 / =0 / >0
EFB1: AA                     TAX                    ; 2   keep the sign in X
EFB2: 30 18                  BMI .1  ($EFCC)        ; 2/3 negative: scramble the ARGUMENT itself
EFB4: A9 C9                  LDA #RNDSEED           ; 2
EFB6: A0 00                  LDY /RNDSEED           ; 2
EFB8: 20 F9 EA               JSR LOAD.FAC.FROM.YA   ; 6   FAC = current seed
EFBB: 8A                     TXA                    ; 2
EFBC: F0 E7                  BEQ RTS.19  ($EFA5)    ; 2/3 RND(0): return the seed unchanged
EFBE: A9 A6                  LDA #CON.RND.1         ; 2   S-C: "VERY POOR RND ALGORITHM"
EFC0: A0 EF                  LDY /CON.RND.1         ; 2
EFC2: 20 7F E9               JSR FMULT              ; 6   FAC = seed × 11879546.40625
EFC5: A9 AA                  LDA #CON.RND.2         ; 2   S-C: "ALSO, CONSTANTS ARE TRUNCATED"
EFC7: A0 EF                  LDY /CON.RND.2         ; 2   S-C: "THIS DOES NOTHING, DUE TO SMALL EXPONENT" (see §5.4)
EFC9: 20 BE E7               JSR FADD               ; 6   FAC = FAC + 3.93e-8
EFCC: A6 A1        .1        LDX FAC+4              ; 3   swap lowest and highest mantissa bytes
EFCE: A5 9E                  LDA FAC+1              ; 3   S-C: "TO SUPPOSEDLY MAKE IT MORE RANDOM"
EFD0: 85 A1                  STA FAC+4              ; 3
EFD2: 86 9E                  STX FAC+1              ; 3
EFD4: A9 00                  LDA #0                 ; 2
EFD6: 85 A2                  STA FAC.SIGN           ; 3   force positive
EFD8: A5 9D                  LDA FAC                ; 3   old exponent...
EFDA: 85 AC                  STA FAC.EXTENSION      ; 3   ...becomes the guard byte
EFDC: A9 80                  LDA #$80               ; 2
EFDE: 85 9D                  STA FAC                ; 3   exponent $80 => 0.5 <= |mantissa| < 1 before normalizing
EFE0: 20 2E E8               JSR NORMALIZE.FAC.2    ; 6   shift out leading zeros (value < 1)
EFE3: A2 C9                  LDX #RNDSEED           ; 2
EFE5: A0 00                  LDY /RNDSEED           ; 2
EFE7: 4C 2B EB     GO.MOVMF  JMP STORE.FAC.AT.YX.ROUNDED ; 3  round, write $C9-$CD, RTS with FAC = result
```

The routine's own instructions cost 85 cycles on the `RND(1)` path. The token table
dispatches `RND` to `$EFAE`: the address-table entry at `$D092` is `AE EF`, and the
keyword text sits at `$D226`. **(a)**

Microsoft's own description of the routine (`m6502.asm` lines 6329–6340, verbatim):

```
	;PSUEDO-RANDOM NUMBER GENERATOR.
	;IF ARG=0, THE LAST RANDOM NUMBER GENERATED IS RETURNED.
	;IF ARG .LT. 0, A NEW SEQUENCE OF RANDOM NUMBERS IS
	;STARTED USING THE ARGUMENT.
	;   TO FORM THE NEXT RANDOM NUMBER IN THE SEQUENCE,
	;MULTIPLY THE PREVIOUS RANDOM NUMBER BY A RANDOM CONSTANT
	;AND ADD IN ANOTHER RANDOM CONSTANT. THE THEN HO
	;AND LO BYTES ARE SWITCHED, THE EXPONENT IS PUT WHERE
	;IT WILL BE SHIFTED IN BY NORMAL, AND THE EXPONENT IN THE FAC
	;IS SET TO 200 SO THE RESULT WILL BE LESS THAN 1. THIS
	;IS THEN NORMALIZED AND SAVED FOR THE NEXT TIME.
	;THE HO AND LOW BYTES WERE SWITCHED SO THERE WILL BE A
	;RANDOM CHANCE OF GETTING A NUMBER LESS THAN OR GREATER
	;THAN .5 .
```

(`200` is octal, i.e. `$80`.) The Apple build (`REALIO=4`) assembles the path shown
above. For the Commodore PET (`REALIO=3`), the *same source* makes `RND(0)` load VIA
timer bytes (`CQHTIM`, lines 6357–6370) into the FAC. That is a hardware entropy path
Microsoft already had, and the Apple build does not get it. **(a)**

---

## 4. Plain-English walkthrough

**Argument handling.** `SIGN` looks only at the exponent and the sign byte, so
`RND(0.001)`, `RND(1)` and `RND(99)` are identical calls. **(a)**

**`RND(X>0)`: advance the generator.**
1. Load the 5-byte seed at `$C9` into the FAC.
2. Multiply by 11879546.40625. For a seed in [0.5, 1) the product is about 2²³, so the
   FAC exponent comes out around `$97`/`$98`.
3. Add 3.93×10⁻⁸. This is 2⁵⁰ times smaller than the product, and it almost never
   changes a bit (§5.4).
4. Swap `FAC+1` (most significant mantissa byte) with `FAC+4` (least significant).
5. Clear the sign. Put the old exponent in the guard byte. Set the exponent to `$80`.
6. Normalize: shift left until the mantissa's top bit is 1, decrementing the exponent
   once per shift. The result is in (0, 1).
7. Round using the guard byte, store it as the new seed, and return the same value.

This is **not a textbook LCG** `x ← (a·x + c) mod m`. There is no modulus. Steps 4–6
replace the "mod" with a byte transposition and a renormalization, and the additive
term is effectively absent. **(a)** from the code. Consequence: LCG lattice/spectral
results do not transfer to this generator automatically. Anyone who wants a spectral
figure has to compute it on this map. **(c)**

**`RND(0)`: re-read.** `LOAD.FAC.FROM.YA` puts the seed in the FAC, then `BEQ RTS.19`
returns before any arithmetic. You get the last value again and the seed is untouched.
**(a)**

**`RND(X<0)`: reseed from X.** `BMI` jumps straight to step 4. The *argument's own*
bytes are shuffled, made positive, normalized, and stored as the seed. The same X always
gives the same seed. **(a)** For small integers the low mantissa byte of X is zero, so
the swap puts a zero byte on top and normalization shifts by at least 8 bits. That is
why `RND(-1)` returns **2.99196472E-08** and not a number near 0.5. Worked through:
−1 unpacks to exponent `$81`, mantissa `80 00 00 00`. After the swap the mantissa is
`00 00 00 80` with guard `$81`. Normalization gives `80 81 00 00` with exponent `$68`,
so the value is 0x80810000/2³² × 2⁻²⁴ ≈ 2.992×10⁻⁸. **(a)**, and confirmed **(E)**.

`RND(-0)` is `RND(0)`: the FAC exponent is 0, `SIGN` returns 0, and nothing is reseeded.
**(a)**

---

## 5. Measured behaviour (running the ROM bytes)

Method: `tools/harness.py` loads the AppleWin II+ ROM into a py65 NMOS 6502 emulator,
cold-starts Applesoft through the Autostart RESET path, and either types BASIC lines
(through a KEYIN trap) or calls `$EFAE` directly. All results **(E)**.

### 5.1 Cold-start seed and the fifth-byte bug

```
; ROM: applesoft
F123: 80 4F C7 52 58         .HS 804FC75258  ; S-C: "APPROX. = .811635157" / "THE LAST BYTE IS NOT COPIED"
F150: A2 1C                  LDX #GENERIC.END-GENERIC.CHRGET-1   ; assembles to $1C
F152: BD 0A F1     .1        LDA GENERIC.CHRGET-1,X
F155: 95 B0                  STA CHRGET-1,X
F157: 86 F1                  STX SPEEDZ
F159: CA                     DEX
F15A: D0 F6                  BNE .1
```

The loop copies source `$F10B–$F126` to `$B1–$CC`. That is `CHRGET` plus the first
**four** seed bytes. `$F127` (`$58`) is never copied, so `$CD`, the lowest mantissa byte
of `RNDSEED`, keeps whatever RAM held. **(a)** (S-C, McFadden and Davis all flag this.)
The bug is already in Microsoft's source. Line 6733 is `LDXI RNDX+4-CHRGET`, which stops
one byte short when `ADDPRC` adds a fifth byte. The ROM-image seed table (lines
6694–6698) is `128, 79, 199, 82, <88>` = `$80 $4F $C7 $52 $58`, which matches the Apple
ROM. (The RAM-loaded table at lines 978–982 has `89`.) **(a)**

Seed as stored in ROM: 0.811635157. Seed actually used with `$CD=$00`: 0.811635137. **(a)**

Consequences **(E)**:

| RAM byte `$CD` at power-on | first five `RND(1)` after cold start |
|---|---|
| `$00` (and `$01`) | .270011996 .139756248 .690102028 .141352116 .152267027 |
| `$58` (the intended byte) | .512199496 .362071259 .653373034 .550275739 .345680522 |
| `$FF` | .973136996 .103117626 .0177148333 .779343355 .551834438 |

The 256 possible values of `$CD` produce **181 distinct** first outputs, and 181
distinct 5-value sequences.

* "Every machine produces the same sequence after power-on" is true only **for a given
  power-on value of `$CD`**. What real DRAM holds there at power-on was **not measured**.
  An emulator that zeroes RAM will always show the `$00` row. **(E)** for the
  dependency; the real-hardware distribution is unknown.
* **Ctrl-RESET does not touch the seed.** Autostart warm-starts BASIC through `SOFTEV =
  $E003`. The seed was `7E 0F 1C 43 0E` before the reset and after it. **(E)**
* **`E000G` from the monitor (BASIC cold start)** reloads four bytes and leaves `$CD`
  as the last `RND` left it. Seed afterwards: `80 4F C7 52 CB`. **(E)**
* DOS 3.3 boot was not emulated. Whether DOS touches `$C9-$CD` is **unverified**.

### 5.2 Cycle structure: short attractor cycles

The generator was iterated through the ROM routine, and each 5-byte state was checked
against all earlier states.

| Starting seed | Calls before entering cycle | Cycle length |
|---|---|---|
| cold start, `$CD=$00` | 19,263 | **37,758** |
| cold start, `$CD=$FF` | 6,818 | **37,758** |
| `RND(-1)` | 1,060 | **37,758** |
| `RND(-2)` | 3,887 | **32,366** |
| `RND(-12345)` | 26,120 | **37,758** |
| `RND(-54321)` | 1,383 | **32,366** |

All six seeds tested fell into one of two cycles, of 37,758 and 32,366 states. The state
space is roughly 2³² packed values. **(E)**

**Update, 2026-09-12.** Those six seeds were not representative. The research agent's
exhaustive sweep over all 256 cold-start values of `$CD`
(`research/tools/cd_sweep_results.jsonl`, `research/LITERATURE.md` C1/Q5b) found **five**
cycles:

| Cycle length | `$CD` values leading to it | Example `$CD` (calls before entering) |
|---|---|---|
| 37,758 | 110 of 256 (43.0%) | `$00` (19,263), `$FF` (6,818) |
| 32,366 | 78 (30.5%) | `$18` (15,020) |
| **202** | **59 (23.0%)** | **`$58`, the byte the ROM meant to copy (15,382)**, `$7A` (12,155) |
| 4,082 | 5 (2.0%) | `$BC` (12,930) |
| 12,559 | 4 (1.6%) | `$A8` (2,566) |

`tools/deck_audit.py` independently re-derived the 37,758 (`$FF`), 32,366 (`RND(-2)`),
202 (`$58`), 12,559 (`$A8`) and 4,082 (`$BC`) rows on the ROM. The 202 loop matches
Kaner & Vokey's published "repeating itself every 202 numbers" (LITERATURE [A3]). **(E)**
Reseed arguments were not swept for their cycles, so shorter loops may exist.

### 5.3 Bit-level structure

Over the 57,021 cold-start outputs (`$CD=$00`), taking `x = RND(1)`:

* **Fraction bit 25 is stuck.** `INT(x·2²⁵)` is odd in **99.75%** of outputs. In every
  200-call window it is odd 196–200 times. For comparison, bit 24 in the same windows
  ranges 72–127, and bits 1–24 each have means 0.496–0.503. **(E)**
  Mechanism **(a)** from the code: `FMULT` leaves `FAC+1` normalized, top bit = 1. The
  swap moves that byte to `FAC+4`, where its top bit has weight 2⁻²⁵ at exponent `$80`.
  Normalization shifts the mantissa and the exponent together, so that 1-bit keeps
  weight 2⁻²⁵. Only a rounding carry out of bits 26–32 can clear it.
* In packed form this shows as `PEEK(205) >= 128` in 99.5% of outputs ≥ 0.5 **(E)**.
* **High-order bits look fine at this scale.** For `INT(x·N)` with N = 2, 4, 10, 16, 100
  and 256, both the uniformity χ² and the serial-pair χ² are close to their degrees of
  freedom: for N=16, pairs χ² = 253.6 on 255 df. Lag-1 serial correlation is −0.005.
  **(E)**
  → The data **do not support** a slide claiming the leading digits of `RND` are
  visibly serially correlated. The defects that can be shown are the short cycles, the
  stuck low bit, the reseed-value collapse, and seed determinism.

### 5.4 Is the addend really a no-op?

S-C's comment says the `FADD` "DOES NOTHING". With `JSR FADD` patched to `NOP NOP NOP`,
the cold-start sequence is identical for the first **3,885** calls and diverges at call
**3,886**. Stepping each of the 57,021 trajectory states both ways, the addend changes
the stored seed in **5 of 57,021** steps (0.009%). In every such case the difference is
a carry into `FAC+4` and the guard byte. So the addend is almost always absorbed, but it
is **not literally a no-op**. **(E)** Slide wording: "the addend is effectively lost to
precision."

### 5.5 Cost

Measured per call from the RND entry to the final RTS, including all subroutines. The
cycle figures are py65's counts, which include branch-taken and page-cross extras.
**(E)**

| Call | Instructions | Cycles |
|---|---|---|
| `RND(1)` (3,000 calls) | 774 – 1,111 (mean 953) | 2,585 – 3,756 (mean 3,238) |
| `RND(0)` | 33 | 113 |
| `RND(-1)` | 107 | 327 |

At a nominal ≈1.02 MHz, one `RND(1)` costs about 3 ms, plus interpreter overhead. **(c)**

### 5.6 Reseed values

`PRINT RND(-K)` on the ROM **(E)**:

| K | returns |
|---|---|
| 1 | 2.99196472E-08 |
| 2 | 2.99205567E-08 |
| 3 | 4.48217179E-08 |
| 4 | 2.99214662E-08 |
| 100 | 4.66889105E-08 |
| 1000 | 5.83331712E-08 |
| .5 | 2.99187377E-08 |
| 12345 | 3.47904874E-03 |

The next values do differ by seed. After `RND(-1)`: .738207502 .272707136 .299733446.
After `RND(-2)`: .273385388 .621966945 .369081192.

### 5.7 `$4E/$4F` is not an input

No Applesoft code references `$4E`/`$4F` (McFadden cross-reference; S-C listing). The
same five `RND(1)` values came out with the KEYIN counter at `$0041` and at `$3E97`.
Applesoft `RND` gets keyboard "entropy" **only** if the program explicitly passes it,
as in `RND(-(PEEK(78)+256*PEEK(79)))` (see `keyboard-seed.md`). **(a)+(E)**

---

## 6. Supporting FP routines (short ones verbatim)

```
; ROM: applesoft
;  SIGN — return A = $FF/$00/$01
EB82: A5 9D        SIGN      LDA FAC
EB84: F0 09                  BEQ RTS.15
EB86: A5 A2        SIGN1     LDA FAC.SIGN
EB88: 2A           SIGN2     ROL
EB89: A9 FF                  LDA #$FF
EB8B: B0 02                  BCS RTS.15
EB8D: A9 01                  LDA #$01
EB8F: 60           RTS.15    RTS

;  LOAD.FAC.FROM.YA — unpack 5 bytes at (Y,A)
EAF9: 85 5E        LOAD.FAC.FROM.YA STA INDEX
EAFB: 84 5F                  STY INDEX+1
EAFD: A0 04                  LDY #4            ; always five bytes -> the "missing byte" gets read
EAFF: B1 5E                  LDA (INDEX),Y
EB01: 85 A1                  STA FAC+4
EB03: 88                     DEY
EB04: B1 5E                  LDA (INDEX),Y
EB06: 85 A0                  STA FAC+3
EB08: 88                     DEY
EB09: B1 5E                  LDA (INDEX),Y
EB0B: 85 9F                  STA FAC+2
EB0D: 88                     DEY
EB0E: B1 5E                  LDA (INDEX),Y
EB10: 85 A2                  STA FAC.SIGN
EB12: 09 80                  ORA #$80          ; restore the implicit leading 1
EB14: 85 9E                  STA FAC+1
EB16: 88                     DEY
EB17: B1 5E                  LDA (INDEX),Y
EB19: 85 9D                  STA FAC
EB1B: 84 AC                  STY FAC.EXTENSION ; Y=0
EB1D: 60                     RTS

;  FMULT / FADD entries — both load a 5-byte ARG from (Y,A) first
E97F: 20 E3 E9     FMULT     JSR LOAD.ARG.FROM.YA
E982: D0 03        FMULTT    BNE $E987
E7BE: 20 E3 E9     FADD      JSR LOAD.ARG.FROM.YA
E7C1: D0 03        FADDT     BNE $E7C6
E9E3: 85 5E        LOAD.ARG.FROM.YA STA INDEX
E9E5: 84 5F                  STY INDEX+1
E9E7: A0 04                  LDY #4            ; five bytes, same as above, into ARG $A5-$AA

;  NORMALIZE.FAC.2 — byte-at-a-time, then bit-at-a-time
E82E: A0 00        NORMALIZE.FAC.2 LDY #0
E830: 98                     TYA               ; A counts shifts
E831: 18                     CLC
E832: A6 9E        .1        LDX FAC+1
E834: D0 4A                  BNE NORMALIZE.FAC.4
E836: A6 9F                  LDX FAC+2         ; top byte zero: shift 8 bits at once
E838: 86 9E                  STX FAC+1
E83A: A6 A0                  LDX FAC+3
E83C: 86 9F                  STX FAC+2
E83E: A6 A1                  LDX FAC+4
E840: 86 A0                  STX FAC+3
E842: A6 AC                  LDX FAC.EXTENSION ; guard byte (old exponent, in RND) shifts in
E844: 86 A1                  STX FAC+4
E846: 84 AC                  STY FAC.EXTENSION
E848: 69 08                  ADC #8
E84A: C9 20                  CMP #32
E84C: D0 E4                  BNE .1
E84E: A9 00        ZERO.FAC  LDA #0
E850: 85 9D                  STA FAC
E852: 85 A2                  STA FAC.SIGN
E854: 60                     RTS
E874: 69 01        NORMALIZE.FAC.3 ADC #1
E876: 06 AC                  ASL FAC.EXTENSION
E878: 26 A1                  ROL FAC+4
E87A: 26 A0                  ROL FAC+3
E87C: 26 9F                  ROL FAC+2
E87E: 26 9E                  ROL FAC+1
E880: 10 F2        NORMALIZE.FAC.4 BPL NORMALIZE.FAC.3
E882: 38                     SEC
E883: E5 9D                  SBC FAC           ; exponent -= shifts
E885: B0 C7                  BCS ZERO.FAC      ; underflow -> 0
E887: 49 FF                  EOR #$FF
E889: 69 01                  ADC #1
E88B: 85 9D                  STA FAC

;  STORE.FAC.AT.YX.ROUNDED and ROUND.FAC
EB2B: 20 72 EB     STORE.FAC.AT.YX.ROUNDED JSR ROUND.FAC
EB2E: 86 5E                  STX INDEX
EB30: 84 5F                  STY INDEX+1
EB32: A0 04                  LDY #4
EB34: A5 A1                  LDA FAC+4
EB36: 91 5E                  STA (INDEX),Y
EB38: 88                     DEY
EB39: A5 A0                  LDA FAC+3
EB3B: 91 5E                  STA (INDEX),Y
EB3D: 88                     DEY
EB3E: A5 9F                  LDA FAC+2
EB40: 91 5E                  STA (INDEX),Y
EB42: 88                     DEY
EB43: A5 A2                  LDA FAC.SIGN
EB45: 09 7F                  ORA #$7F
EB47: 25 9E                  AND FAC+1         ; sign replaces the implicit 1
EB49: 91 5E                  STA (INDEX),Y
EB4B: 88                     DEY
EB4C: A5 9D                  LDA FAC
EB4E: 91 5E                  STA (INDEX),Y
EB50: 84 AC                  STY FAC.EXTENSION
EB52: 60                     RTS
EB72: A5 9D        ROUND.FAC LDA FAC
EB74: F0 FB                  BEQ RTS.14
EB76: 06 AC                  ASL FAC.EXTENSION ; guard >= $80 ?
EB78: 90 F7                  BCC RTS.14
EB7A: 20 C6 E8               JSR INCREMENT.FAC.MANTISSA
EB7D: D0 F2                  BNE RTS.14
EB7F: 4C 8F E8               JMP NORMALIZE.FAC.6
E8C6: E6 A1        INCREMENT.FAC.MANTISSA INC FAC+4
E8C8: D0 0A                  BNE RTS.12
E8CA: E6 A0                  INC FAC+3
E8CC: D0 06                  BNE RTS.12
E8CE: E6 9F                  INC FAC+2
E8D0: D0 02                  BNE RTS.12
E8D2: E6 9E                  INC FAC+1
E8D4: 60           RTS.12    RTS
```

The long `FMULT` and `FADD` bodies ($E987–$E9E2, $E7C6–$E82D) are not reproduced.
Their full commented text is in S-C DocuMentor `S.E7A0` / `S.E913`, and in McFadden's
`Applesoft.html`.

---

## 7. Safe / unsafe slide statements

| Say | Don't say |
|---|---|
| "Multiplier as executed: 11879546.40625 (`98 35 44 7A` + stray `68`)" | "multiplier 11879546" without the caveat, or any integer-LCG modulus |
| "Addend 3.93×10⁻⁸ is lost to precision (changed 5 of 57,021 steps)" | "the addend does nothing" |
| "Cold start copies only 4 of 5 seed bytes; `$CD` is leftover RAM" | "every Apple II gives the identical sequence" (unqualified) |
| "Ctrl-RESET preserves the seed" | "RESET reseeds RND" |
| "Observed cycles: 37,758, 32,366, 12,559, 4,082 and 202 (23% of power-on `$CD` values reach the 202 loop)" | "period 2³²" or any period derived from LCG theory |
| "Dice faces from `INT(RND(1)*6)+1` are statistically uniform in every long cycle; see `deck-code-audit.md`" | "Applesoft's dice are loaded" as a distribution claim |
| "Fraction bit 25 is set ≈99.75% of the time" | "low-order bits are serially correlated" (not shown by these data) |
| "Applesoft RND never reads `$4E/$4F`" | "Applesoft seeds from keyboard timing" |
