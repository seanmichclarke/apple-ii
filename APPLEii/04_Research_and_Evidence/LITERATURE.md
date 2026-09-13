# The Problem of the Apple II RNG — Literature & Research Record

Research agent output, compiled 2026-09-12. Scope and evidence rules follow `../BRIEF.md`.

## How to read this file

Every claim carries one label:

- **(a) documented fact**: stated in a primary source I fetched and read (ROM bytes, source code, Apple/Microsoft manuals, the original paper or article).
- **(b) community consensus**: stated by secondary or community sources I fetched, without a primary document I could check.
- **(c) inference**: my own reasoning or arithmetic. **(c-emu)** marks a result I computed by running the real Applesoft ROM code in a 6502 emulator (`tools/rnd_emu.py`, `tools/rnd_experiments.py`). Anyone can re-run it, but no published source backs it up.

Sources are cited as bracketed IDs such as [A3] or [O1], defined in §1. A source in §1.5 ("cited but not fetched") never counts as verification for any claim.

**One point for the deck team up front (c):** the literature does **not** contain a spectral or lattice analysis of Applesoft `RND` itself. Applesoft `RND` is not a textbook LCG. It has no explicit modulus, it uses truncated floating-point constants, it swaps bytes, and it renormalizes. So Marsaglia's hyperplane theorem and Knuth's spectral test do not apply to it directly. The documented failures of this generator are short cycles, seeding, failed statistical tests, and a bad initialization. General LCG lattice theory can appear on a slide only as background, not as a measured property of Applesoft `RND`. See §3, C10.

---

## 1. Annotated bibliography

### 1.1 Academic

**[A1] Marsaglia, G. "Random Numbers Fall Mainly in the Planes." *PNAS* 61(1):25–28, Sept 1968.** doi:10.1073/pnas.61.1.25
URLs: https://pmc.ncbi.nlm.nih.gov/articles/PMC285899/ (fetched; metadata only, the article is page scans). Crossref metadata fetched via https://api.crossref.org/works/10.1073/pnas.61.1.25. https://www.pnas.org/doi/10.1073/pnas.61.1.25 returned 403.
This paper shows that n-tuples from a multiplicative congruential generator lie on a small number of parallel hyperplanes. **I could not read the primary text.** The bound below comes from [M10], a secondary source: all n-tuples lie in at most (n!·m)^(1/n) hyperplanes. Use this for background only.

**[A2] Knuth, D. E. *The Art of Computer Programming, Vol. 2: Seminumerical Algorithms*, ch. 3 (random numbers).** 1st ed. 1969, 2nd ed. 1981, 3rd ed. 1997 (ISBN 0-201-89684-2).
URL: https://www-cs-faculty.stanford.edu/~knuth/taocp.html (fetched; confirms the edition years and ISBN only).
I did not read the book itself. I know its content only through two period sources that cite it. [A3] reports Knuth's spectral-test thresholds ("pass" is ν > 0.10, "flying colors" is ν > 1.0) and his Algorithm S. [P1] reports Knuth's four rules for choosing a, c, and m, and his warning that "tweaking" a generator ruins it.

**[A3] Kaner, C. & Vokey, J. R. "A Better Random Number Generator for Apple's Floating Point BASIC."** Manuscript © 1982, published in *MICRO*, June 1984, pp. 26–35.
URL: https://kaner.com/pdfs/random.pdf (downloaded; full text read. The author has removed the assembly-language sections.)
This is the only published statistical test of Applesoft `RND` I could read. It says `RND` "fails [standard statistical tests] miserably." On the first batch of 10,000 numbers, `RND` failed only the triplets test. Then, "between the 10,000th and the 20,000th number generated, RND fell into an endless loop, repeating itself every 202 numbers." The paper also explains spectral-test selection of 40-bit LCG constants (Coveyou–MacPherson; Knuth's Algorithm S), with full ν₂…ν₆ tables. It is a good primary source for explaining lattice structure to the audience.

**[A4] Aldridge, J. W. "Cautions regarding random number generation on the Apple II."** *Behavior Research Methods, Instruments, & Computers* 19(4):397–399, July 1987. doi:10.3758/BF03202585
URLs: https://www.apple.asimov.net/documentation/programming/misc/random%20number%20generation%20note.pdf (downloaded; full text read). Crossref metadata fetched via https://api.crossref.org/works/10.3758/BF03202585.
This is the peer-reviewed source for the seeding problem.
- It describes the $4E/$4F KEYIN counter.
- It states that "Applesoft in fact makes no use of the $4E-$4F value."
- It says `RND` with positive arguments "generates exactly the same sequence each time the machine is powered on."
- It reports a real case: a psychology memory experiment whose "individually randomized" word lists repeated for the first subject tested each day.
- It gives the fix an Apple representative recommended: `X=RND(-1*(PEEK(78)+256*PEEK(79)))`.
- It quotes the Applesoft manual (pp. 102, 159) and documents a related Apple Pascal `RANDOMIZE`/`NOLOAD` failure.

**[A5] Gleason, J. M. "Statistical Tests of the Apple IIe Random Number Generator Yield Suggestions from Generator Seeding."** *Collegiate Microcomputer* 6(2):108–112, May 1988. ERIC EJ372427.
URL: https://eric.ed.gov/?id=EJ372427 (fetched; abstract only).
According to the abstract, the paper "discusses flaws in the Apple IIe Applesoft random number generator, RND, and reports results of frequency and serial correlation tests." It also suggests seeds that pass basic screening tests. **I have not read the paper or seen its numbers.**

**[A6] Brysbaert, M. "Algorithms for randomness in the behavioral sciences: A tutorial."** *BRMIC* 23(1):45–60, March 1991. doi:10.3758/BF03203334
URL: https://api.crossref.org/works/10.3758/BF03203334 (metadata fetched). The Springer article page redirected to a login.
It appeared in the same search results as [X1], and it may be the source of the [X1] summary quoted in §1.5. **I did not read the text, so I attribute nothing to it.**

### 1.2 Period literature (1983–1989)

**[P1] Sander-Cederlof, B. "Random Numbers for Applesoft." *Apple Assembly Line* 4(8), May 1984.**
URL: https://www.txbobsc.com/aal/1984/aal8405.html (downloaded; full text read).
This is the most technically specific period source. It names three flaws:
1. The initialization copies only four of the five seed bytes. The copy loop is at $F150, and changing $F151 from $1C to $1D fixes it.
2. The algorithm is poor and relies on a "tweak."
3. The four-byte constants mean the algorithm is implemented incorrectly.

It gives `RND` at $EFAE and the seed at $C9–CD. Its HGR dot-plot demo stops adding dots after "about seven minutes," and "the repetition starts at the 37,758th 'random' number." It notes that Integer BASIC uses the $4E/$4F seed. It also reprints the Call-A.P.P.L.E. replacement (a=8192, c=0, m=67099547) and offers a Knuth-style replacement (a=314159269, c=907633386, m=2³²) plus a 16-bit generator seeded from $4E/$4F (a=19125, c=13843, m=2¹⁶).

**[P2] Sander-Cederlof, B. "More Random Number Generators." *Apple Assembly Line* 4(9), June 1984.**
URL: https://www.txbobsc.com/aal/1984/aal8406.html (downloaded; full text read).
This article confirms that [A3] ran in *MICRO* in June 1984 and that the work was funded by NSERC. It lists the Kaner–Vokey constants and corrects a typo in the printed article: an additive constant printed as 24607 is really 26407 ($6727). It says the printed listing "cannot possibly be successfully loaded, assembled, POKEd, or executed," and gives a rewrite.

**[P3] Empson, D. "Apple II Random Number Generator." *GS WorldView*, Nov 1999.** This is a write-up of Robert C. Moore, "Random Bytes," *The Sourceror's Apprentice* 1(4), April 1989.
URL: https://gswv.apple2.org.za/a2zine/GS.WorldView/v1999/Nov/Articles.and.Reviews/Apple2RandomNumberGenerator.htm (fetched).
It describes a homebrew shift/XOR generator with period 2²⁵−1 = 33,554,431 (a fuller variant reaches 2³²−1). The generator is seeded from $4E/$4F and warmed up with 32 throwaway calls. The article says it "doesn't have any connection to the Applesoft BASIC RND() function." It is evidence that the community was replacing `RND` outright.

*What I searched for and didn't find:* I found no *Nibble*, *Creative Computing*, or *Dr. Dobb's* article on Applesoft `RND` that I could fetch. Call-A.P.P.L.E. and *Byte* items appear only as citations; see §1.5.

### 1.3 Vendor primary sources (Apple, Microsoft) and ROM artifacts

**[O1] Apple Computer. *Applesoft BASIC Programming Reference Manual*** (1981 per [A4]).
URL: https://archive.org/stream/Applesoft_BASIC_Programming_Reference_Manual_Apple_Computer/Applesoft_BASIC_Programming_Reference_Manual_Apple_Computer_djvu.txt (downloaded OCR; RND passages read).
This is Apple's official description of `RND`:
- A positive argument "generates a new random number each time it is used."
- A negative argument works "as if from a permanent random number table built into the APPLE."
- `RND(0)` returns the most recent number, and "CLEAR and NEW do not affect this" (p. 102; summary on p. 159).
- The manual never mentions the fixed power-on sequence or $4E/$4F. [A4]'s page-cited quotes match this OCR text word for word, so the quotes are double-sourced.

**[O2] Apple Computer. *Apple II Reference Manual*** (the edition covering the Apple II and Apple II Plus; I did not verify the exact printing date).
URL: https://archive.org/stream/apple-ii-ref-manual/Image072217171023.duplex.merged_djvu.txt (downloaded OCR; read).
Apple documents the keyboard counter as a seed source: "Random Number Seeding. While it waits for the user to press a key, RDKEY is continually adding 1 to a pair of numbers in memory. When a key is finally pressed, these two locations together represent a number from 0 to 65,535, the exact value of which is quite unpredictable. Many programs and languages use this number as the base of a random number…" (p. 32). The built-in routine list says "$FD1B KEYIN … randomizes the random number seed," and the ROM listing shows `FD1B: E6 4E  KEYIN INC RNDL` / `FD1D: D0 02 BNE KEYIN2 INCR RND NUMBER` / `FD1F: E6 4F INC RNDH`.

**[O3] Apple Computer. *Apple IIe Technical Reference Manual*** (I did not verify the printing date).
URL: https://archive.org/stream/Apple_IIe_Technical_Reference_Manual/Apple_IIe_Technical_Reference_Manual_djvu.txt (downloaded OCR; read).
"KEYIN repeatedly increments the 16-bit number in memory locations 78 and 79 (hexadecimal $4E and $4F)… The value of this number changes so rapidly that there is no way to predict what it will be after a key is pressed." Appendix B describes "$FD1B KEYIN … randomizes the random number seed at $4E-$4F." The zero-page listing labels these bytes "random counter low/high." The internal-ROM listing shows the IIe doing the same increment elsewhere (`C27D: E6 4E WAITKEY1 INC RNDL ;bump random seed`).

**[O4] Microsoft. BASIC-M6502 source, v1.1 (1976–78), file `m6502.asm`.**
URL: https://github.com/microsoft/BASIC-M6502 (raw file downloaded from https://raw.githubusercontent.com/microsoft/BASIC-M6502/main/m6502.asm).
This is the original assembly source that Applesoft descends from. `REALIO=4` selects the Apple build. The `RND` routine (source line 6353) and its constants `RMULZC`/`RADDZC` (lines 6344–6351) sit inside a `RADIX 8` block (line 4847), so their values are octal. The source shows three things:
- Both constants were written with only **four** bytes each, even though `ADDPRC==1` selects five-byte floats. The truncation is in Microsoft's source, not in Apple's port.
- The seed initializer `RNDX` does get its fifth byte (`IFN ADDPRC,<89>`).
- The copy loop's count is `LDXI RNDX+4-CHRGET`. That count reaches only the fourth seed byte, which makes it the source-level origin of the uncopied fifth byte (c, from reading the expression).

Comments in the routine include "REVERSE HO AND LO" and "MAKE RESULT BETWEEN 0 AND 1."

**[O5] ROM images from the AppleWin project: `Apple2_Plus.rom`, `Apple2e.rom`, `Apple2e_Enhanced.rom`.**
URL: https://github.com/AppleWin/AppleWin/tree/master/resource (listed via the GitHub API; the raw files were downloaded and dumped with Python).
These bytes are my ground truth. $EFA6–$EFE9 (constants and `RND`), $F123–$F127 (initial seed), and $F150–$F151 (copy-loop count) are **byte-identical across the II+, unenhanced IIe, and enhanced IIe images**. $FD1B differs between models: on the II+ it is `E6 4E D0 02 E6 4F`, while both IIe images jump elsewhere (see [O3]).

### 1.4 Modern community and reference

**[M1] Sander-Cederlof, B. *S-C DocuMentor: Applesoft*** (commented disassembly).
URLs: http://www.txbobsc.com/scsc/scdocumentor/ (index), https://www.txbobsc.com/scsc/scdocumentor/EE8D.html (`RND`), https://www.txbobsc.com/scsc/scdocumentor/EFEA.html (cold start). All fetched.
This is the canonical commented listing. At the `RND` code it says "VERY POOR RND ALGORITHM," "ALSO, CONSTANTS ARE TRUNCATED," and "<<<THIS DOES NOTHING, DUE TO >>> <<<SMALL EXPONENT >>>". At the constants it says "<<< THESE ARE MISSING ONE BYTE FOR FP VALUES >>>". At the cold start it says "<<< NOTE THAT LOOP VALUE IS WRONG! >>> <<< THE LAST BYTE OF THE RANDOM SEED IS NOT >>> <<< COPIED INTO PAGE ZERO! >>>". It also labels the swap "SHUFFLE HI AND LO BYTES / TO SUPPOSEDLY MAKE IT MORE RANDOM".

**[M2] McFadden, A. "Applesoft Disassembly"** (6502bench SourceGen project; created 2019-10-27, updated 2025-08-03).
URL: https://6502disassembly.com/a2-rom/Applesoft.html (fetched; `RND` and cold-start sections read).
This is a cross-referenced conversion of [M1] with the same bug annotations. **It is not independent of [M1]**, so I never count the two as separate corroboration.

**[M3] McFadden, A. Monitor and Integer BASIC disassemblies.**
URLs: https://6502disassembly.com/a2-rom/OrigF8ROM.html, https://6502disassembly.com/a2-rom/AutoF8ROM.html, https://6502disassembly.com/a2-rom/IntegerBASIC.html (all downloaded; relevant sections read).
In both the original and Autostart Monitor, KEYIN is at $FD1B. Integer BASIC's `RND` is at $EF4E and reads and rewrites `MON_RNDL`/`MON_RNDH` ($4E/$4F) directly, labelled 'low byte of KEYIN "random" value.'

**[M4] Mosher, C. `Apple-II-Source`, `src/system/monitor/common/keyin.m4`.**
URL: https://raw.githubusercontent.com/cmosher01/Apple-II-Source/master/src/system/monitor/common/keyin.m4 (downloaded; read).
This reconstructed, assemblable Monitor source has `KEYIN INC RNDL / BNE KEYIN2 ;INCR RND NUMBER / INC RNDH / KEYIN2 BIT KBD ;KEY DOWN? / BPL KEYIN`.

**[M5] Steil, M. "Fully Commented Commodore 64 BASIC ROM Disassembly – based on Applesoft!"** pagetable.com, 2014-12-29.
URL: https://www.pagetable.com/?p=728 (fetched).
Steil writes that Applesoft and Commodore BASIC are "almost the same instruction for instruction," because both derive from Microsoft 6502 BASIC. This is useful context: Commodore `RND` critiques concern the same code family. **I did not check whether Commodore's RND constants are identical.**

**[M6] C64-Wiki, "RND."**
URL: https://www.c64-wiki.com/wiki/RND (fetched).
It claims Commodore's `RND` sequence "could shrink to 723 values without repetition." A further claim, that it can get stuck on a single value, appeared only in a search-engine summary of this page and not in my fetch. The wiki gives no author or method; it points to comp.sys.cbm and forum threads I didn't fetch. Treat this as (b), and it is about Commodore, not Apple.

**[M7] Applefritter forum. "Random number generation on the Apple II with AppleSoft BASIC,"** July 2021.
URL: https://www.applefritter.com/content/random-number-generation-apple-ii-applesoft-basic (fetched).
The practical point: "The values at 78 and 79 are only updated by the keyin routine while it's waiting for keyboard input. Just checking the keyboard flag at $C000 with the WAIT command bypasses this." The thread cites [P1] and [A4].

**[M8] Wikipedia, "Applesoft BASIC."**
URL: https://en.wikipedia.org/wiki/Applesoft_BASIC (fetched).
A secondary source. It says `RND` "is capable of producing a predictable series of outputs due to the manner in which the generator is seeded when first powering on," citing [A4].

**[M9] Wikipedia, "RANDU."**
URL: https://en.wikipedia.org/wiki/RANDU (fetched).
Background for the lattice discussion: V₍ⱼ₊₁₎ = 65539·Vⱼ mod 2³¹. Consecutive triples obey x₍ₖ₊₂₎ = 6x₍ₖ₊₁₎ − 9xₖ, so they fall on 15 planes. It quotes Knuth (1981) on RANDU bringing "dismay into the eyes and stomachs of many computer scientists."

**[M10] Wikipedia, "Marsaglia's theorem."**
URL: https://en.wikipedia.org/wiki/Marsaglia's_theorem (fetched).
A secondary statement of [A1]: at most (n!·m)^(1/n) hyperplanes. For RANDU it gives a bound of 2,344 planes in 3-D against 15 actual.

### 1.5 Cited by fetched sources, but NOT fetched or read by me (no claims rest on these)

- **[X1] Modianos, D. T., Scott, R. C., & Cornwell, L. W. (1987). "Testing intrinsic random-number generators." *Byte* 12, 175–178.** Cited by [A4]. I did not find an online copy. What I know of its content comes only from a search-engine summary whose source page I couldn't identify: the article "surveyed a number of random-number generators on nine microcomputers, with some generators, particularly those of the Apple IIe, being flawed either for statistical reasons or because they have short cycles."
- **[X2] Sparks, D. (1983). "RND is fatally flawed." *Call-A.P.P.L.E.* 6, 29–34 (Jan 1983).** The title, issue, and pages are confirmed by [P1]. The author's name "Sparks, D." comes only from a search snippet of a Springer reference list, so it is **unverified**. Scans on callapple.org are behind a members login.
- **[X3] Wichmann, B. & Hill, D. (1987). "Building a random-number generator." *Byte* 12(3), 127–128.** Cited by [A4]; I know its metadata only from search results.
- **[X4] Albrecht & Firedrake, *The Mysterious and Unpredictable RND*.** Cited by [A3] (spelled "Albrech"). Not verified.
- **[X5] comp.sys.apple2 / comp.sys.apple2.programmer threads**: "Where does the Applesoft RND() function get its data?", "Streamlining Applesoft – Random number generators", and "Need a good random number generator". Google Groups returned HTTP 429 or empty pages on every attempt, and **no content from them is used here**.
- **[X6] Crossley, J. "Applesoft Internals," *Apple Orchard* 1(1).** Named by [M1] as the origin of its label names. Not fetched.

---

## 2. Established facts

### F1. Location and bytes of `RND` — (a)

The Apple ][+ ROM image [O5] contains, byte for byte, the listing in [M1] (and [M2]):

```
EFA6: 98 35 44 7A        CON_RND_1   (4 bytes; "MISSING ONE BYTE")
EFAA: 68 28 B1 46        CON_RND_2
EFAE: 20 82 EB    RND    JSR SIGN            ; argument -> -1 / 0 / +1
EFB1: AA                 TAX
EFB2: 30 18              BMI $EFCC           ; negative: use argument itself
EFB4: A9 C9              LDA #<RNDSEED       ; $00C9
EFB6: A0 00              LDY #>RNDSEED
EFB8: 20 F9 EA           JSR LOAD_FAC_FROM_YA
EFBB: 8A                 TXA
EFBC: F0 E7              BEQ $EFA5 (RTS)     ; zero: return seed unchanged
EFBE: A9 A6 A0 EF 20 7F E9   LDA/LDY #CON_RND_1 : JSR FMULT
EFC5: A9 AA A0 EF 20 BE E7   LDA/LDY #CON_RND_2 : JSR FADD
EFCC: A6 A1              LDX FAC+4           ; swap highest and lowest
EFCE: A5 9E              LDA FAC+1           ;   mantissa bytes
EFD0: 85 A1              STA FAC+4
EFD2: 86 9E              STX FAC+1
EFD4: A9 00 85 A2        LDA #0 : STA FAC_SIGN   ; force positive
EFD8: A5 9D 85 AC        LDA FAC : STA FAC_EXTENSION ; old exponent -> guard byte
EFDC: A9 80 85 9D        LDA #$80 : STA FAC      ; exponent 2^0 -> value < 1
EFE0: 20 2E E8           JSR NORMALIZE_FAC_2
EFE3: A2 C9 A0 00        LDX #<RNDSEED : LDY #>RNDSEED
EFE7: 4C 2B EB           JMP STORE_FAC_AT_YX_ROUNDED
```

The unenhanced and enhanced IIe images contain identical bytes over $EFA6–$EFE9 [O5]. The code matches the Microsoft source [O4] step for step. In that source, `LDAI 200` is in a `RADIX 8` block, so it is octal 200 = $80, consistent with the ROM byte (a).

### F2. The algorithm in words — (a)

With a positive argument, `RND` multiplies the stored seed by CON_RND_1 and adds CON_RND_2 using the ordinary floating-point routines. It then swaps the high and low mantissa bytes and clears the sign. It moves the old exponent into the guard (extension) byte and forces the exponent to $80, which normalizes the result into [0,1). It stores the rounded result back as the new seed [O4][M1][O5]. [P1] calls this a congruential algorithm implemented in floating point, and [M1] calls it a "very poor RND algorithm."

**There is no modulus step.** The "mod" is implicit: forcing the exponent to $80 discards the integer part's position information (c).

### F3. The constants — (a), with (c) arithmetic

| Label | Address | Bytes (ROM [O5], listing [M1]) | Microsoft source [O4] (octal) | Value if read as 4-byte float | Value as actually loaded (5 bytes) |
|---|---|---|---|---|---|
| CON_RND_1 | $EFA6 | 98 35 44 7A | `RMULZC: 230,065,104,172` = $98,$35,$44,$7A | 11,879,546 | 11,879,546.40625 (5th byte = $68, the first byte of CON_RND_2) |
| CON_RND_2 | $EFAA | 68 28 B1 46 | `RADDZC: 150,050,261,106` = $68,$28,$B1,$46 | ≈ 3.9276777×10⁻⁸ | ≈ 3.9276778×10⁻⁸ (5th byte = $20, the `JSR` opcode at $EFAE) |

- The bytes are **triple-sourced**: ROM image, S-C listing, and Microsoft source (a).
- Applesoft floats are five bytes: an exponent plus four mantissa bytes. [P1] says "Applesoft arithmetic routines expect five-byte operands. For some reason the constants used in RND are only four bytes long," and [M1] flags "MISSING ONE BYTE" (a).
- The decimal values are my own decoding of the Microsoft float format (c). The mantissa's top bit is the sign bit and is forced to 1.
- The claim that the loader picks up the next ROM byte as the fifth byte follows from the byte layout (c, strongly supported by the code). The emulator executes the real loaders, so every (c-emu) result includes this effect. I did not test it in isolation.

### F4. Seed storage and initial value — (a)

- `RNDSEED` is five bytes at **$C9–$CD** [M1][M2][P1].
- The initial value is stored at **$F123: `80 4F C7 52 58`**, which is ≈ 0.811635157 [O5][M1].
- Microsoft's source gives `RNDX: 128,79,199,82,<89>` in decimal (`RADIX 10` block), which is $80,$4F,$C7,$52,**$59**. The fifth byte differs from the Apple ROM ($58) (a). Because that byte is never copied (F5), the difference has no effect (c).

### F5. The initialization bug: the fifth seed byte ($CD) is never set — (a), triple-sourced

At cold start, `F150: A2 1C  LDX #$1C` copies the generic CHRGET routine and the seed into zero page. The count is one too small, so $CD is never written [O5][M1][P1]. [P1]: "Changing $F151 from $1C to $1D would fix it." The source-level cause is `LDXI RNDX+4-CHRGET` in [O4], written for four-byte floats (a). As a result, **$CD holds whatever was in RAM** when BASIC started (c).

### F6. `RND(0)` — (a)

`RND(0)` returns the most recently generated number, and "CLEAR and NEW do not affect this" [O1]. In the code, a zero sign loads the seed and branches to `RTS` without changing it [O5][M1].

### F7. Negative arguments — (a) for the documented behavior, (c) for the code-level details

- The manual [O1] says: "RND(aexpr) generates the same random number each time it is used with the same aexpr, as if from a permanent random number table built into the APPLE," and each negative argument starts "a particular, repeatable sequence" (a).
- The `BMI $EFCC` [O5] skips the multiply and add. The negative argument's own float bytes are byte-swapped, sign-cleared, normalized, and stored as the seed (a). So the new seed depends only on |argument| (c).
- **Edge case (c):** `SIGN` reduces an argument of 0 to zero. So `RND(-(PEEK(78)+256*PEEK(79)))` with both bytes zero is really `RND(0)` and **does not reseed**.

### F8. `$4E/$4F` (RNDL/RNDH) is a keyboard-wait counter — (a), triple-sourced

The Monitor's KEYIN at **$FD1B** runs `INC RNDL ($4E)`, `BNE`, `INC RNDH ($4F)`, `BIT KBD`, `BPL KEYIN`, looping until a key's high bit is set. Sources: Apple's own ROM listing and prose [O2], the IIe manual [O3], [M3] (both original and Autostart F8 ROMs), [M4], and the II+ ROM bytes `E6 4E D0 02 E6 4F` [O5]. Apple calls the value "quite unpredictable" [O2] with "no way to predict what it will be" [O3] (a — Apple's claim, not a measurement).

### F9. Applesoft `RND` never reads $4E/$4F; Integer BASIC `RND` does — (a)

The Applesoft `RND` code at $EFAE–$EFE9 contains no reference to $4E or $4F [O5][M1], and [A4] says: "Applesoft in fact makes no use of the $4E-$4F value." Integer BASIC's `RND` ($EF4E) loads, transforms, and stores `MON_RNDL/MON_RNDH` directly [M3], and [P1] agrees ("Integer BASIC uses this seed").

### F10. The counter only moves while KEYIN waits — (a) from the code, (b) for the practical consequences

In the II+ Monitor, the only code that increments the counter is KEYIN's wait loop [O2][M4]. Integer BASIC's `RND` also rewrites $4E/$4F [M3], and IIe firmware has its own increment loops [O3]. So:
- A turnkey program that never takes keyboard input leaves the seed with no human timing in it [A4] (a — Aldridge's claim).
- Polling the keyboard with `WAIT 49152,128` or `PEEK(49152)` bypasses the counter [M7] (b).

### F11. The documented workaround — (a)

According to [A4], an Apple representative advised `X=RND(-1*(PEEK(78)+256*PEEK(79)))` "after keyboard input but before the first use of RND." [P1] and [P3] instead replaced `RND` with USR routines, and [P3]'s generator is seeded from $4E/$4F.

---

## 3. Contested or unclear

**C1. What is the period of `RND`? 37,758 [P1] vs 202 [A3].** Both are published, and both are right.
- (a) [P1] reports repetition starting at "the 37,758th" number. [A3] reports a loop "repeating itself every 202 numbers," entered between call 10,000 and 20,000.
- (c-emu) I ran the genuine ROM `RND` (II+ image [O5]) under py65. Starting from the ROM seed `80 4F C7 52 xx`:

  | $CD at cold start | Calls before entering the cycle | Cycle length |
  |---|---|---|
  | $00 | 19,263 | **37,758** |
  | $FF | 6,818 | **37,758** |
  | $58 (Microsoft's intended byte) | 15,382 | **202** |
  | $7A | 12,155 | **202** |

  After 16 reseeds with `RND(-n)` (n = 1, 65535, and 14 random values) I also found cycles of **32,366** and **4,082**. `RND` is not one long cycle. It has several attractor cycles, and which one a program falls into depends on the seed, including the uninitialized byte $CD.
- (c-emu) **Full sweep of all 256 possible $CD values at cold start** (raw results in `tools/cd_sweep_results.jsonl`). Every start ends in one of five cycles:

  | Cycle length | $CD values that reach it | Share |
  |---|---|---|
  | 37,758 | 110 | 43.0 % |
  | 32,366 | 78 | 30.5 % |
  | 202 | 59 | 23.0 % |
  | 4,082 | 5 | 2.0 % |
  | 12,559 | 4 ($5F, $6D, $A8, $A9) | 1.6 % |

  Steps before entering a cycle range from 164 to 62,895 (mean ≈ 17,180). For the first four lengths, I checked membership against the actual recorded cycle states. The four 12,559 results were each detected independently, and I did not check that they are the same cycle.
- The "period of `RND`" is therefore not a single number, and the two period sources don't actually disagree (c-emu).
- **Caveats (c):** my harness only sets up FAC and the seed, not a full BASIC environment, and it tests only the II+ image (the IIe `RND` bytes are identical). No hardware run was done.

**C2. Is the power-on sequence really identical every time?**
- (a) [A4] observed identical sequences after each power-on and says so without qualification.
- (a) F5 shows $CD is never initialized. [P1] suggests that "not copying the last byte could make the numbers generated a little more random from one run to the next."
- (c-emu) Changing $CD changes the sequence from the **first** call. $CD=$00 gives 0.270012, 0.139756, …; $CD=$58 gives 0.512199, 0.362071, …
- The power-up value of $CD also decides the cycle: 23 % of possible values (59 of 256) put an untouched program into the 202-number loop (C1 sweep, (c-emu)).
- Both can hold. Aldridge's machine probably powered up with the same $CD value each time, and DRAM power-up contents are often consistent on a given machine (c). But nobody has published a measurement of what $CD powers up to, or whether DOS 3.3 or another boot path writes $CD before `RND` runs. **This is open. A test on real hardware would settle it.**

**C3. What does the "tweak" swap?**
- [P1] says Applesoft "tweaks the generated value by reversing the middle two bytes of the 32-bit value."
- The ROM [O5] and Microsoft source [O4] ("REVERSE HO AND LO") swap **FAC+1 and FAC+4**, the highest and lowest mantissa bytes, and [M1] agrees ("SHUFFLE HI AND LO BYTES").
- **The code is authoritative (a). [P1]'s wording is wrong on this detail.**

**C4. Does the `FADD` of CON_RND_2 "do nothing"?**
- (a) [M1]: "<<<THIS DOES NOTHING, DUE TO >>> <<<SMALL EXPONENT >>>".
- (c-emu) I replaced the `JSR FADD` at $EFC9 with NOPs and compared against the unpatched code from cold start ($CD=$00). The seeds are identical for 3,885 calls and diverge at call **3,886**.
- The addend is usually swallowed by rounding but occasionally changes the result, so "does nothing" is nearly but not literally true. I have not explained the mechanism.

**C5. What did Modianos et al. (Byte, 1987) measure?** They are cited as having found `RND` limits [A4] and IIe short cycles (snippet only). **Not read. Don't use on a slide without the article.**

**C6. Who wrote "RND is Fatally Flawed"?** The title and issue are confirmed by [P1]. The author name "D. Sparks" is **unverified** (see [X2]).

**C7. The Kaner–Vokey constants.** The PDF [A3] lists X: a=27182819621, c=3; Y: a=8413453205, c=99991; Z: a=31415938565, c=24607. [P2] says the printed 24607 is a typo for 26407 ($6727, confirmed by arithmetic, (c)) and labels them in a different order. This matters only if the deck quotes the replacement constants.

**C8. Kaner & Vokey's date: 1982 or 1984?** The PDF is marked "Copyright © 1982" and says it was published in *MICRO* in June 1984; [P2] confirms the 1984 publication. Cite **1984** for publication and 1982 for the manuscript (a).

**C9. Commodore's "723 values" figure [M6].** Its method and provenance are unknown, and it concerns a different ROM. [M5] shows the code families are nearly identical (b), but I didn't compare Commodore's constants or seed handling. **Don't put this on an Apple slide as an Apple number.**

**C10. Is Applesoft `RND` an "LCG" with lattice structure?**
- Period sources call it congruential [P1], and community sources call it a "modified LCG" (search snippet, unverified).
- Structurally it is not an LCG (c). There is no integer modulus, the multiply and add are floating point with rounding, and a byte permutation and renormalization follow.
- Marsaglia's bound [A1] and Knuth's spectral test [A2] assume an integer LCG, so they do not transfer mechanically.
- **I found no published spectral test, lattice plot, or TestU01/DIEHARD/NIST STS run of Applesoft `RND`**, after searching explicitly for each.
- The brief's item 1 ("lattice/spectral structure") needs either new analysis clearly labelled (c), or a reframe: LCG lattice theory is the *standard* that Applesoft `RND` fails before you even get there, because its cycles are tiny.

**C11. How fast does $4E/$4F wrap?**
- (a) [A4]: "counts to $FFFF and starts again at 0 in less than a second."
- (c) The II+ KEYIN loop is `INC zp` (5 cycles) + `BNE` taken (3) + `BIT abs` (4) + `BPL` taken (3) = 15 CPU cycles per count. 65,536 × 15 ≈ 983,000 cycles, or about **0.96 s** at ≈1.02 MHz. That roughly matches Aldridge. No hardware measurement has been done, and the IIe path differs ([O3]).

**C12. What do Gleason (1988) [A5] and Brysbaert (1991) [A6] actually report?** Only the abstract and metadata are verified; their numbers are unknown to me.

---

## 4. Quantitative ammunition

Each figure carries its label and source.

| # | Figure | Value | Label / source |
|---|---|---|---|
| Q1 | Seed state size | 5 bytes at $C9–$CD, of which the mantissa is 32 bits | (a) [M1][P1] |
| Q2 | Theoretical ceiling for a 32-bit mantissa | 2³² = 4,294,967,296 ("4 billion") | (a) [P1]; arithmetic (c) |
| Q3 | Cycle AAL observed (1984) | repetition from the **37,758th** number; HGR plot stalls after **~7 minutes** | (a) [P1] |
| Q4 | Cycle Kaner & Vokey observed | **202**, entered between call 10,000 and 20,000 | (a) [A3] |
| Q5 | Cycles found in the real ROM code | **37,758; 32,366; 12,559; 4,082; 202** — no other cycle turned up in 256 cold starts plus 16 reseeds | (c-emu) |
| Q5b | Cold start, all 256 values of the uninitialized $CD | 43.0 % → 37,758; 30.5 % → 32,366; **23.0 % → 202**; 2.0 % → 4,082; 1.6 % → 12,559 | (c-emu; exhaustive over $CD, ROM seed bytes otherwise fixed) |
| Q6 | 37,758 as a fraction of 2³² | ≈ 0.00088 % | (c) |
| Q7 | Longest run before any repeat, across all 272 starts | 100,653 calls (cold start, $CD=$0C: 62,895 before entering the cycle + 37,758). Among reseeds: 76,577 (`RND(-23826)`) | (c-emu) |
| Q8 | 16 reseeds `RND(-n)`: which cycle | 10 → 37,758; 3 → 32,366; 1 → 4,082; 2 → 202 | (c-emu; a sample of 16, not a population estimate) |
| Q9 | Cold start with Microsoft's intended $CD=$58 | falls into the **202-cycle** after 15,382 calls | (c-emu) |
| Q10 | AAL's HGR demo vs the screen | 2 `RND` calls per dot means at most 18,879 distinct dots per 37,758-cycle, against 280×160 = 44,800 positions, so it can never fill the screen | (c) arithmetic on [P1] |
| Q11 | Multiplier / addend | 11,879,546 / ≈3.927677739×10⁻⁸ (both constants one byte short) | (a) bytes [O5][M1][O4]; decoding (c) |
| Q12 | Effect of removing the addend | first divergence at call 3,886 | (c-emu) |
| Q13 | Keyboard seed space | 16 bits, so at most 65,536 values; `RND(-0)` does not reseed, leaving ≤ 65,535 distinct reseeds | (a) [O2][O3]; (c) edge case |
| Q14 | $4E/$4F wrap time | "< 1 s" [A4]; ≈0.96 s by cycle count on the II+ | (a) / (c) |
| Q15 | Manual's promise | a "new random number each time" — no warning about the power-on sequence | (a) [O1] |
| Q16 | Real-world damage | a psychology memory experiment repeated "individually randomized" word lists for the first subject each day | (a) [A4] |
| Q17 | Good-LCG yardstick | Knuth's spectral test: ν > 0.10 "pass", ν > 1.0 "flying colors"; Kaner–Vokey's replacements score 2.37–7.40 (normalized) at m = 2⁴⁰ | (a) [A3], reporting [A2] |
| Q18 | Lattice background (not measured on Applesoft) | Marsaglia bound for m=2³²: ≤ ⌊(2·2³²)^½⌋ = 92,681 lines in 2-D, ≤ ⌊(6·2³²)^⅓⌋ = 2,953 planes in 3-D; RANDU: 15 planes against a bound of 2,344 | bound from [M10] (secondary for [A1]); arithmetic (c); RANDU [M9] (b) |
| Q19 | Homebrew replacements | Call-A.P.P.L.E. a=8192, m=67,099,547; AAL/Knuth a=314,159,269, c=907,633,386, m=2³²; AAL 16-bit a=19,125, c=13,843, m=2¹⁶; Moore XOR period 2²⁵−1 = 33,554,431; Kaner–Vokey m=2⁴⁰ | (a) [P1][P2][P3][A3] |

---

## 5. Verification log

### URLs actually retrieved (tool used)

Every URL in §1.1–§1.4 was retrieved in this session, except those marked in-line as failed (pnas.org). I used web fetch, `curl` followed by text extraction, or the GitHub or Crossref APIs. For the two GitHub repository landing URLs ([O4], [O5]), the content came from the raw file and the API listing, not the HTML page. The list:
- kaner.com PDF, asimov PDF, and eric.ed.gov
- txbobsc.com: aal8405, aal8406, and the scdocumentor index, EE8D, and EFEA pages
- gswv.apple2.org.za
- archive.org OCR texts ×3
- GitHub: microsoft/BASIC-M6502 raw, the AppleWin resource listing plus 3 ROMs, and cmosher01 raw
- 6502disassembly.com: Applesoft, OrigF8ROM, AutoF8ROM, IntegerBASIC
- pagetable.com ?p=728
- c64-wiki.com; applefritter.com; Wikipedia ×3
- pmc.ncbi.nlm.nih.gov (metadata only)
- Knuth's TAOCP page
- api.crossref.org ×3

### Tried and failed (and not relied on)

- pnas.org (403)
- ui.adsabs.harvard.edu (405)
- Google Groups ×3 (429 or empty)
- link.springer.com article pages (login redirect)
- the Springer PDF for [A6] (returned HTML)

### Tools

`tools/rnd_emu.py` and `tools/rnd_experiments.py` need py65 and an Apple ][+ ROM image, which is not stored in this repository. They produced every (c-emu) figure. `tools/cd_sweep_results.jsonl` holds the raw 256-row $CD sweep.

To reproduce, with `python -m venv v && v/bin/pip install py65`:
- `rnd_experiments.py <rom> cold 00` and `neg 1,25284`
- `nofadd 00 20000`
- `mkcycles cycles.pkl`, then `classify cycles.pkl cold 0,1,2…`

---

## 6. Claim tally (after re-reading this file, 2026-09-12)

I re-read the whole file against the fetched material. That pass fixed:
- a leftover bracketed paraphrase in C4
- a wrong cross-reference in [A2]: Knuth's rules are in [P1], not [P2]
- an [X1] summary I had mis-attributed to [A6]
- overclaims in F3 and F10

Each of the 43 numbered items in §2–§4 is counted once, at the status of its slide-facing claim:

| Status | Meaning | Count | Items |
|---|---|---|---|
| **V2** | Verified: fetched, and ≥ 2 independent sources ([M2] is not counted as independent of [M1]) | **15** | F1–F9, C3, C8, Q1, Q11, Q13, Q15 |
| **V1** | Verified: fetched primary source, single-sourced | **9** | F10, F11, C7, Q3, Q4, Q14, Q16, Q17, Q19 |
| **E** | Reproducible emulation of the genuine ROM (c-emu); no published source | **8** | C1, C4, Q5, Q5b, Q7, Q8, Q9, Q12 |
| **I** | Inference or arithmetic (c) | **6** | C10, C11, Q2, Q6, Q10, Q18 |
| **U** | Unverified or open | **5** | C2 (open question), C5, C6, C9, C12 |

**Verified: 24 of 43. Unverified or open: 5 of 43. The other 14 are my own emulation (8) or inference (6).**

**Constants and addresses.** These are double-sourced:
- `RND` at $EFAE, CON_RND_1/2 bytes, and RNDSEED $C9–$CD
- initial seed $F123, copy count $F150/$F151
- KEYIN $FD1B, RNDL/RNDH $4E/$4F

These are single-sourced, and flagged here so nobody over-relies on them:
- the Microsoft `RNDX` fifth byte ($59), from [O4] only
- Integer BASIC `RND` at $EF4E, from [M3] only; [P1] confirms the behavior but not the address
- IIe `WAITKEY1` at $C27D, from [O3] OCR only
- the source line numbers in [O4]
