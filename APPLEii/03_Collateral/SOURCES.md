# Sources

This list includes only sources the research team actually fetched and read, unless an entry says otherwise. The full annotated record is in `04_Research_and_Evidence/LITERATURE.md` and `DESIGN_INTENT.md`.

## Period and academic
- Kaner, C. & Vokey, J. R. "A Better Random Number Generator for Apple's Floating Point BASIC." *MICRO*, June 1984, pp. 26–35 (manuscript © 1982). https://kaner.com/pdfs/random.pdf
- "RND is Fatally Flawed." *Call-A.P.P.L.E.* 6, Jan 1983, pp. 29–34. Title and pages were confirmed through AAL May 1984. The author name is unverified, and the article itself was not read.
- Sander-Cederlof, B. "Random Number Generator from Integer BASIC." *Apple Assembly Line*, Aug 1981. http://www.txbobsc.com/aal/1981/aal8108.html
- Sander-Cederlof, B. "Random Numbers for Applesoft." *Apple Assembly Line* 4(8), May 1984. https://www.txbobsc.com/aal/1984/aal8405.html
- Sander-Cederlof, B. "More Random Number Generators." *Apple Assembly Line* 4(9), June 1984. https://www.txbobsc.com/aal/1984/aal8406.html
- Aldridge, J. W. "Cautions regarding random number generation on the Apple II." *Behavior Research Methods, Instruments, & Computers* 19(4):397–399, 1987. doi:10.3758/BF03202585. Scan: https://www.apple.asimov.net/documentation/programming/misc/random%20number%20generation%20note.pdf
- Gleason, J. M. "Statistical Tests of the Apple IIe Random Number Generator Yield Suggestions from Generator Seeding." *Collegiate Microcomputer* 6(2):108–112, 1988. ERIC EJ372427. Only the abstract was read.
- Empson, D. "Apple II Random Number Generator." *GS WorldView*, Nov 1999, a write-up of R. C. Moore, "Random Bytes," *The Sourceror's Apprentice* 1(4), 1989. https://gswv.apple2.org.za/a2zine/GS.WorldView/v1999/Nov/Articles.and.Reviews/Apple2RandomNumberGenerator.htm
- Knuth, D. E. *The Art of Computer Programming*, Vol. 2, ch. 3. Used as background only, not read directly.

## Vendor primary sources
- Microsoft. BASIC-M6502 v1.1 source, `m6502.asm`. https://github.com/microsoft/BASIC-M6502
- Apple Computer. *Apple II Reference Manual* ("Red Book"), 1978: the KEYIN listing and "Random Number Seeding".
- Apple Computer. *Applesoft II BASIC Programming Reference Manual*, the RND entries.
- Apple Computer. *Apple IIe Technical Reference Manual*: the KEYIN counter at 78/79.
- Wozniak, S. "System Description: The Apple-II." *BYTE* 2(5), May 1977.

## Disassemblies and ROM images
- Sander-Cederlof, B. *S-C DocuMentor: Applesoft*. http://www.txbobsc.com/scsc/scdocumentor/
- McFadden, A. Applesoft, Integer BASIC (after P. Santa-Maria), OrigF8ROM, AutoF8ROM, IIc and IIe firmware disassemblies. https://6502disassembly.com/a2-rom/
- AppleWin ROM images `Apple2_Plus.rom` (SHA-1 `33a24f5489ba9195b44be77d9afb2252594cb5c7`), `Apple2e.rom` and `Apple2e_Enhanced.rom`. https://github.com/AppleWin/AppleWin/tree/master/resource

## Community and context
- Steil, M. pagetable.com: "Create your own Version of Microsoft BASIC for 6502" (?p=46), "Microsoft BASIC for 6502 Original Source Code" (?p=774), and the C64 disassembly (?p=728). The msbasic reconstruction: https://github.com/mist64/msbasic
- Weyhrich, S. *Apple II History*, ch. 3 and ch. 16. https://www.apple2history.org
- Applefritter, "Random number generation on the Apple II with AppleSoft BASIC", 2021.

## "Now" parallels
- Debian Security Advisory DSA-1571 / CVE-2008-0166, OpenSSL predictable random number generator (May 2008).
- ISO/IEC 9899 (C standard), `rand`/`srand`: if `rand` is called before `srand`, it behaves as though seeded with 1.
