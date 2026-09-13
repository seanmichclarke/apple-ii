# Deck code audit: "Applesoft's Loaded Dice" (Jeff Robison, VCF Midwest 21)

Audited 2026-09-12 by the source-code agent against `deck/Applesoft_Loaded_Dice_Deck_1.pptx`
(slide text `ppt/slides/slideN.xml`, notes `ppt/notesSlides/notesSlideN.xml`, and all 11
embedded images, transcribed by eye). Every code listing, constant, address and numeric
claim on the 10 slides and in the notes is checked against the verified ROM bytes and
emulation in this directory.

Verdicts: **CORRECT** / **WRONG** / **UNVERIFIABLE** (can't be settled from the ROM bytes,
the listings or emulation). Evidence labels as in `applesoft-rnd.md`: **(a)** ROM bytes or
published listing, **(E)** measured by running the ROM, **(c)** inference.

New measurements come from `tools/deck_audit.py`. Every die face in it is computed by the
ROM's own `RND` → `FMULT` (×6.0) → `INT`. That path was checked against BASIC itself: 40 of
40 faces printed by `FOR I=1 TO 40: PRINT INT(RND(1)*6)+1;: NEXT` matched. `verify.py`
re-run today: 402 listing comparisons, 0 mismatches; all demos OK.

---

## 1. The thesis question: are Applesoft's dice loaded?

**Short answer: no, not in the sense the title says. The code does not produce a biased
die. It produces a scripted one.**

First, a correction to the question's premise. Applesoft `RND` is not an LCG. There is no
modulus. It multiplies by 11879546.40625, adds a constant that is almost always lost to
precision, swaps the most and least significant mantissa bytes, and renormalizes into
(0,1) (`applesoft-rnd.md` §2–4). LCG theory (lattices, "weak low-order bits" in the
mod-2ᵏ sense) doesn't carry over. The low-bit defect it really has is different: fraction
bit 25 is set 99.75% of the time (§5.3). That bit has weight 2⁻²⁵, so no dice, card or
percentage roll can see it.

### 1.1 Distribution over whole cycles (the exact long-run behaviour)

Every Applesoft trajectory ends in a loop, so the face counts over one full loop *are* its
long-run distribution, not a sample estimate. All numbers **(E)**, ROM-computed:

| Start (cycle) | Face counts 1–6 over one full loop | Faces χ² (5 df) | Pairs χ² (35 df) | Triples χ² (215 df) |
|---|---|---|---|---|
| cold `$CD=$FF`, the .973136996 machine (37,758) | 6377 6211 6228 6314 6285 6343 | 3.34, p=0.65 | 28.94, p=0.76 | 224.7, p=0.31 |
| `RND(-2)` (32,366) | 5336 5313 5349 5487 5458 5423 | 4.73, p=0.45 | 44.18, p=0.14 | 231.0, p=0.22 |
| cold `$CD=$A8` (12,559) | 2126 2097 2097 2033 2134 2072 | 3.27, p=0.66 | 32.32, p=0.60 | 201.7, p=0.73 |
| cold `$CD=$BC` (4,082) | 707 681 708 650 646 690 | 5.39, p=0.37 | 37.77, p=0.34 | 194.9, p=0.83 |
| cold `$CD=$58` (**202**) | 40 29 31 45 23 34 | 9.25, p=0.10 | n/a | n/a |

(5% critical values: 11.07 / 49.80 / ≈250. p-values from the χ² survival function.)

In the four long loops, single faces, consecutive pairs and triples are all consistent with
a fair die. Over the .973136996 machine's 37,758-roll loop, the largest deviation of any face
from 1/6 is 0.0022, against a 1-σ of 0.0019 for fair rolls. Earlier work agrees: 10-bin and
256-bin χ², lag-1 serial correlation −0.004 (`research/tools/distribution_results.jsonl`),
and the serial-pair χ² in `applesoft-rnd.md` §5.3.

### 1.2 Where "loaded" *does* hold, and why it's the wrong word

1. **The 202-roll loop.** Of the 256 possible power-on values of `$CD`, 59 (23%) lead
   an untouched program into a 202-number loop. The example starts in the sweep entered it
   after 3,062–23,318 calls (`$58`, the byte the ROM meant to copy, after 15,382). Inside it,
   the long-run shares are fixed forever: face 4 comes up 22.3% of the time and face 5 11.4%.
   That is a permanently lopsided die. But the imbalance is what 202 fair rolls would show
   one time in ten (p=0.10). The defect is that the same 202 rolls repeat, not a weighting
   mechanism. This is Kaner & Vokey's "repeating itself every 202 numbers" (LITERATURE
   [A3]), reproduced on the ROM.
2. **Using the reseed's return value.** For every K from 1 to 65,535, `RND(-K)` returns
   ≈3×10⁻⁸, so `INT(RND(-K)*6)+1` is **1 in 65,535 of 65,535 cases** (E). That *is* a fully
   loaded die, but only in code that uses the number the reseed returns.
3. **Reseeding inside the loop.** `X=RND(-7): PRINT RND(1)` in a loop prints one value
   forever (`demos.md` Demo 3, line 80). That's a misuse, not a bias.

### 1.3 What the disassembly does support

* **Predetermined rolls.** With the same power-on byte at `$CD`, every power-on gives the
  same rolls. On the `$CD=$FF` machine the first 20 dice are always
  `6 1 1 5 4 4 6 4 5 5 1 5 6 6 4 2 3 6 3 1` (E).
* **Short loops.** Every trajectory falls into one of five loops: 37,758, 32,366,
  12,559, 4,082 or 202 (`applesoft-rnd.md` §5.2).
* **No entropy by default.** `RND` never reads `$4E/$4F`, and only COLD.START and `RND`
  write `$C9–$CD` (§5.7; §3 below, slide 6).
* **`RND(-K)` returns a useless value**, and `RND(0)` doesn't reseed.

**Proposed framing.** The dice aren't loaded, they're **scripted**. Candidate titles:
*"Applesoft's Stacked Deck"* (a stacked deck is fair cards in a fixed order, which is exactly
what the code does), or keep *"Loaded Dice"* as the hook and make slide 2 say it outright:
*"The dice aren't weighted. They're pre-rolled."* A one-sentence thesis the code supports:

> Applesoft's RND rolls fair-looking dice from a script: the same power-on memory gives the
> same rolls, every sequence ends in a loop, and nearly a quarter of power-on states end up
> in a loop only 202 rolls long.

This also fits the deck's real argument, which is about seeding, not bias. The title is
Jeff's call; this section is the evidence for it.

---

## 2. Is `INT(RND(1)*6)+1` biased by truncation? The arithmetic

**No, not at any detectable level.** Modulo bias needs a *small integer range reduced mod
N*. Applesoft doesn't do that. It scales a 32-bit fraction and truncates.

**Ideal bound.** Suppose x took each of the 2³² values k/2³² equally often. Face f is hit by
the k in [⌈(f−1)·2³²/6⌉, ⌈f·2³²/6⌉). 2³²/6 = 715,827,882.67, so the counts are

```
face:   1            2            3            4            5            6
count:  715,827,883  715,827,883  715,827,882  715,827,883  715,827,883  715,827,882
```

The largest relative deviation is (2/3)/715,827,882.67 = **9.3×10⁻¹⁰** (E, exact integer arithmetic).
To see a 1-σ effect of that size (≈1.6×10⁻¹⁰ in probability) you'd need about
p(1−p)/δ² ≈ 5.8×10¹⁸ rolls. At ≈3 ms per `RND(1)` (§5.5) that is roughly 5×10⁸ years. **(c)**

**The FP representation doesn't change this.** Applesoft values aren't evenly spaced:
below 0.5 the mantissa gives finer steps. That only makes the lattice finer, never coarser.
The boundaries 1/6, 1/3, 2/3 and 5/6 are repeating binary fractions (1/6 = 0.0010101…₂),
so no representable x sits exactly on one. 1/2 is exact, and `INT` puts it in face 4, as it
should.

**Rounding in the multiply.** `FMULT` rounds 6·x to 32 mantissa bits, so a value a hair
below k/6 could in principle round up to exactly k and move to the next face. Measured on
the ROM: **0 mismatches** between the ROM's `INT(RND(1)*6)+1` and the exact rational
⌊6x⌋+1 across **128,550 outputs** (all five trajectories above, tails included). No output
was ≥ 1. **(E)**

**Contrast: Integer BASIC really does have modulo bias, but not for dice.** `RND(6)` is
(15-bit LFSR state) `MOD 6` (`JMP MOD` at `$EF7D`). Over one full period, the states are
1..32,767 once each:

```
32767 = 6·5461 + 1   →   RND(6)+1 faces: 5461 5462 5461 5461 5461 5461
```

Face 2 is 0.018% more likely (E, model validated 300/300 against the ROM). That's
negligible for dice, but serious for large N. For `RND(20000)`, results 1–12,767 come up
**twice as often** as 12,768–19,999 (E). That is a genuinely loaded range. Keystroke waits
also add to the same register, which disturbs the LFSR walk.

---

## 3. Slide-by-slide audit

### Slide 1: title

| Claim | Verified source says | Verdict | Corrected text |
|---|---|---|---|
| Title "Applesoft's Loaded Dice" | Faces uniform over every long loop; bias appears only in the 202-loop (p=0.10) and in `RND(-K)` misuse (§1) | **WRONG** as a distribution claim | "Applesoft's Stacked Deck" or keep the hook and qualify on slide 2 (§1.3) |
| Notes: "boot the machine cold, PRINT RND(1), reboot, same number. Do it three times" | Same number only after a true **power cycle**, and only if power-on RAM gives the same `$CD` each time (`$FE`/`$FF` for .973136996). **Ctrl-RESET** keeps the seed, so you get the *next* number (E). **`E000G`** reloads 4 bytes but `$CD` keeps the last `RND`'s byte, giving a different number (E). DOS 3.3 boot (`PR#6`) not tested | **WRONG** for Ctrl-RESET and warm/BASIC restarts; conditional for power cycles | "Power-cycle the machine (not Ctrl-RESET, not PR#6), PRINT RND(1), power-cycle again, same number. Rehearse on the show machine first." |

### Slide 2: "The Problem"

| Claim | Verified source says | Verdict | Corrected text |
|---|---|---|---|
| `PRINT RND(1)` → `.973136996` | Exactly this value when `$CD` is `$FE` or `$FF` at the first call; the resulting seed is `80 79 1F 81 94`. The 256 values of `$CD` give 181 different first outputs; `$CD=$00` gives .270011996 (E, re-derived today) | **CORRECT** (conditional) | Footnote: "on this machine's power-on RAM; the ROM seeds only 4 of 5 bytes" |
| Notes: "The amber box is the part that has to land. Slide 4 depends on it." | No amber box on slide 2. This note duplicates slide 3's | n/a (misplaced note) | Move to slide 3 only |

### Slide 3: what an RNG is

| Claim | Verified source says | Verdict | Corrected text |
|---|---|---|---|
| "Pseudo-random … The answer becomes the next starting number." | True of Applesoft: `STORE.FAC.AT.YX.ROUNDED` writes the result to `$C9` and returns the same value (a). **Not** true of Integer BASIC: it returns (state before shifting) MOD N, and the next state is that state clocked 17 more times (a) | **CORRECT** for Applesoft; wrong for Integer BASIC | Fine as is if the slide is about Applesoft |
| "Entropy is the key to sufficient randomness and unpatterned results." | Seed entropy sets the *starting point* only. Applesoft still falls into its loops from any seed, and Integer BASIC is a 15-bit LFSR whatever the seed (E) | **WRONG** (conflates seeding with generator quality) | "Entropy makes the starting point unpredictable. It can't fix a generator that loops." |

### Slide 4: "Integer BASIC, 1977"

| Claim | Verified source says | Verdict | Corrected text |
|---|---|---|---|
| "Woz wrote a generator at $EF4E" | `EF4E: 20 15 E7 RND JSR GET16BIT`, entry for token `$2F` (a, 2 dumps) | **CORRECT** | |
| "Known period with limited range" | Period **32,767** (maximal 15-bit LFSR, x¹⁵+x¹⁴+1) when no key waits intervene. Range 0..N−1 for N>0, −(N−1)..0 for N<0; `RND(0)` → `*** >32767 ERR` (E) | **CORRECT** but unquantified | "Period 32,767; returns 0 to N−1" |
| "No Floating point" | 16-bit integer arithmetic, `MOD` operator (a) | **CORRECT** | |
| "Sufficiently random" | Subjective. Measured facts: `RND(6)` bias 1 in 5,461; `RND(20000)` 2:1 range bias (§2) | **UNVERIFIABLE** | "Good enough for games; biased for large N" |
| "counter at $4E and $4F that goes up while the monitor sits waiting for a keypress. Integer BASIC reads it." | `FD1B: E6 4E INC RNDL`, `FD1F: E6 4F INC RNDH` in the KEYIN wait loop; `EF51: A5 4E`, `EF56: A5 4F` in RND (a). It also **writes it back**: the counter *is* the generator state (`EF60: 85 4F`, `EF6D/EF6F: ROL`) | **CORRECT** (understated) | "…Integer BASIC's RND uses it as its own state." |
| "Sander-Cederlof, Apple Assembly Line, August 1981." | Citation, not code. Review A confirmed the article (txbobsc `aal8108`) and that it calls `$EF51`, not `$EF4E` | **UNVERIFIABLE** here | |
| Notes: "$4E/$4F is not a jiffy clock … The Apple II has no timer doing this." | The only writers are the KEYIN wait loop and Integer BASIC `RND`; the count is frozen while a program runs (a) | **CORRECT** | |

### Slide 5: "Built-in Entropy Source"

Captions were paired with images by their positions in `slide5.xml`.

| Claim | Verified source says | Verdict | Corrected text |
|---|---|---|---|
| Image, caption OrigF8ROM: `fd1b: e6 4e KEYIN inc RNDL` … `fd2e: 60 rts` (9 lines, `IOADR` labels) | All 9 lines byte-identical to AppleWin `Apple2.rom` (a) | **CORRECT** | |
| Image, caption AutoF8ROM: same loop, `KBD` labels | Byte-identical to `Apple2_Plus.rom` and apple2js `fpbasic.ts` (a) | **CORRECT** | |
| Image, "Integer BASIC, at $EF4E": `ef4e: 20 15 e7` … `ef7d: 4c 7a e2 jmp MOD` (24 lines) | All 24 lines byte-identical to both Integer BASIC dumps. The comment "uses tken $3f (" is a typo in the source listing, harmless | **CORRECT** | |
| Image, caption **IIc_16kb**: `cc71: e6 4e inc RNDL ;update seed`, `cc73: d0 1c bne UD2`, `cc75: a5 4f lda RNDH` (cropped) | No //c ROM dump in AppleWin or apple2js. The pattern `E6 4E D0 1C A5 4F` is in **no** //e, ][+ or II image. The enhanced //e has a similar routine at `$C27D` (`E6 4E D0 0A A5 4F E6 4F 45 4F`), with a different branch offset (a) | **UNVERIFIABLE** (the image is also cropped mid-line top and bottom) | Re-crop cleanly; label "//c firmware (per McFadden)" |
| Image, caption **Unenh_IIe_80col**: `cb15: e6 4e GETKEY inc MON_RNDL` … `cb23: 60 rts` | All 15 bytes present at `$CB15` in **AppleWin `Apple2e.rom` and apple2js `apple2e.ts`** (unenhanced //e); a second loop is at `$C2D5`. The enhanced //e has the same 15 bytes at `$C83B` (a) | **CORRECT** | |
| "Present in some form in all Apple II ROMs" | `INC $4E` wait loops confirmed in ROM bytes for the II, ][+, unenhanced //e and enhanced //e. //c only via the screenshot. IIc Plus and IIgs not checked | **UNVERIFIABLE** for "all" | "In the II, ][+ and //e ROMs, and the //c firmware" |
| Notes: "Point at the **bne** going back to KEYIN." | `FD1D: D0 02 BNE KEYIN2` branches **forward**, skipping `INC RNDH` unless RNDL wrapped. The branch back to KEYIN is **`FD24: 10 F5 BPL KEYIN`** (a) | **WRONG** | "Point at the BPL at $FD24 going back to KEYIN." |
| Notes: "The counter gets bumped before the keyboard is read, every pass. It's a loop count, not a keystroke count." | `INC` at `$FD1B` precedes `BIT KBD` at `$FD21` on every pass (a) | **CORRECT** | |
| Notes: "Sit there two seconds and it's gone round tens of thousands of times." | 15 cycles per pass (19 on the RNDL wrap), so ≈68,000 counts/s at ≈1.02 MHz (c; clock rate not measured). Two seconds ≈ **136,000 counts**, and the 16-bit counter **wraps about twice**. Applies to the II/][+ loop; the //e and //c loops are longer and unmeasured | **WRONG** (undercounts counts; overstates wraps) | "Sit there two seconds and it has counted about 136,000 times, wrapping its 16 bits twice." |
| Notes: "the second thing Integer BASIC's RND does is read $4E" | `EF4E JSR GET16BIT`, then `EF51 LDA $4E` (a) | **CORRECT** | |
| Notes: "The disassembly is Paul Santa-Maria's work, converted by Andy McFadden." | Matches `IntegerBASIC.html` attribution (`PROVENANCE.md`) | **CORRECT** | |
| Notes: "Woz wrote Integer BASIC with no assembler … only hand-written pages in a binder" | Historical claim; nothing in the ROM or listing bears on it | **UNVERIFIABLE** here | Cite a source (e.g. Woz interview) |

### Slide 6: "Applesoft, 1978"

| Claim | Verified source says | Verdict | Corrected text |
|---|---|---|---|
| "Applesoft, 1978" over a listing at `$EFAE` | `$EFAE` is **Applesoft II in the Apple ][+ ROM** (1979); the //e ROMs are identical there. The *algorithm and constants* date from 1978: Microsoft `m6502.asm` (git date 1978-07-27) has the same RND in octal (a) | **WRONG** (the date and the address belong to different artifacts) | "Applesoft II (1978 code), as burned into the ][+ ROM" |
| "Applesoft relies on different seed. However, the seed for Integer BASIC remains." | Applesoft `RND` never references `$4E/$4F`; the Autostart KEYIN still increments them; identical `RND(1)` output with counter `$0041` vs `$3E97` (a)+(E) | **CORRECT** | |
| "Takes the seed at $C9, multiplies, adds, swaps two bytes around, forces the result under 1, writes it back to $C9." | Right in outline. Precisely: 5-byte seed `$C9–$CD`; ×**11879546.40625** (the 4-byte constant plus a stray 5th byte `$68`); **+3.93×10⁻⁸, which changes the stored seed in only 5 of 57,021 steps**; swaps **FAC+1 ↔ FAC+4** (top and bottom mantissa bytes); clears the sign; old exponent becomes the guard byte; exponent `$80`; normalize; round; store (a)+(E) | **CORRECT** (simplified) | "…multiplies by a constant that's missing a byte, adds a number too small to matter, swaps the top and bottom bytes…" |
| Image: `efae: 20 82 eb RND jsr SIGN` … `efe7: 4c 2b eb jmp STORE_FAC_AT_YX_ROUNDED` | All 28 lines byte-identical to both ][+ dumps (and the //e images) (a) | **CORRECT** | Add credit: "S-C DocuMentor (Sander-Cederlof) via 6502disassembly.com (McFadden)" |
| Image comment "<<< this does nothing, due to small exponent >>>" | S-C's annotation, not Microsoft's. Nearly true: without the add, the sequence diverges at call 3,886 (E) | **CORRECT** in practice, overstated literally | "effectively lost to precision" |
| Image comments "very poor RND algorithm", "to supposedly make it more random" | S-C DocuMentor annotations, not Microsoft source (Microsoft's comment says the swap gives "A RANDOM CHANCE OF GETTING A NUMBER LESS THAN OR GREATER THAN .5") (a) | **CORRECT** as S-C quotes; unattributed | Attribute to Sander-Cederlof |
| Notes: "This is the whole thing. **Twenty-six** instructions." | **28** instructions from `$EFAE` through `JMP` at `$EFE7` (py65 disassembly of the ROM). `RND(1)` executes all 28; `RND(-n)` executes 17; `RND(0)` 8 plus the shared `RTS`. A full `RND(1)` call runs ≈953 instructions including the FP routines (E) | **WRONG** | "Twenty-eight instructions, plus about 900 more inside the floating-point routines it calls." |
| Notes: "the seed comes from $C9, which got a fixed value out of ROM at boot" | COLD.START copies only **4 of 5** seed bytes: the loop `F150: A2 1C … F15A: D0 F6` copies `$F10B–$F126` to `$B1–$CC`, so `80 4F C7 52` reach `$C9–$CC`. `$F127` (`$58`) never reaches `$CD`, which keeps whatever RAM held (a) | **WRONG** (partly) | "…which got four fixed bytes out of ROM at boot, and one byte of whatever was lying in RAM." |
| Notes: "the answer goes back to $C9. Nothing else feeds it." | No instruction in `$D000–$FFFF` writes `$C9–$CD` directly (4 byte-pattern hits all fall mid-instruction); `NEW`, `CLEAR`, `RUN` leave the seed unchanged (E). Only COLD.START and `RND` write it. `RND(-n)` feeds in its argument | **CORRECT** for `RND(+)` | |
| Notes: "McFadden's disassembly at 6502disassembly.com" | That listing is McFadden's SourceGen conversion of **Sander-Cederlof's S-C DocuMentor**; the critical comments are S-C's | **CORRECT** but incomplete | Credit both |
| Alt text `/home/claude/rnd_listing.png` (also `keyin.png`, `intbasic_rnd.png` on slide 5) | Build paths leaked into image descriptions | n/a (hygiene) | Real descriptions |

### Slide 7: "Applesoft Manual, 1978"

| Claim | Verified source says | Verdict | Corrected text |
|---|---|---|---|
| "RND (aexpr) Returns a random real number ≥ 0 and < 1." | `RND(+)` outputs lie in (0,1): 0 of 128,550 ROM outputs were ≥ 1 (E). `RND(-K)` returns ≈3×10⁻⁸ for small integers | **CORRECT** | |
| "If aexpr > 0, RND(aexpr) generates a new random number each time it is used." | `SIGN` → +1 path multiplies/swaps/stores (a). The argument's value is ignored: `RND(.001)`, `RND(1)` and `RND(99)` are identical (a) | **CORRECT** | |
| "If aexpr < 0 … generates the same random number each time it is used with the same aexpr … subsequent … positive arguments will follow the same sequence each time." | `BMI` at `$EFB2` shuffles the argument's own bytes into the seed; same K, same sequence (E, Demo 3) | **CORRECT** | |
| "A different random sequence is initialized by each different negative argument." | K = 1..65,535 give **65,535 distinct seeds** (E). But those sequences merge into at most five loops, and the "random number" each `RND(-K)` returns is ≈3×10⁻⁸ (E) | **CORRECT** at the start; misleading long-run | |
| "If aexpr is zero, RND(aexpr) returns the most recent previous random number generated (CLEAR and NEW do not affect this)." | `EFBC: F0 E7 BEQ RTS.19` returns the loaded seed unchanged (a). `NEW`, `CLEAR`, `RUN` leave `$C9–$CD` unchanged (E). Caveat: right after power-on it returns the ROM seed, which was never "generated" | **CORRECT** | |
| Date "1978" | The Aug 1978 *Applesoft II Reference Manual* (A2L0006X) RND entry reads "X<=0 starts a new sequence of random numbers using X" (`PROVENANCE.md`). That is different wording, and it contradicts this slide's `RND(0)` text. So these scans are from a different edition. archive.org full-text search for "permanent random number table" found nothing (OCR-limited) | **UNVERIFIABLE** (probably wrong edition/date) | Identify the edition and part number |
| Notes (identical to slide 6's: "Twenty-six instructions…") | Copy-pasted from slide 6 | **WRONG** (misplaced; carries the 26 error) | Replace with notes about the manual text |

### Slide 8: "Sources"

| Claim | Verified source says | Verdict | Corrected text |
|---|---|---|---|
| "Kaner & Vokey, 1982. First published account." | Manuscript © 1982; **published in *MICRO* No. 72, June 1984**, pp. 26–35 (LITERATURE [A3], C8). Sparks, "RND is Fatally Flawed", *Call-A.P.P.L.E.* Jan 1983 was in print first | **WRONG** ("first published") | "Kaner & Vokey, MICRO, June 1984 (written 1982)" |
| "Call A.P.P.L.E., Jan 1983, 'RND is Fatally Flawed.'" | Sparks, D., *Call-A.P.P.L.E.* 6, pp. 29–34 (LITERATURE, Crossref citation) | **CORRECT** | Add author and pages |
| "Sander-Cederlof, AAL May 1984. Found the startup bug. The seed copy is off by one." | The bug is real: `LDX #$1C` loop copies 4 of 5 bytes; also present in Microsoft's source (line 6733, `LDXI RNDX+4-CHRGET`) (a). Who found it first is not a code question | **CORRECT** (bug); priority **UNVERIFIABLE** | "Documented the startup bug" |
| "Aldridge 1987, Gleason 1988. Behavior Research Methods. ERIC EJ372427." / "Empson, GS WorldView 1999. Built Moore's LFSR" | Citations; outside the code. One ERIC number for two papers (Review A §10) | **UNVERIFIABLE** here | See `research/LITERATURE.md` |
| Notes: "The 202 figure is measured, from the paper, on real Applesoft." | The figure **is not on any slide**. It exists: Kaner & Vokey, "repeating itself every 202 numbers", entered between the 10,000th and 20,000th number. On the ROM, a cold start with `$CD=$58` enters a 202-loop after 15,382 calls, inside that window; 23% of `$CD` values reach it (E). The printed MICRO OCR lacks the passage; check the scan | **CORRECT** (but orphaned) | Put "202" on the slide: "a loop of 202 numbers" |

### Slide 9: "Two Part Solution"

`LC_Loader.bin` and `Patch_lc.bin` aren't in the workspace, so no patch behaviour can be
verified. Only the addresses and constraints can.

| Claim | Verified source says | Verdict | Corrected text |
|---|---|---|---|
| "Enables language card write mode while keeping ROM readable" | Soft-switch behaviour; not in the audited ROMs and loader not available | **UNVERIFIABLE** | Name the switches used (e.g. `$C081` ×2) |
| "Copies $D000-$FFFF (all of Applesoft and the monitor ROM)" | ][+ ROM image: Applesoft `$D000–$F7FF`, Autostart monitor `$F800–$FFFF`, RESET vector `$FA62` (a). On an original II the same range is Integer BASIC | **CORRECT** (for a ][+ / //e) | |
| "Writes the patch code into the LC at $F5CB (may impact HFIND, supposedly unused by AppleSoft.)" | S-C labels `$F5CB` HFIND, "not called by any Applesoft routine". The ROM scan finds **no direct JSR/JMP to $F5CB anywhere in $D000–$FFFF** (a). Available room `$F5CB–$F5FF` = **53 bytes**. `$F600` is an `RTS` (`60`) that **HLIN branches to** (`F59C: F0 62 BEQ $F600`), and DRAW starts at `$F601` (a). External machine-language callers are not ruled out | **CORRECT** that Applesoft doesn't call it; "may impact"/"supposedly" is weaker than the evidence | "Patch (≤53 bytes) overwrites HFIND at $F5CB–$F5FF, which nothing in the ROM calls; the shared RTS at $F600 is untouched." |
| "Writes JMP $F5CB at $EFAE in the LC copy" | `$EFAE` is RND's entry (dispatch table `$D092` = `AE EF`). The 3-byte JMP replaces exactly `20 82 EB` (`JSR SIGN`), so the patch must call `SIGN` itself (a) | **CORRECT** | |
| "1. Preserves negative and zero RND() functionality while relying on the KEYIN counter present in the ROM." | Patch unavailable. What the ROM requires: `RND(0)` must return `$C9–$CD` unchanged; `RND(-K)` must seed deterministically from K; a counter value of **0** used as a negative seed would go down the `RND(0)` path, because `SIGN` returns 0 (a). The counter is RAM `$4E/$4F`, bumped by ROM code | **UNVERIFIABLE** | Show the patch listing and a before/after test |
| "Two Part Solution" with only item "1." | | n/a (hygiene) | Number both parts |

### Slide 10: "Try it yourself"

| Claim | Verified source says | Verdict | Corrected text |
|---|---|---|---|
| Notes: "does the C64 have this too (yes, same Microsoft code, but Commodore wired RND(0) to hardware timers and gave people TI)" | Microsoft's source: the Commodore build (`REALIO=3`) makes `RND(0)` load VIA timer bytes (`CQHTIM`, lines 6357–6370); the Apple build doesn't (a). That is the **PET** path; the C64 ROM itself was not examined | **CORRECT** for PET; **UNVERIFIABLE** for C64 specifics | |
| Notes: "Why not replace the generator (speed, no space, and RND(-n) has to keep working)" | One `RND(1)` ≈ 953 instructions / 3,238 cycles ≈ 3 ms (E); the patch site holds 53 bytes (a) | **CORRECT** | Numbers available if asked |
| Notes: "What's at $F5CB (HFIND, answer it straight)" | HFIND (a) | **CORRECT** | |

---

## 4. Tally and priorities

Counted by each row's leading verdict in §3 (57 rows). A few CORRECT rows also carry an
unverifiable sub-point: the AAL priority claim and the C64 specifics.

| Verdict | Count |
|---|---|
| CORRECT (including conditional/understated) | 35 |
| WRONG | 10 |
| UNVERIFIABLE | 9 |
| n/a (hygiene/misplaced notes) | 3 |

**Fix before presenting, in order:**
1. **Title/thesis.** "Loaded" isn't supported; "scripted / stacked" is (§1).
2. **Slide 6 notes:** 26 → 28 instructions, and "fixed value out of ROM" → 4 fixed bytes plus one RAM byte. The same error sits in slide 7's notes.
3. **Slide 1 notes demo:** a real power cycle, not Ctrl-RESET (which gives the next number).
4. **Slide 5 notes:** BPL at `$FD24`, not BNE. Two seconds ≈ 136,000 counts, two wraps.
5. **Slide 6 header:** "1978" vs the ][+ ROM address.
6. **Slide 8:** Kaner & Vokey published 1984, not the first publication. Put the 202-loop on the slide; it's the strongest number the deck has.
7. **Slide 3:** entropy ≠ unpatterned output.

**Open:** //c ROM bytes for `$CC71`; the manual edition on slide 7; `Patch_lc.bin`
contents and length (must be ≤ 53 bytes); DOS 3.3 boot effect on `$C9–$CD`; real-hardware
power-on value of `$CD`.

## Reproduce

```sh
cd source/tools
../../.venv/bin/python verify.py                         # listings + demos, seconds
../../.venv/bin/python deck_audit.py rom lattice intbasic   # ~1 s
../../.venv/bin/python deck_audit.py negsweep            # ~45 s
../../.venv/bin/python deck_audit.py cycle-cdff cycle-neg2 cycle-cd58   # ~2.5 min
../../.venv/bin/python -c "import deck_audit as d; d.cycle('A8', d.cold(0xA8)); d.cycle('BC', d.cold(0xBC))"
```

//e checks used AppleWin `Apple2e.rom` (SHA-1 `61fa9254…d747`), `Apple2e_Enhanced.rom`
(`b8ea90ab…198b`) and apple2js `apple2e.ts`, downloaded to `/tmp/a2rng-roms`.
