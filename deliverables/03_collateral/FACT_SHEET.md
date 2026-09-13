# Fact sheet: what the talk can safely say

Every number on either deck is listed here, with its source and how it was checked.

**Evidence labels**
- **(a)** Documented: ROM bytes, a primary listing, the manual, or the paper.
- **(E)** Measured by running the genuine ROM code in a 6502 emulator. Reproducible, but not published anywhere.
- **(c)** Inference or arithmetic.

**Re-verified on 2026-09-12** by running `tools/verify_headline_numbers.py` against AppleWin's `Apple2_Plus.rom` (SHA-1 `33a24f5489ba9195b44be77d9afb2252594cb5c7`). The output is in `evidence/verify_headline_numbers.log`.

---

## The seed

| Claim | Value | Label | Source |
|---|---|---|---|
| Seed storage | 5 bytes at `$C9–$CD` | (a) | S-C DocuMentor; AAL May 1984 |
| Seed table in ROM | `$F123: 80 4F C7 52 58` (≈ .811635157) | (a) | ROM bytes |
| Cold-start copy loop | `$F150: A2 1C` (`LDX #$1C`) copies `$F10B–$F126` → `$B1–$CC` | (a) | ROM bytes |
| The bug | The fifth seed byte is never copied, so `$CD` keeps whatever RAM held | (a) | S-C DocuMentor; AAL May 1984; Microsoft source `LDXI RNDX+4-CHRGET` |
| Published one-byte fix | `$F151`: `$1C` → `$1D` | (a) | AAL May 1984 |
| Bug origin | Microsoft's source, not Apple's port. Apple inserted `STX SPEEDZ` inside that same loop and kept the short count | (a) | m6502.asm; ROM `$F157` |
| First `RND(1)`, `$CD=$FF` or `$FE` | **.973136996** | (E) | re-verified |
| First `RND(1)`, `$CD=$00` | .270011996 | (E) | re-verified |
| First `RND(1)`, `$CD=$58` (the value Microsoft intended) | .512199496 | (E) | re-verified |
| Distinct first values across all 256 `$CD` values | 181 | (E) | re-verified |
| What `$CD` actually holds at power-on on real DRAM | **Unknown** | — | Open item A1 |
| Ctrl-RESET | Leaves the seed untouched (Autostart warm start) | (E) | `source/applesoft-rnd.md` §5.1 |
| Only power-on repeats; rerun or reboot looks random | Aldridge: "It is only when a machine is powered off and back on that the sequence begins repeating itself." | (a) | Aldridge 1987 |

## The generator (Microsoft's, in Applesoft)

| Claim | Value | Label | Source |
|---|---|---|---|
| Entry point | `RND` at `$EFAE`; routine `$EFAE–$EFE7`, 28 instructions | (a) | ROM; listing |
| Author | Microsoft 6502 BASIC. The port is credited to Weiland & Gates. Do not name the author of the generator itself | (a) | m6502.asm; Microsoft 2025 |
| Constants | `98 35 44 7A` and `68 28 B1 46`: 4 bytes each, but read as 5 | (a) | ROM; S-C "MISSING ONE BYTE" |
| Multiplier as actually executed | 11,879,546.40625 (stray fifth byte `$68`) | (a)+(c) | `source/applesoft-rnd.md` §2 |
| Addend | 3.93×10⁻⁸. Lost to precision: it changes the stored seed in 5 of 57,021 steps. Say "effectively nothing," not "nothing" | (E) | §5.4 |
| The swap | `FAC+1` ↔ `FAC+4`, highest and lowest mantissa bytes. AAL's "middle two bytes" is wrong | (a) | ROM; Microsoft source "REVERSE HO AND LO" |
| Listing comments | "very poor RND algorithm", "this does nothing", "to supposedly make it more random" are **Sander-Cederlof's** annotations, not Microsoft's | (a) | S-C DocuMentor |
| Is it an LCG? | Not a textbook one: no modulus, plus a byte swap and renormalize. LCG lattice theory does not transfer to it | (a)+(c) | `research/LITERATURE.md` C10 |
| Stuck bit | Fraction bit 25 is set in 99.75% of outputs | (E) | §5.3 |
| Leading digits | Pass uniformity χ² and serial-pair χ² tests at N up to 256. **Don't** claim they look patterned | (E) | §5.3 |
| `RND(-1)` | Prints 2.99196472E-08 | (E) | re-verified |
| `RND(0)` | Returns the last value; seed untouched | (a) | code; manual |
| Never reads `$4E/$4F` | No reference anywhere in Applesoft | (a) | McFadden cross-reference; Aldridge |
| Same bytes in II Plus, IIe, enhanced IIe | `$EFA6–$EFE9`, `$F123`, `$F150` byte-identical. The //c and IIgs were not checked | (a) | ROM comparison |

## Loops

| Claim | Value | Label | Source |
|---|---|---|---|
| Kaner & Vokey | "between the 10,000th and the 20,000th number generated, RND fell into an endless loop, repeating itself every 202 numbers" | (a) | MICRO June 1984 (written 1982) |
| Sander-Cederlof | "the repetition starts at the 37,758th 'random' number" | (a) | AAL May 1984 |
| Same generator, different `$CD` | `$FF` → 37,758-loop after 6,818 calls. `$58` → **202-loop after 15,382 calls** | (E) | re-verified (the `$58` case) |
| All 256 cold starts | 43.0% → 37,758 · 30.5% → 32,366 · 23.0% → 202 · 2.0% → 4,082 · 1.6% → 12,559 | (E) | `tools/cd_sweep_results.jsonl`. The four 12,559 results were not checked to be the same loop |
| Reseeding doesn't escape | `RND(-52894)` and `RND(-22258)` both reach the 202-loop | (E) | `evidence/` |

## The counter and Integer BASIC

| Claim | Value | Label | Source |
|---|---|---|---|
| KEYIN | `$FD1B: E6 4E D0 02 E6 4F` (`INC RNDL / BNE / INC RNDH`) | (a) | ROM; Red Book |
| Apple documents it | "…the exact value of which is quite unpredictable. Many programs and languages use this number as the base of a random number" | (a) | Apple II Reference Manual p. 32 |
| Rate | 15 CPU cycles per loop → ≈68,000 counts/s → wraps every ≈0.96 s (II Plus loop; IIe/IIc loops differ) | (c) | cycle arithmetic; Aldridge: "less than a second" |
| Only moves in a key wait | Programs polling `$C000` directly never advance it | (a)+(b) | code; Applefritter |
| Integer BASIC `RND` | `$EF4E`, 50 bytes. The state **is** `$4E/$4F` | (a) | Santa-Maria disassembly |
| Integer BASIC period | 32,767 (15-bit maximal LFSR, feedback bit14 XOR bit13) | (E) | re-verified `intbasic_rnd_emu.py` |
| Output | `RND(X)` = state `MOD X` | (a) | `JMP MOD` at `$EF7D` |
| Counter shown in | Original F8, Autostart F8, unenhanced IIe 80-col (`$CB15`), IIc 16K (`$CC71`). Say "all" only after checking the enhanced IIe, later IIc and IIgs | (a) | disassemblies |

## HFIND and the patch location

| Claim | Value | Label | Source |
|---|---|---|---|
| HFIND | `$F5CB–$F5FF`, 53 bytes. "(not called by any Applesoft routine)" | (a) | S-C DocuMentor |
| Callers in ROM | No `JSR` or `JMP` to `$F5CB` anywhere in `$D000–$FFFF` | (a) | re-verified by byte search |
| `$F600` | `RTS`, reached from HLIN (`BEQ` at `$F59C`). **Must not be overwritten** | (a) | re-verified |
| Residual risk | A user program doing `CALL 62923` | (c) | — |

## The damage

| Claim | Label | Source |
|---|---|---|
| A memory experiment gave repeated "individually randomized" word lists to each day's first subject, tested right after power-on | (a) | Aldridge 1987 |
| Apple's advice to that lab: `X=RND(-1*(PEEK(78)+256*PEEK(79)))` "after keyboard input but before the first use of RND" | (a) | Aldridge 1987 |
| Games that shipped broken because of it | **No verified example.** Don't name one | — |

## Commodore

| Claim | Label | Source |
|---|---|---|
| The C64 has the same generator and constants (stored as 5 bytes with a trailing `$00`) | (a) | c64ref disassembly |
| Timer-seeded `RND(0)` and `TI` were written into **Microsoft's** source for Commodore and shipped in the first PET ROM (1977). Credit Microsoft-for-Commodore, not Commodore alone | (a) | m6502.asm `IFE REALIO-3`; Steil msbasic |

## "Now" (parallel only, not lineage)

| Claim | Label | Source |
|---|---|---|
| Debian OpenSSL, CVE-2008-0166: a 2006 Debian change removed almost all entropy mixing from OpenSSL's PRNG, so keys were predictable until the 2008 disclosure | (a) | Debian Security Advisory DSA-1571-1 (May 2008) |
| C `rand()` without `srand()` behaves as if seeded with 1 | (a) | ISO C standard, `rand` |

---

## Don't say / say instead

| Don't say | Say |
|---|---|
| "Every Apple II prints .973136996" | "This machine prints the same number every power-on" |
| "a fixed seed from ROM" (unqualified) | "four of the five seed bytes come from ROM; the fifth is leftover RAM" |
| "reboot and you get the same number" | "power-cycle and you get the same number" |
| "Woz's LCG" / "Apple's RNG" | "Microsoft's generator, in Applesoft" |
| "the addend does nothing" | "the addend is lost to precision" |
| "swaps the middle two bytes" | "swaps the highest and lowest bytes" |
| "the period of RND is …" | "it falls into one of several loops: 202, 37,758 …" |
| "sufficiently random" | "period 32,767: fine for games, not for statistics" |
| "may impact HFIND, supposedly unused" | "overwrites HFIND, which no Applesoft routine calls" |
| "present in all Apple II ROMs" | "in the II, II Plus, IIe and IIc ROMs shown" |
| "Commodore wired RND(0) to timers" | "Microsoft's Commodore build read the timers" |
| "first published account" (Kaner & Vokey) | "written 1982, published 1984" |
