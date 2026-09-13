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

**[A3] Kaner, H. C. & Vokey, J. R. "A Better Random Number Generator."** *MICRO* No. 72, June 1984, pp. 26–35. The printed byline is "H. Cem Kaner and John R. Vokey". The manuscript is titled "A Better Random Number Generator for Apple's Floating Point BASIC", © 1982.

**Two versions exist, and they differ:**
- **Manuscript**, https://kaner.com/pdfs/random.pdf (downloaded; full text read; the author has removed the assembly-language sections).
  - It says `RND` "fails [standard statistical tests] miserably."
  - On the first batch of 10,000 numbers, `RND` failed only the triplets test.
  - **It contains the 202 passage:** "between the 10,000th and the 20,000th number generated, RND fell into an endless loop, repeating itself every 202 numbers."
- **Printed article**, https://archive.org/details/micro-6502-journal-72 (OCR `micro_72_jun_1984_djvu.txt` downloaded; article read).
  - The issue's table of contents has "26 A Better Random Number Generator — H. Cem Kaner and John R. Vokey", with the next article at p. 36.
  - The printed Applesoft comment is only "RND, when subjected to standard statistical tests, fails them badly."
  - It says "We developed these generators two years ago (summer, 1981)."
  - **The OCR contains no "202", "endless" or "miserably" anywhere in the issue**, so the printed article apparently omits the 202-loop test. OCR can drop digits, so this should be checked against the scan.
  - Printed Table 1 gives Z's additive constant as 26407; the manuscript's 24607 is the typo [P2] flagged.

**Independent confirmation of the publication date:** Heth (1984), *BRMIC* 16(6):548–550 (doi:10.3758/BF03200841), cites "Kaner, H. C., & Vokey, J. R. (1984, June). A better random number generator. Micro, pp. 26–35" (Crossref reference list, fetched). Vokey's university publication list (https://scholar.ulethbridge.ca/jrvokey/publications/, fetched) gives "(1982) … Micro, 72, 26–35"; the year there is the manuscript's, since issue 72 is June 1984.

**Why it matters here:** it has the spectral-test selection of 40-bit LCG constants (Coveyou–MacPherson; Knuth's Algorithm S), with full ν₂…ν₆ tables, and it is a good primary source for explaining lattice structure to the audience.

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

**[P4] Sander-Cederlof, B. "Random Number Generator from Integer BASIC." *Apple Assembly Line* 1(11), August 1981.**
URL: https://www.txbobsc.com/aal/1981/aal8108.html (downloaded; full text read).
This article shows how to call the Integer BASIC `RND` from machine code: enter at `IB.RANDOM .EQ $EF51` with X=$20 and the argument in $CE/$CF. It gives a stand-alone copy of "Woz's routines" that reads `MON.RNDL/MON.RNDH` ($4E/$4F) and states that the monitor modifies the seed "whenever you are in KEYIN… at $FD1B thru $FD24."

It also claims a defect: "It is a binary polynomial technique, but there seems to be a bug in it… it really generates the values between $6000 and $60FF twice, and never generates $2000-20FF at all!" **I could not reproduce that defect by running the genuine ROM code** (see C13).

**[P5] Sparks, D. "RND is Fatally Flawed."** *Call-A.P.P.L.E.* 6(1), January 1983. It is a "Call-A.P.P.L.E. Technote" beginning on p. 29, per the issue's menu page, with the byline "David Sparks/Call-A.P.P.L.E. Staff Writer".
Crossref's structured reference list for Vokey, Baker, Hayman & Jacoby (1986), *BRMIC*, doi:10.3758/BF03200985, cites it as "Sparks, D. (1983) RND is fatally flawed. Call A.P.P. L. E., 6, 29–34." Vokey was Kaner's co-author.
URL: https://archive.org/details/call-apple-1983-01 (OCR `call_apple_v6_n1_djvu.txt` downloaded; article read).

What it establishes:
- **Who got there first**, in Sparks's words:
  - "Tom Crawford in February 1981 described the problem: after a few thousand calls, the RND function starts repeating itself."
  - "Dave Lingwood discovered that the initial random number 'seed' value provided by Applesoft is not always the same, and described his findings in Call-A.P.P.L.E. in Depth #1."
  - Sparks's own RNDGEN (Call-A.P.P.L.E., May 1982) also failed.
- **The startup bug, fully diagnosed in January 1983:** "Look at the 'disassembly' of line $F150. It says LDX #$1C. That is the bug… If the instruction read 'LDX #$1D' then it would correctly get one additional byte, the essential final one of the 'seed'… byte $CD, does not receive any known value which can be consistently relied upon."
  - The seed at $F123–$F127 is given as "80 4F C7 52 58… .811635157."
- **The multiplier, read as five bytes:** "98 35 44 7A 68, and they represent the decimal value 11879546.4." This matches F3's as-loaded value (a).
- **Restoring the fifth byte doesn't help:** with all five bytes restored (`C9:80 4F C7 52 58`), the Hi-Res dot test still fails.
- **Very short loops:** "we have found instances of seeds which lead to repeating sequences only a few dozen values in length." I did not reproduce this; see C14.
- **Crawford's RND(-1) claim:** Crawford found RND(-1) seeding "produces an especially long sequence; he tested it to 10 million values." Emulation contradicts this; see C14.
- **Its "smoking gun"** is the four-instruction byte swap at $EFCC.
- **It publishes USRND** (Hare, Russ, Faulkner, Sparks): S' = (8192·S) MOD 67099547.

**[P6] Hare, T., Russ, J. & Faulkner, G. "A New Pseudo-Random Number Generator."** *Call-A.P.P.L.E.* 6(1), January 1983, p. 33. The issue menu lists it under "John Russ"; the article byline is "Tom Hare/John Russ/Gary Faulkner", all of North Carolina State University. Same scan as [P5].
- "The sequence of values provided can fall into one of several rather short (as little as 200) repetitive loops, and even with reseeding the values provided will not pass even simple tests of having a random nature."
- It calls `RND` an "unexpected number generator."
- It originated the Hi-Res dot-plot test.
- Its "License Plate Game" simulation shows gaps and regular repeats in the results for 2,900 alphabets generated with `RND`. The replacement generator's loop is "over 67 million."

**[P7] Crawford, T. "Applesoft Random Function."** *Call-A.P.P.L.E.*, February 1981.
- The title, author and month are verified from the "1981 Call-A.P.P.L.E. Index" (listed under ADVANCED TECHNICAL), printed in *Call-A.P.P.L.E.* February 1982: https://archive.org/details/call-apple-1982-02 (OCR read).
- **The article itself is not on archive.org** (its Call-A.P.P.L.E. run starts in January 1982), **so I have not read it.** I know its content only through [P5].

**[P8] Lingwood, D. A. "Amplifying Applesoft."** In *Call-A.P.P.L.E. in Depth No. 1* (A.P.P.L.E., 1981).
- The title, author, volume and year come from a reference list in *Call-A.P.P.L.E.* January 1982: https://archive.org/details/call-apple-1982-01 (OCR read).
- **I have not read it.** According to [P5], it showed that $CD "isn't always initialized to the same value," although it "did not present the correct value for the offending byte."

**[P3] Empson, D. "Apple II Random Number Generator." *GS WorldView*, Nov 1999.** This is a write-up of Robert C. Moore, "Random Bytes," *The Sourceror's Apprentice* 1(4), April 1989.
URL: https://gswv.apple2.org.za/a2zine/GS.WorldView/v1999/Nov/Articles.and.Reviews/Apple2RandomNumberGenerator.htm (fetched).
**"Moore" is Robert C. Moore of the Applied Physics Laboratory at Johns Hopkins University, Laurel, Maryland**, per Empson's own text (fetched; it spells the university "John Hopkins"). The magazine, *The Sourceror's Apprentice*, is listed on archive.org as published by Ariel Publishing (from an item for Vol. 1 No. 3, which I didn't open) (b).

Moore's article "covers two designs for shift and exclusive OR random number generators." Empson wrote a 6502 routine for the simpler one, with period 2²⁵−1 = 33,554,431. The full design reaches 2³²−1. **Empson's page prints 2³²−1 as "4194962795", which is wrong; the correct value is 4,294,967,295.** The generator is seeded from $4E/$4F and warmed up with 32 throwaway calls. The article says it "doesn't have any connection to the Applesoft BASIC RND() function." It is evidence that the community was replacing `RND` outright.

*What I searched for and didn't find:* I found no *Nibble*, *Creative Computing*, or *Dr. Dobb's* article on Applesoft `RND` that I could fetch. Call-A.P.P.L.E. and *Byte* items appear only as citations; see §1.5.

### 1.3 Vendor primary sources (Apple, Microsoft) and ROM artifacts

**[O1] Apple Computer. *Applesoft BASIC Programming Reference Manual*.** The archived copy's notice reads "©1978 by APPLE COMPUTER INC.", product A2L000J (030-0013-03); I checked this after the first draft, which had given 1981. [A4] cites a 1981 printing.
URL: https://archive.org/stream/Applesoft_BASIC_Programming_Reference_Manual_Apple_Computer/Applesoft_BASIC_Programming_Reference_Manual_Apple_Computer_djvu.txt (downloaded OCR; RND passages read).
This is Apple's official description of `RND`:
- A positive argument "generates a new random number each time it is used."
- A negative argument works "as if from a permanent random number table built into the APPLE."
- `RND(0)` returns the most recent number, and "CLEAR and NEW do not affect this" (p. 102; summary on p. 159).
- The manual never mentions the fixed power-on sequence or $4E/$4F. [A4]'s page-cited quotes match this OCR text word for word, so the quotes are double-sourced.

**[O2] Apple Computer. *Apple II Reference Manual*.** This edition covers the Apple II and Apple II Plus. The archived copy's notice reads "©1979 by Apple Computer Inc.", product A2L0001A (030-0004-01), "Written by Christopher Espinosa".
URL: https://archive.org/stream/apple-ii-ref-manual/Image072217171023.duplex.merged_djvu.txt (downloaded OCR; read).
Apple documents the keyboard counter as a seed source: "Random Number Seeding. While it waits for the user to press a key, RDKEY is continually adding 1 to a pair of numbers in memory. When a key is finally pressed, these two locations together represent a number from 0 to 65,535, the exact value of which is quite unpredictable. Many programs and languages use this number as the base of a random number…" (p. 32). The built-in routine list says "$FD1B KEYIN … randomizes the random number seed," and the ROM listing shows `FD1B: E6 4E  KEYIN INC RNDL` / `FD1D: D0 02 BNE KEYIN2 INCR RND NUMBER` / `FD1F: E6 4F INC RNDH`.

**[O3] Apple Computer. *Apple IIe Technical Reference Manual*.** The archived copy reads "Copyright © 1985 by Apple Computer, Inc." (Addison-Wesley).
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

**[M11] AppleWin emulator source: `source/Core.cpp`, `source/Memory.cpp`, `source/Memory.h`, `help/CommandLine.html`.**
URLs: https://raw.githubusercontent.com/AppleWin/AppleWin/master/source/Core.cpp, …/source/Memory.cpp, …/source/Memory.h, …/help/CommandLine.html (all downloaded; relevant lines read).
- The default is `int g_nMemoryClearType = MIP_FF_FF_00_00;` (Core.cpp line 79).
- In `MemReset()`, that pattern writes `FF FF 00 00` repeating from $0000. Offset $CC is a multiple of 4, so $CC and $CD are $FF.
- The `-memclear` switch offers patterns 0–7. Setting it to -1 picks a random pattern at each reset "for nostalgia's sake."

This explains why a default AppleWin power-on shows `.973136996`.

**[M12] Gregori, L. "C64 BASIC — How I fixed RND." 2020-05-24.**
URL: https://www.larsgregori.de/2020/05/24/c64-basic-how-i-fixed-rnd/ (fetched).
The context is an emulator fix. It describes C64 `RND(0)` as reading the CIA timer registers ($DC04/$DC05/$DC08/$DC09), and `RND(-TI)` as seeding from the jiffy clock at $A0–$A2. It is a secondary source (b), used only for the deck's Commodore Q&A answer.

### 1.5 Cited by fetched sources, but NOT fetched or read by me (no claims rest on these)

- **[X1] Modianos, D. T., Scott, R. C., & Cornwell, L. W. (1987). "Testing intrinsic random-number generators." *Byte* 12, 175–178.** Cited by [A4]. I did not find an online copy. What I know of its content comes only from a search-engine summary whose source page I couldn't identify: the article "surveyed a number of random-number generators on nine microcomputers, with some generators, particularly those of the Apple IIe, being flawed either for statistical reasons or because they have short cycles."
- **[X2]** *Superseded:* the Call-A.P.P.L.E. January 1983 scan has since been fetched and read. See [P5] and [P6].
- **[X7] Afflerbach, L. (1985). "The pseudo-random number generators in Commodore and Apple microcomputers." *Statistische Hefte* 26, 321–333** (doi:10.1007/BF02932542). The metadata is verified via Crossref, and the paper is cited by [A6]. The text is closed access and I have not read it. **This is the most likely academic structural analysis of the Microsoft-derived generator, and the top follow-up if anyone can get a copy.**
- **[X8] Lordahl, D. S. (1988). "Repairing the Microsoft BASIC RND function." *BRMIC* 20(2), 221–223** (doi:10.3758/BF03203835). Metadata verified via Crossref; cited by [A6]. Not read; the Springer PDF returned a login page.
- **[X9] Strube, M. (1983). "Tests of randomness for pseudorandom number generators." *Behavior Research Methods & Instrumentation* 15(5), 536–537** (doi:10.3758/BF03203701). Metadata only. Not read, and it isn't known whether it covers Applesoft.
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

**C6. Who wrote "RND is Fatally Flawed"?** *Resolved:* David Sparks, Call-A.P.P.L.E. Staff Writer. The byline and the issue's menu page are in the January 1983 scan [P5], and Vokey et al. (1986) cite it the same way (a).

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

**C13. Does Woz's Integer BASIC generator skip values? [P4] says yes; the ROM code says no.**
- (a) [P4] (Aug 1981) reports that the algorithm "generates the values between $6000 and $60FF twice, and never generates $2000-20FF at all!"
- (a) The original Apple II ROM image (`Apple2.rom`, [O5] repository) holds exactly the bytes shown in [M3] at $EF4E–$EF7F (`20 15 e7 a5 4e 20 08 e7 a5 4f d0 04 c5 4e 69 00 29 7f 85 4f …`).
- (c-emu) `tools/intbasic_rnd_emu.py` runs that ROM code under py65 with [P4]'s own calling convention (JSR $EF51, X=$20), for 32,768 calls with no keyboard wait in between. The 15-bit working value takes **32,767 distinct values**, every value from $0001 to $7FFF exactly once. The $2000–$20FF block is hit 256 times, and so is the $6000–$60FF block. An independent Python model of the listing agrees (cycle of 32,767 from every start tested).
- The defect [P4] reports is therefore most likely in the author's stand-alone port or his test, not in Woz's ROM (c). I did not examine the printed port byte by byte.
- (c-emu) There is a real, ordinary bias in the same generator, from reducing the 15-bit value modulo the argument. With `RND(1000)`, output buckets 0–699 get about 3,300 hits each while 800–999 get 3,200, because 32,767 mod 1000 = 767. The bias is negligible for small arguments such as `RND(6)`.

**C14. Two 1983 loop-length claims that the ROM code does not reproduce.**
- (a) Sparks [P5] reports "instances of seeds which lead to repeating sequences only a few dozen values in length."
  - (c-emu) In 272 emulated starts (256 cold-start $CD values plus 16 `RND(-n)` reseeds), the shortest loop was 202. I did not sweep all reseed arguments, so some seeds with shorter loops may exist.
- (a) Sparks reports that Crawford seeded with `RND(-1)`, "tested it to 10 million values," and found no repeat.
  - (c-emu) On the Apple ][+ ROM, `RND(-1)` enters the 37,758 loop after 1,060 calls, so the first repeat is at call 38,818.
- **Possible explanations (c):**
  - Crawford's test may have looked for something other than an exact repeat.
  - Crawford (1981) may have been using Applesoft from cassette, disk or a firmware card rather than the II+ ROM.
  - Sparks's "few dozen" may refer to repeating *output patterns* (for example in a scaled or integer use) rather than seed loops.

  None of these is verified. Treat both period claims as unconfirmed and don't put them on a slide.

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
- Added for §7:
  - txbobsc.com aal8108
  - 6502disassembly.com IIc_16kb and Unenh_IIe_80col
  - raw GitHub AppleWin `source/Core.cpp`, `source/Memory.cpp`, `source/Memory.h`, `help/CommandLine.html`
  - larsgregori.de
  - archive.org metadata API for [O1] (it carries no date field; the ©1978 comes from the OCR text)
- Knuth's TAOCP page
- api.crossref.org ×3
- Added for the slide 8 verification:
  - archive.org scans and OCR of *Call-A.P.P.L.E.* January 1983 (`call-apple-1983-01`), January 1982 (`call-apple-1982-01`), February 1982 (`call-apple-1982-02`), plus March and June 1982 (searched only)
  - archive.org scan and OCR of *MICRO* No. 72 (`micro-6502-journal-72`), and the archive.org advanced-search API
  - api.crossref.org reference lists for 10.3758/BF03200985, BF03200841, BF03203701 and BF03203334, plus bibliographic queries for Lordahl, Afflerbach and Strube
  - api.semanticscholar.org (metadata only; no abstracts are exposed)
  - scholar.ulethbridge.ca (Vokey's publication list)
  - the GS WorldView page again, as raw HTML, for Moore's affiliation
- Not retrievable: Springer PDFs for Strube, Lordahl, Heth and Brysbaert (login page); *Call-A.P.P.L.E.* 1981 issues (not on archive.org)

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

Two more scripts were added for §7:
- `tools/rnd_distribution.py <Apple2_Plus.rom>` produces the first-value-per-$CD and uniformity figures in `tools/distribution_results.jsonl`.
- `tools/intbasic_rnd_emu.py <Apple2.rom> 32768 1234 1000` runs the Integer BASIC ROM `RND` (results in `tools/intbasic_results.txt`).

The reboot-demo result in H1 came from a short inline run using `rnd_emu.py`: power-on with $CD=$FF, `RND(1)`, rewrite $C9–$CC as the cold start does, then `RND(1)` again.

---

## 6. Claim tally (after re-reading this file, 2026-09-12)

I re-read the whole file against the fetched material. That pass fixed:
- a leftover bracketed paraphrase in C4
- a wrong cross-reference in [A2]: Knuth's rules are in [P1], not [P2]
- an [X1] summary I had mis-attributed to [A6]
- overclaims in F3 and F10

Each of the 45 numbered items in §2–§4 is counted once, at the status of its slide-facing claim. C13 and C14 were added during the deck review, and C6 moved from U to V2 once the Call-A.P.P.L.E. scan was read:

| Status | Meaning | Count | Items |
|---|---|---|---|
| **V2** | Verified: fetched, and ≥ 2 independent sources ([M2] is not counted as independent of [M1]) | **16** | F1–F9, C3, C6, C8, Q1, Q11, Q13, Q15 |
| **V1** | Verified: fetched primary source, single-sourced | **9** | F10, F11, C7, Q3, Q4, Q14, Q16, Q17, Q19 |
| **E** | Reproducible emulation of the genuine ROM (c-emu); no published source | **10** | C1, C4, C13, C14, Q5, Q5b, Q7, Q8, Q9, Q12 |
| **I** | Inference or arithmetic (c) | **6** | C10, C11, Q2, Q6, Q10, Q18 |
| **U** | Unverified or open | **4** | C2 (open question), C5, C9, C12 |

**Verified: 25 of 45. Unverified or open: 4 of 45. The other 16 are my own emulation (10) or inference (6).** The deck review has its own tally in §7.6.

**Constants and addresses.** These are double-sourced:
- `RND` at $EFAE, CON_RND_1/2 bytes, and RNDSEED $C9–$CD
- initial seed $F123, copy count $F150/$F151
- KEYIN $FD1B, RNDL/RNDH $4E/$4F

These are single-sourced, and flagged here so nobody over-relies on them:
- the Microsoft `RNDX` fifth byte ($59), from [O4] only
- Integer BASIC `RND` at $EF4E, from [M3] only; [P1] confirms the behavior but not the address
- IIe `WAITKEY1` at $C27D, from [O3] OCR only
- the source line numbers in [O4]

(The Integer BASIC $EF4E address has since been double-sourced from the ROM image; see C13.)

---

## 7. SUPPORT FOR THE EXISTING DECK

### The artifact

- **File:** `deck/Applesoft_Loaded_Dice_Deck_1.pptx`, MD5 `e5e25ee084ebe40119020c764230ac2b`, revision 2, `lastModifiedBy` Jeff Robison, modified 2026-09-13T03:24:31Z.
- **Title slide:** "Applesoft's Loaded Dice — The Truth About Randomness on the Apple II, Then and Now", Jeff Robison, VCF Midwest 21 2026.
- **What I reviewed:** all 10 slides' text, all 10 speaker-note pages, and all 11 embedded images. The images are on slide 5 (four Monitor/IIe/IIc KEYIN listings and the Integer BASIC `RND` listing), slide 6 (the Applesoft `RND` listing), and slide 7 (four Applesoft manual excerpts, plus the `.973136996` screen grab).

**The presenter is Jeff Robison**, so everything below is written as recommendations for him.

Slide numbers below are the deck's physical order. The deck's printed page numbers are inconsistent; see §7.5.

### 7.1 Framing check: the deck does not claim biased output, and the evidence says it shouldn't

The scope-change note described the deck's thesis as "Applesoft RND is biased/non-uniform, not merely predictable." **The deck does not say that.** Its actual argument is a seed regression:
- Integer BASIC (1977) seeded from the live $4E/$4F KEYIN counter (slides 4–5).
- Applesoft (1978) takes its seed from ROM at boot, so a cold boot prints the same first number (slides 2, 6, and the notes).

"Loaded dice" is a metaphor for a predetermined roll. No slide or note asserts a skewed distribution.

**Evidence on distributional bias, for Q&A and for anyone tempted to add a bias claim:**
- (a) Kaner & Vokey [A3]: on the first 10,000 numbers, Applesoft `RND` "failed only the triplets test." It passed the frequency tests on that batch. Its documented failure is the loop of 202.
- (c-emu) I ran the genuine ROM routine from the deck's own boot state ($CD=$FF), with die rolls `INT(RND(1)*6)+1` over one full 37,758-value cycle (`tools/rnd_distribution.py`, `tools/distribution_results.jsonl`):
  - Face counts were 6,377 / 6,211 / 6,228 / 6,314 / 6,285 / 6,343, giving χ² = 3.34 at 5 degrees of freedom. The 5 % critical value is 11.07, so no bias is detectable.
  - Over the first 600 calls, χ² = 5.2 (5 degrees of freedom), also not significant.
  - Ten equal bins give χ² = 7.92 (9 df; critical value 16.92), and 256 bins give χ² = 239 (255 df).
  - The mean is 0.49987, and the lag-1 serial correlation is −0.004.
- (a) Gleason 1988 [A5] ran frequency and serial-correlation tests, but I haven't read the results.
- **Conclusion: no source I have, and none of my measurements, supports "Applesoft's output is non-uniform."** The dice are fair; they roll the same sequence every time, and the sequence is short.

Recommendation: keep "loaded" as the metaphor for a predetermined roll, and don't add a bias claim. If someone asks whether the dice are actually loaded, the defensible answer is "No — fair dice that always roll the same sequence."

### 7.2 HIGH severity: the deck says something the sources contradict or can't support

**H1. Slide 1 notes: "boot the machine cold, PRINT RND(1), reboot, same number. Do it three times." Slide 2 shows `.973136996`.**
- (c-emu) `.973136996` is the first `RND(1)` only when the uninitialized fifth seed byte $CD is **$FE or $FF** at power-on. Across all 256 possible $CD values there are **181 different first values**. For example, $CD=$00 gives `.270011996`.
- (a) AppleWin's default power-on RAM pattern puts $FF at $CD [M11]. The screen grab is consistent with that; I haven't confirmed which machine or emulator produced it.
- (c-emu) **A reboot that re-runs Applesoft's cold start without wiping RAM will not repeat it.**
  - After the first `RND(1)`, $CD holds **$94**.
  - The cold-start copy restores only $C9–$CC (F5).
  - So every later boot prints **`.676261996`**, not `.973136996`. The demo gives a different number the second time, and after that `.676261996` repeats.
  - A true power cycle repeats `.973136996` only if that RAM powers up the same way. AppleWin's default does; real hardware is unmeasured (C2). If AppleWin is set to `-memclear -1` (random pattern), the value varies from one power cycle to the next.
- **Recommendation:** rehearse on the exact show machine. "Reboot" must mean a power cycle, not Ctrl-Reset or `PR#6`. Or reword to "same number every power-on on this machine."
- I did not test whether a DOS 3.3 boot, or a IIe Ctrl-OpenApple-Reset, writes $CD.

**H2. Slide 6 speaker notes (and the duplicate notes on slide 7): "the seed comes from $C9, which got a fixed value out of ROM at boot."**
- (a) Only **four of the five** seed bytes ($C9–$CC) get a fixed value.
- The copy loop `F150: A2 1C LDX #$1C` never writes $CD. This is triple-sourced: ROM bytes [O5], S-C DocuMentor "<<< THE LAST BYTE OF THE RANDOM SEED IS NOT COPIED INTO PAGE ZERO! >>>" [M1], and AAL May 1984 [P1]. Microsoft's source shows the cause, `LDXI RNDX+4-CHRGET` [O4].
- **Slide 8 already credits AAL with "The seed copy is off by one," so the notes contradict the deck's own sources slide.**
- The off-by-one byte is exactly what decides which number slide 2 shows (H1), so it strengthens the talk.
- **Fix:** "four of its five bytes come from ROM; the fifth is whatever was in RAM, and Microsoft's own source has the off-by-one."

**H3. Slide 8: "Kaner & Vokey, 1982 — First published account."**
- (a) **Contradicted on both counts.**
- **The date.** The article was published in *MICRO* No. 72, June 1984, pp. 26–35. Four sources confirm it: the archive.org scan of that issue [A3], the manuscript's own header, AAL June 1984 [P2], and Heth's 1984 citation. "1982" is the manuscript copyright, and the printed article says the generators were developed in "summer, 1981."
- **"First."** Every one of these appeared in *Call-A.P.P.L.E.* before June 1984:
  - Tom Crawford, "Applesoft Random Function," **February 1981** [P7]. Per [P5], it reported repetition "after a few thousand calls."
  - Dave Lingwood, *Call-A.P.P.L.E. in Depth #1*, **1981**, on $CD not always being initialized [P8].
  - Sparks's RNDGEN, **May 1982** [P5].
  - Sparks, "RND is Fatally Flawed," and Hare/Russ/Faulkner, "A New Pseudo-Random Number Generator," both **January 1983** [P5][P6].
- **Fix:** "Kaner & Vokey — written 1982, published *MICRO* June 1984."
  - The earliest account on this record is Crawford, *Call-A.P.P.L.E.*, February 1981. The index verifies it, but I haven't read the article.
- "Dr. Kaner sent me the paper directly" is consistent with the kaner.com manuscript, which differs from the printed text (see H5).

**H4. Slide 8: "Aldridge 1987, Gleason 1988 — Behavior Research Methods. ERIC EJ372427."**
- (a) **This conflates two papers.**
  - Aldridge: *Behavior Research Methods, Instruments, & Computers* 19(4):397–399, July 1987 (doi:10.3758/BF03202585) [A4].
  - Gleason: *Collegiate Microcomputer* 6(2):108–112, May 1988; **EJ372427 is Gleason's ERIC record** [A5].
- **Fix:** "Aldridge 1987, *Behavior Research Methods, Instruments & Computers*; Gleason 1988, *Collegiate Microcomputer* (ERIC EJ372427)."

**H5. Slide 8 notes: "The 202 figure is measured, from the paper, on real Applesoft." No 202 appears anywhere on the slide.**
- (a) **What 202 is: a cycle length**, not a count of distinct values. The manuscript [A3] says "between the 10,000th and the 20,000th number generated, RND fell into an endless loop, repeating itself every 202 numbers."
- (a) **It comes from the manuscript and apparently isn't in the printed article.**
  - The *MICRO* No. 72 OCR contains no "202", "endless" or "miserably". Its only Applesoft verdict is "RND, when subjected to standard statistical tests, fails them badly."
  - The copy Dr. Kaner sent Jeff is presumably the manuscript, so "from the paper" is true of that copy. Cite it as the manuscript.
  - OCR can miss digits, so check the scanned pages 29–31 before stage.
- (a) **There is independent published corroboration from 17 months earlier.** Hare/Russ/Faulkner, *Call-A.P.P.L.E.*, January 1983: `RND` "can fall into one of several rather short (as little as 200) repetitive loops" [P6].
- (c-emu) The ROM code has a 202 loop, but it is one of five: 37,758, 32,366, 12,559, 4,082 and 202.
  - **From the deck's own boot state ($CD=$FF, `.973136996`), `RND` produces 44,576 distinct values** (6,818 before entering the loop, plus the 37,758 loop) **and never enters the 202 loop.**
  - AAL May 1984 [P1] measured 37,758. Across all 256 power-up values of $CD, 23 % end in the 202 loop.
- **Recommendation:** either put it on the slide, scoped correctly, or cut the note. Scoped wording: "Can get stuck in a 202-number loop (Kaner & Vokey manuscript; Hare/Russ/Faulkner 1983: 'as little as 200'). From a cold boot it gives 44,576 values, then repeats every 37,758."

**H6. Slide 6 notes (also duplicated on slide 7): "Twenty-six instructions."**
- (a) The listing on the slide (image6, $EFAE–$EFE7, identical to [M2] and to the ROM [O5]) has **28 instructions**.
- An audience member counting along will catch it. **Fix:** "twenty-eight instructions."

**H7. Slide 8: "Sander-Cederlof, AAL May 1984 — Found the startup bug. The seed copy is off by one."**
- (a) **"Found" is contradicted.** Sparks, *Call-A.P.P.L.E.*, January 1983 [P5], sixteen months earlier:
  - identified `$F150 LDX #$1C` as "the bug"
  - gave the `LDX #$1D` fix
  - named the missing byte ($58) and its location ($CD)
  - credited Dave Lingwood's 1981 *In Depth #1* article with first showing that $CD "isn't always initialized to the same value" [P8]
- AAL May 1984 itself opens by citing that Call-A.P.P.L.E. article [P1].
- AAL does document the bug correctly ("Changing $F151 from $1C to $1D would fix it"), so it remains a good citation. It just isn't the discovery.
- **Fix:** "Sparks, Call-A.P.P.L.E. Jan 1983 — found the off-by-one seed copy (`$F150 LDX #$1C`); Lingwood 1981 had noticed the symptom; Sander-Cederlof, AAL May 1984, published the fix."

### 7.3 MEDIUM: supportable with a caveat, or worth tightening

**M-a. Slide 4, "Integer BASIC, 1977 — Known period with limited range / No Floating point / Sufficiently random."**
- (c-emu) "Known period" is supported. The genuine ROM seed update is a maximal 15-bit sequence of **32,767**, every value $0001–$7FFF once (C13).
- "No floating point" (a) is correct.
- "Sufficiently random" is an opinion; no published test of Integer BASIC `RND` exists in what I found. Two caveats if challenged:
  1. `RND(X)` reduces the seed modulo X, so large arguments are mildly biased: `RND(1000)` buckets 0–699 get about 3,300 hits each and 800–999 about 3,200 (c-emu).
  2. The counter only advances while KEYIN waits, so repeated `RND` calls with no keypress in between are deterministic (a, [O2][P4]).
- Suggested wording: "good enough for games."

**M-b. Slide 4 citation, "Sander-Cederlof, Apple Assembly Line, August 1981."**
- **Verified** [P4]: "Random Number Generator from Integer BASIC," AAL 1(11). It supports "Integer BASIC reads it," names "Woz's algorithm," and places the monitor increment at $FD1B–$FD24.
- **Landmine:** the same article claims Woz's generator "never generates $2000-20FF at all" and generates $6000–$60FF twice. The genuine ROM code does not do that (C13, c-emu). A knowledgeable questioner may raise it. The answer: the bug was in the article's own stand-alone port or test, not the ROM.
- Don't cite this article as evidence that Integer BASIC's output is good.

**M-c. Slide 5, "Present in some form in all Apple II ROMs," with four 6502disassembly.com URLs.**
- **All four URLs fetched, and each matches the image on the slide:**
  - OrigF8ROM and AutoF8ROM: `fd1b: e6 4e KEYIN inc RNDL`.
  - Unenh_IIe_80col: `cb15: e6 4e GETKEY inc MON_RNDL ;bump random seed` (also `c2d5`).
  - IIc_16kb: `cc71: e6 4e inc RNDL ;update seed`.
  - The enhanced IIe's `C27D WAITKEY1 ;bump random seed` is in the IIe Technical Reference Manual [O3].
- The Integer BASIC image on slide 5 matches the original ROM bytes at $EF4E exactly (C13).
- **Not checked:** IIc Plus and IIgs. "All" is slightly more than I can source; "every 8-bit Apple II ROM" is safer, or keep "all" and be ready to hear about the IIgs.
- For a stronger slide, add Apple's own words: the 1979 Apple II Reference Manual p. 32, "Random Number Seeding … the exact value of which is quite unpredictable. Many programs and languages use this number as the base of a random number" [O2]. The 1985 IIe manual adds "no way to predict what it will be" [O3].

**M-d. Slide 5 notes: "Sit there two seconds and it's gone round tens of thousands of times."**
- (c) The II+ KEYIN loop takes 15 CPU cycles per increment. That is about 68,000 increments per second at 1.02 MHz, **≈136,000 in two seconds**, or about two full wraps of the 16-bit counter.
- Aldridge says it wraps "in less than a second" [A4].
- "Tens of thousands of times" understates the increments, and it overstates the wraps if "gone round" means wraps.
- Suggested wording: "sixty-some thousand counts a second — it wraps roughly once a second." The IIe and IIc loops differ and I haven't timed them.
- The note that "the counter gets bumped before the keyboard is read, every pass" is correct (a) [O2][M4].

**M-e. Slide 9, the two-part patch: "patch code into the LC at $F5CB (may impact HFIND, supposedly unused by AppleSoft)" and "JMP $F5CB at $EFAE."**
- (a) [M2] labels $F5CB "HFIND – calculates current position of hi-res cursor."
- (c) A search of the full Applesoft disassembly finds **no internal reference** to HFIND other than its own definition, so "unused by Applesoft" holds *for the ROM itself*.
- HFIND remains a fixed entry point (`CALL 62923`) that third-party hi-res code could call; I found no Apple manual documenting it.
- $EFAE is the correct `RND` entry (F1).
- **I could not verify** the claim that the patch "preserves negative and zero `RND()` functionality," or that the patch fits inside HFIND. `LC_Loader.bin` and `Patch_lc.bin` are not in the workspace, and I did not go looking for the presenter's repository.
- Two Q&A caveats, both sourced:
  1. The counter does not move in programs that poll `$C000` with `WAIT`/`PEEK` [M7].
  2. Turnkey programs never wait in KEYIN [A4].

  The patch adds no unpredictability in either case.

**M-f. Slide 7, "Applesoft Manual, 1978."**
- **Supported.** Images 7–10 match, word for word, the Applesoft BASIC Programming Reference Manual OCR (the `RND` entry and its three argument cases), and that copy is marked "©1978 by APPLE COMPUTER INC." [O1].
- Aldridge quotes the same wording from a 1981 printing [A4], so the text was unchanged by 1981.
- **A strengthening fact:** Aldridge (published 1987; the contact date isn't given) reports that an Apple representative recommended `X=RND(-1*(PEEK(78)+256*PEEK(79)))`. Apple's own support told users to hand-feed $4E/$4F into `RND`, which is the case for slide 9 in Apple's words.
- Edge case (c): if both bytes are zero, that line is `RND(0)` and doesn't reseed.

**M-g. Slide 6, "Applesoft, 1978 / Takes the seed at $C9, multiplies, adds, swaps two bytes around, forces the result under 1, writes it back to $C9."**
- The description matches the code (F2) (a).
- "1978" agrees with Wikipedia's Applesoft II release year (b) and the manual's ©1978 (a). The listing shown is the Apple ][+ ROM, and its bytes match [O5].
- If the talk names the swapped bytes, say "the highest and lowest mantissa bytes." Don't repeat AAL's "middle two bytes," which is wrong (C3).
- **Worth adding for this audience:** the constants `98 35 44 7A` and `68 28 B1 46` (11,879,546 and ≈3.93×10⁻⁸) are each **one byte short of a float, and they are short in Microsoft's own 1978 source** (`RMULZC`/`RADDZC`, in octal) [O4]. That backs the deck's "Microsoft's code, not Woz's" point with Microsoft's own listing.
- Sander-Cederlof's listing comment "VERY POOR RND ALGORITHM" [M1] is a quotable one-liner.

### 7.4 Per-slide list of what would strengthen each slide

| Slide (physical) | Add or cite | Label |
|---|---|---|
| 1 | Demo caveat, H1 | (c-emu) |
| 2 `.973136996` | Footnote: "Apple ][+ ROM, power-on with $CD=$FF (AppleWin default); a different power-up byte gives a different number" | (c-emu), [M11] (a) |
| 3 PRNG definition | Kaner & Vokey: `RND` "fails [standard statistical tests] miserably"; lattice background from [A3] or Knuth, if wanted | (a) |
| 4 Integer BASIC | AAL Aug 1981 (verified); ROM header "By Steve Wozniak, Copyright 1977"; period 32,767 | (a); (c-emu) |
| 5 $4E/$4F | Apple II Reference Manual (1979) p. 32 and IIe Tech Ref (1985) quotes; all four URLs verified | (a) |
| 6 Applesoft `RND` | Constants short in Microsoft's 1978 source; S-C "VERY POOR RND ALGORITHM"; fix H2 and H6 | (a) |
| 7 Manual | Aldridge's Apple-rep workaround; manual ©1978 verified | (a) |
| 8 Sources | Fix H3 and H4; add AAL Aug 1981, Microsoft BASIC-M6502 source, and Moore, *Sourceror's Apprentice* (April 1989), the original behind Empson's write-up [P3]; Aldridge's contaminated psychology experiment | (a) |
| 9 Patch | Aldridge turnkey caveat; Applefritter `WAIT` caveat; no internal HFIND references | (a), (b), (c) |
| 10 Q&A notes | C64 answer supported: Microsoft's source has a Commodore-only branch (`REALIO=3`) that loads VIA timer bytes for `RND(0)` [O4]; C64 CIA timers and `TI` [M12]; "same instruction for instruction" [M5] | (a), (b) |

### 7.5 LOW: housekeeping I noticed while extracting

- **Printed page numbers:** slides 6 and 7 both show "5", slide 8 shows "7", and slide 9 shows "9" (there is no 8).
- **Duplicated speaker notes:** slide 3's notes repeat slide 2's ("The amber box is the part that has to land. Slide 4 depends on it."), and slide 7's notes repeat slide 6's.
- **Slide 8, "Empson, GS WorldView 1999 — Built Moore's LFSR":**
  - The article presents a shift/XOR generator from Robert C. Moore's April 1989 *Sourceror's Apprentice* article [P3]. Crediting Moore 1989 alongside Empson is more accurate.
  - "LFSR" fits its 2²⁵−1 period (c), though the article itself says "cyclic shift/XOR."
- **Slide 5 notes, "The disassembly is Paul Santa-Maria's work, converted by Andy McFadden":** verified from the IntegerBASIC.html header (a). "Woz wrote Integer BASIC with no assembler … binder" is outside my sources.
- **Slide 4 notes, "$4E/$4F is not a jiffy clock":** consistent with [O2][O3]. The counter only moves inside keyboard-wait loops.

### 7.6 Tally for this section

- **Deck statements contradicted by fetched sources:** 5. They are H2 (seed "fixed" versus the uncopied fifth byte), H3 ("first published," 1982), H4 (Gleason venue and ERIC number), H6 (26 versus 28 instructions), and H7 (Sander-Cederlof "found" the startup bug).
- **Deck statements that are right but will mislead as phrased:** 2. They are H1 (the reboot demo) and H5 (202: a manuscript-only figure, and only one of five loops).
- **Deck statements verified:** 9. They are the slide 4 AAL Aug 1981 citation, the $EF4E address and listing, the four slide 5 URLs and listings, the slide 6 `RND` description and listing bytes, the slide 7 manual text and 1978 date, `$4E/$4F` as a keyboard-wait counter, the `.973136996` value (for $CD=$FF), the McFadden/Santa-Maria credit, and the C64 `RND(0)` timer answer.
- **Deck statements I couldn't verify:** the patch's preserved `RND(-n)`/`RND(0)` behavior and its size, "Woz wrote with no assembler," and "all Apple II ROMs" for the IIc Plus and IIgs. ("Dr. Kaner sent me the paper" is personal, but consistent with the manuscript version.)

### 7.7 Slide 8's source list, item by item

**1. Kaner & Vokey.**
- **Full citation:** Kaner, H. C. & Vokey, J. R., "A Better Random Number Generator," *MICRO* No. 72, June 1984, pp. 26–35; manuscript © 1982 [A3].
- **First?** No (H3).
- **What they measured:**
  - Spectral tests of their own three 40-bit LCGs: normalized U₂–U₆ scores from 2.37 to 7.40, where Knuth's "pass" is > 0.10.
  - Serial, Kolmogorov–Smirnov and runs tests on up to 850,000 numbers.
  - Full-period serial-correlation bounds.
  - Applesoft `RND` itself only in the manuscript: it failed the triplets test on the first 10,000 numbers, then fell into the 202 loop (H5).

**2. Call-A.P.P.L.E., January 1983.**
- **Citation:** Sparks, David, "RND is Fatally Flawed," *Call-A.P.P.L.E.* vol. 6 no. 1, January 1983, p. 29 onward (Technote) [P5]. Vokey et al. (1986) cite the pages as 29–34.
- The companion article is Hare, Russ & Faulkner, "A New Pseudo-Random Number Generator," p. 33 [P6]. It was an A.P.P.L.E. staff article, not a letter.

**3. Apple Assembly Line.**
- **May 1984:** Sander-Cederlof, "Random Numbers for Applesoft," AAL 4(8), https://www.txbobsc.com/aal/1984/aal8405.html [P1]. Verified, except for "found" (H7).
- **August 1981:** Sander-Cederlof, "Random Number Generator from Integer BASIC," AAL 1(11), https://www.txbobsc.com/aal/1981/aal8108.html [P4]. Verified; watch the landmine in M-b.

**4. Aldridge and Gleason.**
- Aldridge, *BRMIC* 19(4):397–399, 1987, doi:10.3758/BF03202585 [A4].
- **ERIC EJ372427 resolves** (https://eric.ed.gov/?id=EJ372427, fetched) to Gleason, J. M., *Collegiate Microcomputer* 6(2):108–112, May 1988. That journal is not *Behavior Research Methods* (H4).

**5. Empson and Moore.**
- Empson, "Apple II Random Number Generator," *GS WorldView*, November 1999 [P3].
- "Moore" is **Robert C. Moore**, Applied Physics Laboratory, Johns Hopkins University: "Random Bytes," *The Sourceror's Apprentice* 1(4), April 1989.
- "Built … for the Apple II" is fair: Empson supplies a 6502 routine for the simpler of Moore's two shift/XOR designs.
- Don't quote Empson's "4194962795."

**6. The 202 figure.** It is a loop length from the Kaner–Vokey manuscript, corroborated by Hare/Russ/Faulkner's "as little as 200." Details in H5.

**Worth adding to slide 8:**
- Crawford, *Call-A.P.P.L.E.* February 1981 (earliest report)
- Lingwood, *Call-A.P.P.L.E. in Depth #1*, 1981 ($CD symptom)
- Hare/Russ/Faulkner, January 1983 ("as little as 200")

### 7.8 The quantitative punchline: how much can `RND` produce from its fixed seed?

**Published figures** (all (a) unless noted):

| Source | Claim |
|---|---|
| Crawford, *Call-A.P.P.L.E.* Feb 1981 (via [P5]; article unread) | "after a few thousand calls, the RND function starts repeating itself" |
| Hare/Russ/Faulkner, Jan 1983 [P6] | "one of several rather short (as little as 200) repetitive loops" |
| Sparks, Jan 1983 [P5] | some seeds loop in "only a few dozen values" (not reproduced; C14) |
| Kaner & Vokey manuscript [A3] | a loop of 202, entered between call 10,000 and 20,000 |
| Sander-Cederlof, AAL May 1984 [P1] | "the repetition starts at the 37,758th 'random' number"; the Hi-Res plot stalls after ~7 minutes |

**No published source counts how many distinct values or sequences are reachable from the fixed ROM seed.** I searched for one and found nothing.

**The count, computed by running the genuine Apple ][+ ROM (c-emu):**
- From the ROM seed with power-on $CD=$FF, the deck's `.973136996` state: **44,576 distinct values, then an endless 37,758-value loop.**
  - That is 6,818 values before entering the loop, plus the 37,758 in it.
  - The float mantissa could hold 2³² = 4,294,967,296 values, so this is ≈ 0.001 % of the space.
- Across all 256 possible power-up values of $CD:
  - 181 different first numbers
  - every run ends in one of just **five loops**: 37,758, 32,366, 12,559, 4,082 or 202 values long
  - the longest run before repeating is 100,653 values
- **Suggested slide line:** "Room for four billion numbers. From a cold boot, Applesoft gives you 44,576 — then repeats forever." Label it as measured by running the ROM.
