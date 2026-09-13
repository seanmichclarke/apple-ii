# Deck code audit: "Applesoft's Loaded Dice" (Jeff Robison, VCF Midwest 21)

Audited 2026-09-12 by the source-code agent against `deck/Applesoft_Loaded_Dice_Deck_1.pptx`:
slide text, speaker notes, and all 11 embedded images, transcribed by eye. Every code
listing, constant, address and numeric claim is checked against the verified ROM bytes,
the published disassemblies, and emulation.

**The deck's thesis, as audited:** a **seed regression**. Integer BASIC's `RND` draws on
the `$4E/$4F` keyboard-wait counter. Applesoft's `RND` uses its own seed at `$C9`, loaded
from ROM at boot, so a cold boot gives the same sequence every time. "Loaded dice" is a
metaphor for a predetermined start. It is not a claim of non-uniform output.

Verdicts: **CORRECT** / **WRONG** / **UNVERIFIABLE** (can't be settled from ROM bytes,
listings or emulation). Evidence labels: **(a)** ROM bytes or published listing, **(E)**
measured by running the ROM, **(c)** inference.

Tools: `tools/deck_audit.py` (new measurements), `tools/verify.py` (re-run today: 402 listing
comparisons, 0 mismatches; all demos OK).

---

## 1. Priority verification targets

### Target 1: `.973136996` is the first `PRINT RND(1)` after a cold boot (slide 2)

**Verdict: CORRECT, digit for digit, when the power-on RAM byte at `$CD` is `$FE` or
`$FF`. It is not guaranteed by the ROM alone.**

* **Emulator run, typed at the `]` prompt** (Apple ][+ ROM, py65, no DOS) **(E)**:

  | Power-on RAM fill | `PEEK(205)` | first `PRINT RND(1)` | second |
  |---|---|---|---|
  | **AppleWin default** (`MIP_FF_FF_00_00`) | 255 | **.973136996** | .103117626 |
  | **MAME apple2** (even bytes `$00`, odd `$FF`) | 255 | **.973136996** | .103117626 |
  | all `$FF` | 255 | **.973136996** | .103117626 |
  | all `$00` | 0 | .270011996 | .139756248 |

  The fill patterns come from the emulators' own source. AppleWin `source/Core.cpp:79`
  sets `g_nMemoryClearType = MIP_FF_FF_00_00` by default. `source/Memory.cpp` `MemReset`
  then writes `$FF` to offsets 0 and 1 of every 4 bytes, and `$CD` = 205 ≡ 1 (mod 4).
  MAME `src/mame/apple/apple2.cpp` fills `adr` with `0` and `adr+1` with `$FF` in steps of
  2, and `$CD` is odd. **(a)** for both fill rules. The emulated result is **(E)**.
* **Why it depends on RAM.** Cold start copies only four seed bytes (Target 5), so `$CD`
  keeps its power-on value. That byte is the low mantissa byte of the seed. `RND` swaps the
  low and high mantissa bytes after multiplying, which pushes it into the leading digits.
  Across the 256 possible values of `$CD` there are **181 different first outputs**. Only
  `$FE` and `$FF` give `.973136996` (seed afterwards `80 79 1F 81 94`). **(E)**
* **Scope limits.**
  * Real hardware's power-on DRAM contents were **not measured**. Both major emulators model
    them as a `$00/$FF` stripe that puts `$FF` at `$CD`, which is consistent with the slide.
  * Only the ][+ boot was emulated. The //e and enhanced //e have byte-identical `RND`, seed
    table and copy loop (a), but their reset firmware wasn't traced for writes to `$CD`.
  * AppleWin's default machine is an enhanced //e.
  * A DOS 3.3 boot from disk was not emulated.
  * AppleWin's `-memclear` switch changes the fill; `-memclear 0` gives zeroed RAM and
    `.270011996`.
* **What does *not* repeat it.** Ctrl-RESET preserves the seed, so the next `PRINT RND(1)`
  gives the *next* value, `.103117626`, not the same one. `CALL -151` / `E000G` reloads four
  bytes and leaves `$CD` as the last `RND` left it, so the value differs. **(E)**

**Live-demo checklist (slide 1 notes, slide 2):**
1. Rehearse on the exact machine or emulator and boot path used on stage.
2. Use a true power cycle, not Ctrl-RESET.
3. Optionally type `PRINT PEEK(205)` first. It reads `255` without touching the seed, and it
   shows the audience the leftover byte.
4. Make sure no HELLO program calls `RND`.

### Target 2: `$C9` is Applesoft's seed, loaded with a fixed ROM value at boot (slides 6, 8)

**Verdict: `$C9` CORRECT. "Fixed value from ROM" CORRECT for 4 of 5 bytes, WRONG as
stated.**

* The seed is the 5-byte packed float `RNDSEED` at **`$C9–$CD`** (S-C DocuMentor
  definitions). `RND` loads it with `EFB4: A9 C9 / EFB6: A0 00 / EFB8: 20 F9 EA` and stores
  back with `EFE3: A2 C9 / EFE5: A0 00 / EFE7: 4C 2B EB`. **(a)**
* ROM value: `F123: 80 4F C7 52 58`, which is 0.811635157. Cold start writes
  **`80 4F C7 52` to `$C9–$CC`**, while `$CD` is never written (Target 5). The seed actually
  used with `$CD=$FF` is `80 4F C7 52 FF`. **(a)+(E)**
* Nothing else writes `$C9–$CD`. A synced disassembly of `$D000–$FFFF` finds no direct
  store to them outside COLD.START and `RND`. `NEW`, `CLEAR` and `RUN` leave the seed
  unchanged. **(a)+(E)**
* `RND` never reads `$4E/$4F`. The same output came with the counter at `$0041` and at
  `$3E97`. **(a)+(E)**

### Target 3: `$EF4E` and the `$4E/$4F` KEYIN counter (slides 4, 5)

**Verdict: CORRECT. The counter is bumped once per polling-loop pass. It counts loop
passes, not keystrokes.**

* Integer BASIC `RND` entry: `EF4E: 20 15 E7 JSR GET16BIT`, then `EF51: A5 4E LDA RNDL` and
  `EF56: A5 4F LDA RNDH`. It also writes the register back (`EF60: 85 4F`, shift loop `EF66–EF72`), so the counter *is* the
  generator's state. Two dumps, and a model matched the ROM on 300 of 300 calls. **(a)+(E)**
* Monitor wait loop, identical in the original and Autostart ROMs **(a)**:

  ```
  FD1B: E6 4E     KEYIN   INC RNDL      ; every pass, before the keyboard is read
  FD1D: D0 02             BNE KEYIN2    ; skip high byte unless RNDL wrapped
  FD1F: E6 4F             INC RNDH
  FD21: 2C 00 C0  KEYIN2  BIT KBD       ; key down?
  FD24: 10 F5             BPL KEYIN     ; no: loop back to $FD1B
  ```

  Each pass is 15 CPU cycles (19 when RNDL wraps), about 68,000 counts per second at
  ≈1.02 MHz, so the 16-bit counter wraps about once a second. The timing is **(c)**; the
  clock rate was not measured. The counter is frozen whenever no key wait is running.
* The //e firmware has the same loop shape: `CB15: E6 4E D0 02 E6 4F AD 00 C0 10 F5 8D 10
  C0 60` is byte-identical in two unenhanced //e dumps, and the same bytes sit at `$C83B` in
  the enhanced //e. **(a)**

### Target 4: "Twenty-six instructions" (slide 6 notes, repeated in slide 7 notes)

**Verdict: WRONG. It's 28.**

py65 disassembly of the ROM from `$EFAE` through `JMP STORE.FAC.AT.YX.ROUNDED` at `$EFE7`
gives 28 instructions, matching the 28 lines on slide 6's own image. **(a)**
* `RND(1)` executes all 28 (both branches fall through).
* `RND(-n)` executes 17: `JSR`, `TAX`, the taken `BMI`, then the 14 instructions from
  `$EFCC`.
* `RND(0)` executes 8, then the shared `RTS` at `$EFA5`.

A whole `RND(1)` call runs about 953 instructions including the floating-point subroutines
(E). **Corrected:** "Twenty-eight instructions, plus about 900 more inside the
floating-point routines it calls."

### Target 5: "The seed copy is off by one" (slide 8, Sander-Cederlof AAL May 1984)

**Verdict: CORRECT. Here's exactly what is off by one.**

COLD.START copies `CHRGET` and the seed from ROM into zero page with one shared loop **(a)**:

```
F150: A2 1C        LDX #$1C          ; 28
F152: BD 0A F1  .1 LDA $F10A,X       ; source $F10A+X
F155: 95 B0        STA $B0,X         ; dest   $B0+X
F157: 86 F1        STX SPEEDZ
F159: CA           DEX
F15A: D0 F6        BNE .1            ; stops when X hits 0
```

X runs from `$1C` down to `$01`, so it copies 28 bytes: `$F10B–$F126` → `$B1–$CC`. The block
to copy is 29 bytes: the 24-byte `CHRGET` routine (`$F10B–$F122` → `$B1–$C8`) plus the
5-byte seed (`$F123–$F127` → `$C9–$CD`). The last byte, `$F127` = `$58`, never reaches
`$CD`. **The count should be `$1D`.**

Origin: Microsoft's `m6502.asm` line 6733 computes the count as `LDXI RNDX+4-CHRGET`
($C9+4−$B1 = $1C). That was right for the 4-byte-float build, where the seed has four
bytes. It was never widened when the 9-digit build (`ADDPRC`) made floats five bytes. **(a)**

This off-by-one is why Target 1 depends on RAM. It's the only way anything outside the ROM
reaches the Applesoft seed at boot, and it adds no timing entropy.

**Slide wording:** "Found the startup bug" is fine as a description of what AAL
documented. Who spotted it first isn't a code question. Suggested precise version: "The
cold-start copy loop counts 28 bytes instead of 29, so the seed's last byte is never
copied."

### Target 6: `$F5CB` / HFIND, "supposedly unused by AppleSoft" (slide 9)

**"Unused by Applesoft": CORRECT. Three sources agree, and the hedge can go. "The patch is
safe": UNVERIFIABLE, because `Patch_lc.bin` and `LC_Loader.bin` are not in the workspace.
Hard constraints below.**

Evidence that nothing in the ROM calls HFIND:
1. **S-C DocuMentor, `F5BA.html`**, lines 1100–1110: `HFIND -- CALCULATES CURRENT POSITION
   OF HI-RES CURSOR / (NOT CALLED BY ANY APPLESOFT ROUTINE)`. **(a)**
2. **McFadden's `Applesoft.html`** carries the same comment. The HFIND label has **zero
   references** in its cross-linked listing. This source is *derived* from S-C, so it is
   not independent. **(a)**
3. **Independent ROM scan** of the ][+ image, synced instruction-by-instruction over
   `$D000–$FFFF`. It finds **no** `JSR`, `JMP`, indirect `JMP`, absolute read or branch that
   targets `$F5CB–$F5FF`, and no `CB F5`/`CA F5` address-table pair anywhere. **Nothing
   falls through into it either.** The bytes just before are data: `MSKTBL` at `$F5B2`,
   `CON_1C` at `$F5B9` and `COSINE_TABLE` at `$F5BA–$F5CA`, preceded by `F5B0: 50 D9 BVC
   LF58B ;...always`. **(a)**

Evidence about the patch site, which bears on safety **(a)**:
* HFIND occupies **`$F5CB–$F5FF`, 53 bytes**. It reads `$26/$27` (HBASL/H), `$30` (HMASK)
  and `$E5`, writes the cursor position to `$E0–$E2`, and ends in the `RTS` at **`$F600`**.
* **`$F600` is shared.** HLIN (`HPLOT … TO`) branches to it: `F59C: F0 62 BEQ $F600`. **DRAW
  starts at `$F601`.** A patch longer than 53 bytes, or one that changes `$F600`, breaks
  line drawing, and a longer one breaks `DRAW`/`XDRAW` too.
* **`JMP $F5CB` at `$EFAE` overwrites exactly `20 82 EB` (`JSR SIGN`)**, RND's first
  instruction. The patch has to call `SIGN` itself before it can tell `RND(-n)`, `RND(0)`
  and `RND(+)` apart.
* The ROM contract "preserves negative and zero RND()" has to keep:
  * `RND(0)` returns `$C9–$CD` unchanged (`EFBC: BEQ RTS.19`).
  * `RND(-K)` seeds deterministically from K.
  * A counter value of `$0000` passed as a negative seed is zero, so `SIGN` returns 0 and it
    silently takes the `RND(0)` path.

Not ruled out:
* **External callers.** HFIND is a named, documented routine in the circulated Applesoft
  disassemblies, so machine-language hi-res programs could `JSR $F5CB`. No source here
  establishes whether commercial software does.
* **Language-card environment.** ProDOS in LC RAM, `INT`/`FP` bank switching, RESET forcing
  ROM read on the //e and //c: outside the ROM code; see `review/REVIEW_A_TECHNICAL.md` §3.

**Corrected slide text:** "Patch (≤ 53 bytes) overwrites HFIND at `$F5CB–$F5FF`, which no
Applesoft or monitor code calls (S-C DocuMentor; ROM scan). The shared `RTS` at `$F600` is
untouched."

**To verify the patch:** supply `Patch_lc.bin` and `LC_Loader.bin`. They can be run on the
][+ ROM in this emulator to check the length, that `$F600` is intact, `RND(0)`, `RND(-1)`
repeatability, and `HLIN`/`DRAW` still returning.

---

## 2. The thesis as a whole: uniform but deterministic, same sequence every cold boot

| Part of the claim | Verdict | Evidence |
|---|---|---|
| Deterministic | **CORRECT** | Output depends only on the 5 seed bytes; `demos.md` Demo 1B replays the power-on sequence exactly (E) |
| Identical sequence every cold boot | **CORRECT per machine** | Holds whenever power-on RAM gives the same `$CD`; AppleWin default and MAME both give `$FF` (§1 Target 1). Not every *machine*: 181 first values exist across `$CD` (E) |
| Seeded from a fixed ROM value | **Mostly**: 4 of 5 bytes | Target 5 |
| Integer BASIC gets real, modest entropy from key waits | **CORRECT** | `$4E/$4F` is its state, and every `KEYIN` pass bumps it; same program, different key timing, different output (E) |
| The entropy source remains, unused by Applesoft | **CORRECT** | Autostart KEYIN still counts; Applesoft never reads it (a)+(E) |
| "Uniform" (not a deck claim, but it holds) | **CORRECT** | Appendix A |

Two caveats a pedant may raise, both consistent with the thesis:
* Warm paths don't reseed. Ctrl-RESET continues the sequence (E).
* Every Applesoft sequence eventually loops: 37,758, 32,366, 12,559, 4,082 or 202 numbers
  (`applesoft-rnd.md` §5.2). That's a generator defect, separate from the seed regression.
  Slide 8's notes allude to the 202 loop.

---

## 3. Slide-by-slide audit

### Slide 1: title

| Claim | Verified source says | Verdict | Corrected text |
|---|---|---|---|
| Title "Applesoft's Loaded Dice" (metaphor for a predetermined start) | Start is predetermined per power-on RAM state (§1). Output is not weighted (Appendix A) | **CORRECT** as metaphor | Say once, early, "not weighted, pre-rolled", so no one reads it as a bias claim |
| Notes: "boot the machine cold, PRINT RND(1), reboot, same number. Do it three times" | Same number after each **power cycle** with the same power-on `$CD` (AppleWin default, MAME: `.973136996`). Ctrl-RESET gives the *next* number; `E000G` gives a different one (E) | **CORRECT** for power cycles; **WRONG** if "reboot" means Ctrl-RESET | "Power-cycle, PRINT RND(1), power-cycle again, same number." |

### Slide 2: "The Problem"

| Claim | Verified source says | Verdict | Corrected text |
|---|---|---|---|
| `PRINT RND(1)` → `.973136996` | Exact digits reproduced by typing into the ][+ ROM with AppleWin's and MAME's power-on RAM patterns; requires `$CD` ∈ {`$FE`,`$FF`} (§1 Target 1) | **CORRECT** | Optional footnote: "4 bytes from ROM + 1 byte of power-on RAM" |
| Notes: "The amber box is the part that has to land. Slide 4 depends on it." | No amber box on slide 2; the note duplicates slide 3's | n/a (misplaced) | Keep on slide 3 only |

### Slide 3: what an RNG is

| Claim | Verified source says | Verdict | Corrected text |
|---|---|---|---|
| "Pseudo-random … The answer becomes the next starting number." | True of Applesoft: the result is stored to `$C9` and returned (a). Integer BASIC returns (state) MOD N and advances the state 17 LFSR steps (a) | **CORRECT** for Applesoft | |
| "Entropy is the key to sufficient randomness and unpatterned results." | Entropy sets the starting point. It doesn't prevent patterns: Applesoft loops from any seed (E) | **WRONG** (conflates the two) | "Entropy makes the starting point unpredictable." |

### Slide 4: "Integer BASIC, 1977"

| Claim | Verified source says | Verdict | Corrected text |
|---|---|---|---|
| "Woz wrote a generator at $EF4E" | `EF4E: 20 15 E7 RND JSR GET16BIT` (a, 2 dumps) | **CORRECT** | |
| "Known period with limited range" | Period 32,767 (15-bit LFSR) between key waits; returns 0..N−1; `RND(0)` → `>32767 ERR` (E) | **CORRECT** | "Period 32,767; 0 to N−1" |
| "No Floating point" | 16-bit integer `MOD` (a) | **CORRECT** | |
| "Sufficiently random" | Subjective | **UNVERIFIABLE** | |
| "counter at $4E and $4F that goes up while the monitor sits waiting for a keypress. Integer BASIC reads it." | `FD1B INC RNDL` / `FD1F INC RNDH` in the wait loop; `EF51 LDA $4E`, `EF56 LDA $4F`; RND also writes it back (a) | **CORRECT** | "…Integer BASIC uses it as its generator state." |
| "Sander-Cederlof, Apple Assembly Line, August 1981." | Citation; Review A confirmed it (txbobsc `aal8108`, which calls `$EF51`) | **UNVERIFIABLE** here | |
| Notes: "$4E/$4F is not a jiffy clock … no timer doing this." | Only the KEYIN loop and Integer BASIC RND write it; frozen otherwise (a) | **CORRECT** | |

### Slide 5: "Built-in Entropy Source"

Captions were paired with images by their positions in `slide5.xml`.

| Claim | Verified source says | Verdict | Corrected text |
|---|---|---|---|
| Image (OrigF8ROM): `fd1b: e6 4e KEYIN inc RNDL` … `fd2e: 60 rts` | 9 of 9 lines byte-identical to `Apple2.rom` (a) | **CORRECT** | |
| Image (AutoF8ROM): same loop, `KBD` labels | Byte-identical to `Apple2_Plus.rom` and `fpbasic.ts` (a) | **CORRECT** | |
| Image "Integer BASIC, at $EF4E": `ef4e` … `ef7d: 4c 7a e2 jmp MOD` | 24 of 24 lines byte-identical to both dumps (a) | **CORRECT** | |
| Image (IIc_16kb): `cc71: e6 4e inc RNDL`, `cc73: d0 1c bne UD2`, `cc75: a5 4f lda RNDH` (cropped) | No //c dump available; pattern absent from every //e, ][+ and II image. The enhanced //e has the same shape at `$C27D` with a different offset (a) | **UNVERIFIABLE** | Re-crop cleanly |
| Image (Unenh_IIe_80col): `cb15: e6 4e GETKEY inc MON_RNDL` … `cb23: 60 rts` | All 15 bytes at `$CB15` in AppleWin `Apple2e.rom` and apple2js `apple2e.ts` (a) | **CORRECT** | |
| "Present in some form in all Apple II ROMs" | Confirmed in ROM bytes for the II, ][+, unenhanced //e and enhanced //e; //c via screenshot only; IIc Plus and IIgs unchecked | **UNVERIFIABLE** ("all") | "In the II, ][+ and //e ROMs, and the //c firmware" |
| Notes: "Point at the **bne** going back to KEYIN." | `FD1D: D0 02 BNE` branches *forward* past `INC RNDH`. The branch back is **`FD24: 10 F5 BPL KEYIN`** (a) | **WRONG** | "Point at the BPL at $FD24 going back to KEYIN." |
| Notes: "The counter gets bumped before the keyboard is read, every pass. It's a loop count, not a keystroke count." | `INC` at `$FD1B` precedes `BIT KBD` at `$FD21` on every pass (a) | **CORRECT** | |
| Notes: "Sit there two seconds and it's gone round tens of thousands of times." | ≈68,000 counts/s (c), so two seconds ≈ **136,000 counts**, and the 16-bit counter **wraps about twice** | **WRONG** | "Two seconds is about 136,000 counts; the 16-bit counter wraps twice." |
| Notes: "the second thing Integer BASIC's RND does is read $4E" | `JSR GET16BIT`, then `LDA $4E` (a) | **CORRECT** | |
| Notes: "The disassembly is Paul Santa-Maria's work, converted by Andy McFadden." | Matches `IntegerBASIC.html` attribution | **CORRECT** | |
| Notes: "Woz wrote Integer BASIC with no assembler … hand-written pages in a binder" | Historical; nothing in the code bears on it | **UNVERIFIABLE** here | Cite a source |

### Slide 6: "Applesoft, 1978"

| Claim | Verified source says | Verdict | Corrected text |
|---|---|---|---|
| "Applesoft, 1978" over a listing at `$EFAE` | `$EFAE` is Applesoft II **in the ][+ ROM** (1979; identical in the //e ROMs). The algorithm and constants are in Microsoft's 1978 source (a) | **WRONG** (the date and the address belong to different artifacts) | "Applesoft II (1978 code), ][+ ROM" |
| "Applesoft relies on different seed. However, the seed for Integer BASIC remains." | `RND` never touches `$4E/$4F`; Autostart KEYIN still counts (a)+(E) | **CORRECT** | |
| "Takes the seed at $C9, multiplies, adds, swaps two bytes around, forces the result under 1, writes it back to $C9." | Seed `$C9–$CD`; × 11879546.40625 (constant missing a byte); add of 3.93×10⁻⁸ almost always lost; swaps FAC+1 ↔ FAC+4; exponent `$80`; normalize, round, store (a)+(E) | **CORRECT** (simplified) | |
| Image `efae: 20 82 eb` … `efe7: 4c 2b eb` (28 lines) | All 28 lines byte-identical to both ][+ dumps (a) | **CORRECT** | Credit: "S-C DocuMentor (Sander-Cederlof) via 6502disassembly.com (McFadden)" |
| Image comments "very poor RND algorithm", "this does nothing, due to small exponent" | S-C's annotations, not Microsoft's. "Does nothing" is nearly true: the sequence without the add diverges at call 3,886 (E) | **CORRECT** as S-C quotes | Attribute them |
| Notes: "This is the whole thing. **Twenty-six** instructions." | **28** (Target 4) | **WRONG** | "Twenty-eight instructions, plus about 900 in the FP routines it calls." |
| Notes: "the seed comes from $C9, which got a fixed value out of ROM at boot" | 4 of 5 bytes; `$CD` is power-on RAM (Target 5) | **WRONG** (partly) | "…four fixed bytes from ROM and one byte of leftover RAM." |
| Notes: "the answer goes back to $C9. Nothing else feeds it." | Only COLD.START and `RND` write `$C9–$CD`; NEW/CLEAR/RUN don't (a)+(E). `RND(-n)` feeds in its argument | **CORRECT** | |
| Notes: "McFadden's disassembly at 6502disassembly.com" | McFadden's SourceGen conversion of S-C DocuMentor | **CORRECT** (incomplete) | Credit both |
| Alt text `/home/claude/rnd_listing.png` (also `keyin.png`, `intbasic_rnd.png` on slide 5) | Build paths leaked | n/a (hygiene) | Real descriptions |

### Slide 7: "Applesoft Manual, 1978"

| Claim | Verified source says | Verdict | Corrected text |
|---|---|---|---|
| "RND (aexpr) Returns a random real number ≥ 0 and < 1." | `RND(+)` outputs lie in (0,1): none ≥ 1 in 128,550 ROM outputs (E) | **CORRECT** | |
| "If aexpr > 0 … new random number each time" | Positive path; argument value ignored (a) | **CORRECT** | |
| "If aexpr < 0 … same random number … subsequent positive arguments follow the same sequence" | Argument bytes become the seed; same K, same sequence (E) | **CORRECT** | |
| "A different random sequence is initialized by each different negative argument." | K = 1..65,535 give 65,535 distinct seeds (E) | **CORRECT** | |
| "If aexpr is zero, returns the most recent previous random number generated (CLEAR and NEW do not affect this)." | `EFBC: BEQ RTS.19` returns the seed unchanged; NEW/CLEAR/RUN leave it (a)+(E) | **CORRECT** | |
| Date "1978" | The Aug 1978 *Applesoft II Reference Manual* (A2L0006X) has different RND wording ("X<=0 starts a new sequence…"); these scans are another edition | **UNVERIFIABLE** (probably a later edition) | Name the edition |
| Notes (copy of slide 6's, including "Twenty-six instructions") | Misplaced, and carries the Target 4 error | **WRONG** | Notes about the manual text |

### Slide 8: "Sources"

| Claim | Verified source says | Verdict | Corrected text |
|---|---|---|---|
| "Kaner & Vokey, 1982. First published account." | Manuscript © 1982, **published *MICRO* June 1984** (LITERATURE [A3], C8). Sparks, *Call-A.P.P.L.E.* Jan 1983, was in print first | **WRONG** ("first published") | "Kaner & Vokey, MICRO, June 1984 (written 1982)" |
| "Call A.P.P.L.E., Jan 1983, 'RND is Fatally Flawed.'" | Sparks, D., *Call-A.P.P.L.E.* 6, pp. 29–34 | **CORRECT** | Add author and pages |
| "Sander-Cederlof, AAL May 1984. Found the startup bug. The seed copy is off by one." | Loop count `$1C` copies 28 of 29 bytes; `$F127` never reaches `$CD`; bug inherited from Microsoft line 6733 (Target 5) | **CORRECT** | Precise wording in Target 5 |
| "Aldridge 1987, Gleason 1988 … ERIC EJ372427" / "Empson, GS WorldView 1999" | Citations, outside the code | **UNVERIFIABLE** here | See `research/LITERATURE.md` |
| Notes: "The 202 figure is measured, from the paper, on real Applesoft." | No slide shows 202. The figure is real: Kaner & Vokey report a loop "repeating itself every 202 numbers", and on the ROM `$CD=$58` enters a 202-loop after 15,382 calls; 23% of `$CD` values reach it (E) | **CORRECT** (orphaned) | Put it on the slide or cut the note |

### Slide 9: "Two Part Solution"

| Claim | Verified source says | Verdict | Corrected text |
|---|---|---|---|
| "Enables language card write mode while keeping ROM readable" | Loader not available | **UNVERIFIABLE** | Name the switches (e.g. `$C081` ×2) |
| "Copies $D000-$FFFF (all of Applesoft and the monitor ROM)" | ][+ image: Applesoft `$D000–$F7FF`, monitor `$F800–$FFFF` (a) | **CORRECT** (][+ / //e) | |
| "Writes the patch code into the LC at $F5CB (may impact HFIND, supposedly unused by AppleSoft.)" | Unused by Applesoft: S-C, McFadden and an independent ROM scan agree. 53 bytes available; `$F600` RTS shared with HLIN; DRAW at `$F601` (Target 6) | **CORRECT**. The hedge is unnecessary; the size limit is the real risk | Target 6 corrected text |
| "Writes JMP $F5CB at $EFAE in the LC copy" | `$EFAE` = RND entry (`$D092` = `AE EF`); JMP replaces `JSR SIGN` exactly (a) | **CORRECT** | |
| "1. Preserves negative and zero RND() functionality while relying on the KEYIN counter present in the ROM." | Patch binary not available; required behaviour listed in Target 6 | **UNVERIFIABLE** | Show the patch listing |
| "Two Part Solution" with only item "1." | | n/a (hygiene) | Number both parts |

### Slide 10: "Try it yourself"

| Claim | Verified source says | Verdict | Corrected text |
|---|---|---|---|
| Notes: "does the C64 have this too (yes, same Microsoft code, but Commodore wired RND(0) to hardware timers and gave people TI)" | Microsoft source: the Commodore build's `RND(0)` loads VIA timer bytes (`CQHTIM`, lines 6357–6370); Apple's doesn't (a). The C64 ROM itself was not examined | **CORRECT** (PET path); C64 specifics unverified | |
| Notes: "Why not replace the generator (speed, no space, and RND(-n) has to keep working)" | `RND(1)` ≈ 953 instructions ≈ 3 ms (E); patch site 53 bytes (a) | **CORRECT** | |
| Notes: "What's at $F5CB (HFIND, answer it straight)" | HFIND; unused by Applesoft (Target 6) | **CORRECT** | |

---

## 4. Tally and priorities

Counted by each row's leading verdict in §3: **36 CORRECT, 8 WRONG, 9 UNVERIFIABLE, 3 n/a**
(56 rows).

**Fix before presenting:**
1. **Slide 6 notes** (and the copy in slide 7's): "Twenty-six" → 28; "fixed value out of ROM" →
   four bytes plus one byte of leftover RAM.
2. **Slide 2 / slide 1 demo:** power-cycle, don't Ctrl-RESET; rehearse on the stage machine.
   Optional `PRINT PEEK(205)` reveal.
3. **Slide 9:** drop "supposedly"; state the ≤ 53-byte limit and that `$F600` is left intact;
   bring the patch listing.
4. **Slide 5 notes:** BPL at `$FD24`, not BNE; two seconds ≈ 136,000 counts.
5. **Slide 6 header:** "1978" vs the ][+ ROM address.
6. **Slide 8:** "first published" (Kaner & Vokey published 1984); the orphaned 202 note.
7. **Slide 3:** entropy sets the start, not the pattern.

**Open:** real-hardware power-on value of `$CD`; //e reset path and DOS 3.3 boot effects on
`$C9–$CD`; `Patch_lc.bin`/`LC_Loader.bin` contents; external callers of HFIND; //c bytes at
`$CC71`; the edition of the manual on slide 7.

---

## Appendix A: output distribution (context for "uniform")

The deck does not claim bias, but the audience may ask. Die faces `INT(RND(1)*6)+1`, computed
by the ROM's own `RND` → `FMULT` → `INT`, pass χ² for single faces, consecutive pairs and
triples over every long cycle. For the `.973136996` machine's 37,758-number loop: faces
6377 6211 6228 6314 6285 6343, χ² 3.34, p=0.65; pairs p=0.76; triples p=0.31. The ROM face
never differed from exact ⌊6x⌋+1 in 128,550 outputs. Two genuinely lopsided cases are
misuse or loop artefacts, not weighting:
* Inside the 202-number loop, face 4 appears 22.3% of the time (p=0.10).
* `INT(RND(-K)*6)+1` = 1 for all K from 1 to 65,535, because `RND(-K)` returns ≈3×10⁻⁸.

## Reproduce

```sh
cd source/tools
../../.venv/bin/python verify.py                                  # listings + demos
../../.venv/bin/python deck_audit.py rom emuram hfind              # targets 1–6, seconds
../../.venv/bin/python deck_audit.py negsweep cycle-cdff cycle-neg2 cycle-cd58   # appendix, ~4 min
```

External sources fetched 2026-09-12:
* AppleWin `source/Core.cpp`, `source/Memory.cpp` (master)
* MAME `src/mame/apple/apple2.cpp` (master)
* S-C DocuMentor `F5BA.html` and `symboltable.html` (txbobsc.com)
* McFadden `a2-rom/Applesoft.html`
* AppleWin `Apple2e.rom` / `Apple2e_Enhanced.rom` and apple2js `apple2e.ts`
