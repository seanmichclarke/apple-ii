# PROVENANCE — source/ listings and demos

Compiled 2026-09-12 by the source-code agent. The evidence has three layers, in
decreasing order of authority:

1. **ROM bytes.** Two independently hosted dumps per ROM. Every listing line in this
   directory is machine-checked against them (`tools/verify.py`: 402 line/ROM
   comparisons, 0 mismatches).
2. **Execution.** The same ROM bytes run on a py65 NMOS 6502 core (`tools/harness.py`).
   Every behavioural number in `applesoft-rnd.md` §5 and `integer-basic-rnd.md` §3 was
   re-derived by `tools/experiments.py`. Every demo output in `demos.md` was re-typed and
   diffed by `tools/verify.py` (all match).
3. **Published listings and manuals.** These supply labels, comments and Apple's or
   Microsoft's stated intent.

## Listing status summary

| Listing | Label | Bytes agree in | Text/labels reconciled against | Confidence |
|---|---|---|---|---|
| Applesoft `RND` $EFA6–$EFE9 | **verified-against-4-sources** | 2 ROM dumps (+ identical in //e, enhanced //e images) | S-C DocuMentor; Microsoft `m6502.asm` (independent); McFadden and Davis (derivative, agree) | **High** |
| Applesoft FP helpers (SIGN, LOAD/STORE, NORMALIZE, ROUND) | **verified-against-3-sources** | 2 ROM dumps | S-C / McFadden (one lineage); Microsoft source for structure | **High** (bytes); labels high |
| Cold-start seed copy $F123, $F150 | **verified-against-4-sources** | 2 ROM dumps | S-C, McFadden, Davis all flag the bug; Microsoft source line 6733 has it; ROM-image seed table lines 6694–6698 | **High** |
| Monitor `RDKEY`/`KEYIN` $FD0C–$FD2E | **verified-against-5-sources** | AppleWin original + Autostart; apple2js II+ | Red Book 1978 listing (primary); 1979 Reference Manual listing and prose (primary); McFadden OrigF8ROM / AutoF8ROM | **High** |
| Integer BASIC `RND` $EF4E–$EF7F | **verified-against-2-dumps + 1 disassembly + emulation** | 2 ROM dumps ($E000–$F7FF identical) | Santa-Maria disassembly (via McFadden) only | **High** for bytes and behaviour; **medium** for label names (single source) |
| Demo programs | **verified by emulation** | — | typed into emulated II+ / II; output diffed | **High** in emulation; **not yet run on real hardware** |

Nothing in `source/` is marked *reconstructed*. Every byte shown was matched against ROM.

## Sources

### ROM images (byte authority)

| Name | URL | SHA-1 | Covers |
|---|---|---|---|
| AppleWin `Apple2_Plus.rom` | github.com/AppleWin/AppleWin `resource/Apple2_Plus.rom` | `33a24f5489ba9195b44be77d9afb2252594cb5c7` | $D000–$FFFF: Applesoft II + Autostart monitor (RESET vector `$FA62`) |
| AppleWin `Apple2.rom` | github.com/AppleWin/AppleWin `resource/Apple2.rom` | `09288be705464b608ff190519ab008d3dfcd1b05` | $D000–$FFFF: Integer BASIC + original monitor (RESET `$FF59`) |
| apple2js `fpbasic.ts` | github.com/whscullin/apple2js `js/roms/system/fpbasic.ts` | `550cee76329992c5618c1127a541aed145897c84` | identical to AppleWin II+ except `$FFFE-$FFFF` (IRQ vector) |
| apple2js `intbasic.ts` | same repo, `intbasic.ts` | `1da559310c4a1ebd71bff406569a00640e2abfad` | identical to AppleWin `Apple2.rom` over $E000–$F7FF; its $F800 page differs (289 bytes; KEYIN bytes still identical) |
| apple2js `apple2e.ts`, `apple2enh.ts` | same repo | `cdbca4e0023e72c888ca24d02a19586eeea4c250` (IIe) | Applesoft RND block, seed, copy loop and FP core $E7BE–$EB52 byte-identical at the same addresses; **KEYIN differs** |

Independence: two separate emulator projects with separate histories. Both may trace
back to the same physical ROM revision, which is the point. Neither is a disassembly
reassembled.

### Disassemblies and source

| Source | URL | Role | Independence |
|---|---|---|---|
| **S-C DocuMentor: Applesoft** (Bob Sander-Cederlof) | txbobsc.com/scsc/scdocumentor/ `S.EE8D` (RND), `S.EFEA` (CHRGET, seed, COLD.START), `definitions.html` | primary annotated disassembly; source of label names and the `<<< >>>` critical comments | root of the Applesoft-listing lineage |
| **McFadden, Applesoft.html** | 6502disassembly.com/a2-rom/Applesoft.html | SourceGen port of S-C with cross-reference | **derivative of S-C**. Agrees; its cross-reference was used for "no `$4E/$4F` refs" |
| **James Davis, APPLE2.ROM.html** | 6502disassembly.com/a2-rom/APPLE2.ROM.html | full II+ ROM disassembly | built with SourceGen; comments partly track S-C. **Partially independent.** Agrees at $EFA6, $EFAE, $EFCC, $EFE7, $F123, $F150, $FD1B |
| **Microsoft `m6502.asm`** | github.com/microsoft/BASIC-M6502, historical commit `eb3a53cd` (git date 1978-07-27; repo touched 2025-09-03). SHA-1 of file `e1ec8e5d…12af0` | original "BASIC M6502 8K VER 1.1" source with `REALIO=4` (Apple) | **fully independent** of all disassemblies. It is not byte-identical to Applesoft II ROM, but RND logic, constants and the seed-copy bug match |
| mist64 `msbasic` `rnd.s` | github.com/mist64/msbasic | reassemblable MS BASIC family | **derivative** (README: comments from S-C; "cannot (yet) build AppleSoft II"). Only corroborates the constants |
| **Santa-Maria / McFadden, IntegerBASIC.html** | 6502disassembly.com/a2-rom/IntegerBASIC.html | only Integer BASIC disassembly used | single source for Integer BASIC labels |
| McFadden OrigF8ROM / AutoF8ROM / Unenh_IIe_F8ROM | 6502disassembly.com/a2-rom/ | monitor listings ("ported" from Apple's published listings) | derivative of Apple's printed listings |

Microsoft source line references used in the deliverables (file as fetched above):
`RADIX 10` at line 4 and `RADIX 8` at line 4847 (the math package is octal);
`RNDX` RAM seed at lines 978–982 (`128,79,199,82,89`); RND comment block at 6329–6340;
`RMULZC` at 6344–6347 and `RADDZC` at 6348–6351 (octal); `RND` at 6353; Commodore
`CQHTIM` timer path at 6357–6370; `RND1` byte swap at 6381; `RADIX 10` at 6671; ROM-image
seed table at 6694–6698 (`128,79,199,82,<88>`); `LDXI RNDX+4-CHRGET` at 6733.

### Apple manuals (archive.org scans, OCR)

| Document | archive.org id | Used for | Location |
|---|---|---|---|
| *Apple II Reference Manual*, Jan 1978 ("Red Book") | `Apple_II_Reference_Manual_1978-01_Apple` | monitor listing of KEYIN with Woz/Baum comments; `RNDL EPZ $4E`; Integer BASIC RND summary | KEYIN listing at scan leaf 89 (archive full-text search). Printed page number not confirmed |
| *Apple II Reference Manual* (1979, II and II Plus) | `apple-ii-ref-manual` | "Random Number Seeding" prose; `$FD1B KEYIN` entry; listings | printed p. 32 (leaves 41–42); KEYIN entry leaf 71; listing leaves 157/174 |
| *Applesoft II Reference Manual*, Aug 1978 (A2L0006X) | `Applesoft_II_Reference_Manual_1978-08_Apple` | documented `RND(X)` semantics | RND entry. Quote: "X<=0 starts a new sequence of random numbers using X. Calling RND with the same X starts the same random number sequence. X>0 generates a new random number between [0] and 1." |

OCR drops digits and characters (e.g. "between and 1"). Bracketed insertions are mine.
Check the scan image before putting a quote on a slide.

## Method notes (emulation)

* `tools/harness.py`: py65 (PyPI `py65`) NMOS 6502 core, 64K memory, ROM at $D000.
  Writes ≥ $C000 are ignored, and I/O reads return 0.
* **Trap at `$FD1B` KEYIN.** Instead of spinning the wait loop, it adds a chosen
  count (default 1) to `$4E/$4F`, restores the screen character, and returns the next
  queued key. This models the loop's only side effects. It does not model real
  keyboard/strobe timing.
* **Log at `$FDF0` COUT1**, after which the real ROM code runs.
* **Boot.** RAM is zero-filled unless stated. The II+ path runs through the Autostart
  RESET into Applesoft `COLD.START` (no disk controller, so no DOS). The II path goes
  through the original monitor, then Ctrl-B into Integer BASIC.
* py65's `processorCycles` includes branch-taken and page-cross extras. Cycle figures
  are emulator counts, not oscilloscope measurements.
* Integer BASIC behaviour was cross-checked with an independent Python model of the
  listing: 300 of 300 consecutive `RND(32767)` values matched the ROM.

## Discrepancies found (report these; don't resolve them silently)

1. **S-C: "THIS DOES NOTHING" (the `FADD` of `CON.RND.2`).** Emulation says the addend
   changes the stored seed in 5 of 57,021 steps, and removing it makes the sequence
   diverge at call 3,886. Nearly true, but not literally.
2. **Applesoft II manual vs ROM on `RND(0)`.** The manual says X<=0 starts a new
   sequence. The ROM (and Microsoft's own source comment) returns the last value without
   reseeding. The manual is wrong for X=0.
3. **Seed byte `$58` vs `$59`.** Microsoft's RAM-load seed table has 89 (`$59`), and its
   ROM-image table has 88 (`$58`). The Apple ROM has `$58`. Moot anyway, because the byte
   is never copied.
4. **"Floating-point LCG" (BRIEF thesis item 1).** The code is multiply + (nearly
   ineffective) add + MSB/LSB byte swap + renormalize. There is no modulus, so it is not a
   textbook LCG. LCG lattice/spectral theory does not apply directly. **Research and
   slide agents: don't show an LCG modulus, a "period 2³²", or an LCG spectral figure
   for Applesoft RND without deriving it for this map.** Observed cycles are 37,758 and
   32,366 (6 seeds tested, not exhaustive).
5. **"Low-order-bit correlation" (BRIEF item 1).** Not supported by these data for the
   leading digits: serial-pair χ² is normal at N ≤ 256 over 57k outputs. What *is*
   demonstrable is a **stuck bit**, fraction bit 25 ≈ 99.75% ones. Recommend rewording
   the slide to "stuck low-order bit" and "short cycles".
6. **"Every machine reproduces the same sequence after reset" (BRIEF item 3).** Needs
   qualifying. Cold start copies only 4 of 5 seed bytes, and `$CD` is leftover RAM (181
   distinct sequences across its 256 values). Ctrl-RESET does not reseed at all. The claim
   holds per power-on RAM state. Real-hardware power-on contents of `$CD` are
   **unknown**.
7. **$4E/$4F and Applesoft.** Applesoft `RND` never reads the counter. Only Integer BASIC
   `RND` uses it automatically. The BRIEF's item 2 is accurate only if framed as
   "available to programs", or as Integer BASIC's mechanism.

## Not verified / out of scope

* Real Apple II hardware, and emulators other than py65 running AppleWin/apple2js ROM
  images.
* DOS 3.3 / ProDOS effects on `$C9-$CD` or `$4E/$4F` (DOS was not loaded).
* Apple //c ROMs. //e `KEYIN` (different code at `$FD1B`).
* Power-on DRAM contents, i.e. the real distribution of `$CD` and `$4E/$4F`.
* Exact CPU clock rate (≈1.02 MHz is the commonly cited effective rate; timing figures in
  `keyboard-seed.md` are labelled inference).
* Printed page numbers in the 1978 Red Book (only the scan leaf is known).
* How common the `RND(-PEEK(78)…)` idiom was in period software. There is no citation
  here, so treat it as unestablished.

## Reproducing

```sh
python3 -m venv venv && venv/bin/pip install py65
cd source/tools
../../venv/bin/python verify.py            # listings + demos, ~1 min, exit 0 = all match
../../venv/bin/python experiments.py sweep cost resets bits intbasic   # ~1 min
../../venv/bin/python experiments.py fadd  # ~2.5 min
../../venv/bin/python experiments.py cycles  # ~3.5 min
```

Results on 2026-09-12: all experiment outputs matched the numbers in the deliverables.
Verify: listings 402 comparisons / 0 mismatches; demos all OK after correcting one
expected-output line in Demo 3, which had been written before it was run.
