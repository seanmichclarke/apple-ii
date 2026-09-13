# Sources

Each source is marked with how much of it the research team actually read:

- **Read**: full text retrieved and read.
- **Abstract**: metadata or abstract only.
- **Cited**: known only through another source. Nothing in the decks depends on these.

## Primary: code and ROMs

| Source | Status | Used for |
|---|---|---|
| Microsoft, *BASIC M6502 8K VER 1.1* source, `m6502.asm`. github.com/microsoft/BASIC-M6502 (released Sept 2025) | Read | Attribution, the `RND` routine, the four-byte constants, the seed-copy loop count, the Commodore timer build |
| Microsoft Open Source Blog, "Bringing BASIC back: Microsoft's 6502 BASIC is now Open Source," 2025-09-03 | Read | Port credited to Weiland & Gates |
| AppleWin `resource/Apple2_Plus.rom`, `Apple2e.rom`, `Apple2e_Enhanced.rom`. github.com/AppleWin/AppleWin | Read (bytes) | Ground truth; every emulator result |
| B. Sander-Cederlof, *S-C DocuMentor: Applesoft*. txbobsc.com/scsc/scdocumentor/ | Read | Labels and bug annotations, HFIND "not called by any Applesoft routine" |
| A. McFadden, Applesoft disassembly (SourceGen). 6502disassembly.com/a2-rom/Applesoft.html | Read | Slide 6 listing (derived from S-C DocuMentor, not independent of it) |
| A. McFadden, Original F8, Autostart F8, Integer BASIC, IIe 80-col and IIc disassemblies. 6502disassembly.com/a2-rom/ | Read | KEYIN listings, Integer BASIC `RND` at `$EF4E` |
| P. R. Santa-Maria, Integer BASIC disassembly (via McFadden) | Read | Integer BASIC `RND` |
| C. Mosher, Apple-II-Source `keyin.m4`. github.com/cmosher01/Apple-II-Source | Read | Reassembled KEYIN |
| M. Steil, *msbasic* byte-exact reconstruction. github.com/mist64/msbasic | Read | PET BASIC 1/2 `RND(0)` entropy addresses |
| M. Steil et al., C64 ROM disassembly. github.com/mist64/c64ref | Read | C64 `RND` constants, `RND(0)`, `TI` |

## Primary: Apple documentation

| Source | Status | Used for |
|---|---|---|
| *Apple II Reference Manual* ("Red Book"), Jan 1978 | Read (OCR) | KEYIN listing, "Random Number Seeding" p. 32 |
| *Applesoft II BASIC Programming Reference Manual*, ©1978 (030-0013-03) | Read (OCR) | `RND` semantics. The slide 7 scans probably come from a printing of this manual (open item B1) |
| *Applesoft BASIC Programming Reference Manual* (1981) | Read (OCR) | pp. 102, 159 `RND`, as quoted by Aldridge |
| *Applesoft Reference Manual* ("blue book"), Aug 1978 | Read (OCR) | ©1978 Apple / ©1977 Microsoft; its `RND(0)` wording differs from the code (check the scan) |
| *Apple IIe Technical Reference Manual* | Read (OCR) | Counter at `$4E/$4F` |
| S. Wozniak, "System Description: The Apple-II," *BYTE* 2(5), May 1977 | Read | "intended primarily for games and educational uses"; no timer or clock |

## Papers and period articles

| Source | Status | Used for |
|---|---|---|
| C. Kaner & J. R. Vokey, "A Better Random Number Generator for Apple's Floating Point BASIC," *MICRO*, June 1984, pp. 26–35 (manuscript ©1982). kaner.com/pdfs/random.pdf | Read (assembly sections removed by the author) | The 202-number loop |
| J. W. Aldridge, "Cautions regarding random number generation on the Apple II," *Behavior Research Methods, Instruments, & Computers* 19(4):397–399, 1987. doi:10.3758/BF03202585 | Read (asimov scan) | Power-on repeat; memory experiment; Apple's `PEEK(78)` advice |
| J. M. Gleason, "Statistical Tests of the Apple IIe Random Number Generator Yield Suggestions from Generator Seeding," *Collegiate Microcomputer* 6(2):108–112, 1988. ERIC EJ372427 | **Abstract** | Tested `RND`; suggested seeds |
| B. Sander-Cederlof, "Random Numbers for Applesoft," *Apple Assembly Line* 4(8), May 1984. txbobsc.com/aal/1984/aal8405.html | Read | Seed-copy bug and `$F151` fix; 37,758 |
| B. Sander-Cederlof, "More Random Number Generators," *AAL* 4(9), June 1984 | Read | Confirms the *MICRO* publication; constant typo |
| B. Sander-Cederlof, "Random Number Generator from Integer BASIC," *AAL*, Aug 1981. txbobsc.com/aal/1981/aal8108.html | Read | Integer BASIC generator |
| "RND is Fatally Flawed," *Call-A.P.P.L.E.* 6, Jan 1983, pp. 29–34 | **Cited** (by AAL May 1984) | Date and title only. Author unverified |
| D. Empson, "Apple II Random Number Generator," *GS WorldView*, Nov 1999 (on R. C. Moore, "Random Bytes," *The Sourceror's Apprentice* 1(4), 1989) | Read | Community replacement generator |
| Modianos, Scott & Cornwell, "Testing intrinsic random-number generators," *Byte* 12, 1987 | **Cited** | Not used |

## History and context

| Source | Status | Used for |
|---|---|---|
| M. Steil, "Create your own Version of Microsoft BASIC for 6502" and "Microsoft BASIC for 6502 Original Source Code [1978]," pagetable.com | Read | Lineage; seed-copy bug in every version |
| S. Weyhrich, *Apple II History*, chapters 3 and 16. apple2history.org | Read | Applesoft I/II development, Apple's edits |
| J. Szczepaniak, interview with S. Wozniak, *Game Developer*, 2012 | Read | "that'll free me up to work on other things" |

## "Now"

| Source | Status | Used for |
|---|---|---|
| Debian Security Advisory DSA-1571-1, "openssl: predictable random number generator," May 13, 2008; CVE-2008-0166 | Well-known public record; not re-fetched this session | Parallel case only |
| ISO/IEC 9899 (C standard), `rand`/`srand` | Well-known | `rand()` with no seed behaves as `srand(1)` |
