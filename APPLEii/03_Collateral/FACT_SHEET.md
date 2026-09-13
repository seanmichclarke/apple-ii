# Fact sheet: every number on the slides, and where it comes from

**Labels:**
- **DOC**: primary source, read or fetched.
- **EMU**: measured by running the genuine ROM routine under py65. Anyone can reproduce it, but no published source backs it.
- **INF**: inference or arithmetic.
- **OPEN**: needs real hardware.

"Re-run 12 Sep" means the result was re-checked independently while building this package; see `04_Research_and_Evidence/VERIFY_LOG.md`.

| # | Claim as worded on slides | Label | Source | Checked |
|---|---|---|---|---|
| 1 | Applesoft `RND` is at `$EFAE`; the seed is 5 bytes at `$C9–$CD` | DOC | S-C DocuMentor; McFadden; AAL May 1984; ROM image | re-run 12 Sep |
| 2 | Seed table `$F123` = `80 4F C7 52 58` | DOC | ROM image, S-C DocuMentor | re-run 12 Sep |
| 3 | Cold start `LDX #$1C` at `$F150` copies 4 of 5 bytes; `$CD` is never set | DOC | ROM bytes `A2 1C`; S-C "LAST BYTE… NOT COPIED"; Microsoft `LDXI RNDX+4-CHRGET` | re-run 12 Sep |
| 4 | Fix: `$F151` from `$1C` to `$1D` | DOC | Sander-Cederlof, AAL May 1984 | |
| 5 | `$CD`=$FF or $FE → first `RND(1)` = .973136996 | EMU | `tools/verify_headline.py` | re-run 12 Sep |
| 6 | `$CD`=$00 → .270011996; $58 → .512199496; $AA → .738761996 | EMU | same | re-run 12 Sep |
| 7 | 256 `$CD` values → 181 distinct first numbers | EMU | same | re-run 12 Sep |
| 8 | Only power-on repeats; reboots don't | DOC | Aldridge 1987: "only when a machine is powered off and back on" | |
| 9 | Ctrl-RESET preserves the seed | EMU | `applesoft-rnd.md` §5.1 | |
| 10 | "exactly the same sequence each time the machine is powered on" | DOC | Aldridge, BRMIC 19(4):397–399, 1987 | |
| 11 | Loops of 37,758 / 32,366 / 202 / 4,082 / 12,559; shares 43.0 / 30.5 / 23.0 / 2.0 / 1.6 % of `$CD` values | EMU | `tools/cd_sweep_results.jsonl` (256 rows) | 202 re-run for $58 on 12 Sep |
| 12 | `$CD`=$58 enters the 202-loop after 15,382 calls | EMU | same | re-run 12 Sep |
| 13 | Kaner & Vokey: loop of 202, entered between call 10,000 and 20,000 | DOC | MICRO June 1984 (ms. © 1982), kaner.com PDF | |
| 14 | AAL: repeats from the 37,758th number | DOC | AAL May 1984 | |
| 15 | Multiplier as read = 11,879,546.40625 (`98 35 44 7A` + `68`) | DOC bytes + INF decoding | ROM; Microsoft source (octal) | bytes re-run 12 Sep |
| 16 | Addend 3.93×10⁻⁸ is lost to precision; changed 5 of 57,021 steps; first divergence at call 3,886 | EMU | `applesoft-rnd.md` §5.4, `exp_nofadd.jsonl` | |
| 17 | `RND(-1)` stores 2.99196472E-08 | EMU + DOC arithmetic | `applesoft-rnd.md` §4 | re-run 12 Sep |
| 18 | The swap exchanges `FAC+1` and `FAC+4` (high and low) | DOC | listing, Microsoft "REVERSE HO AND LO" | |
| 19 | The `RND` listing `$EFAE–$EFE7` has 28 instructions | DOC | counted from listing | |
| 20 | "very poor RND algorithm" is Sander-Cederlof's comment | DOC | S-C DocuMentor | |
| 21 | Applesoft never reads `$4E/$4F` | DOC | listing cross-reference; Aldridge "makes no use of the $4E-$4F value" | |
| 22 | Integer BASIC `RND` at `$EF4E` reads and rewrites `$4E/$4F` | DOC | Santa-Maria/McFadden disassembly | |
| 23 | Integer BASIC: 15-bit register, feedback bit14 XOR bit13, single cycle of 32,767 | EMU | `tools/intbasic_rnd_emu.py` | re-run 12 Sep |
| 24 | Whole Integer BASIC RNG = 56 bytes (6 in KEYIN + 50 in RND) | DOC bytes + INF count | DESIGN_INTENT §1.1 | |
| 25 | KEYIN `$FD1B`: `INC RNDL / BNE / INC RNDH` | DOC | Apple II Reference Manual; ROM | |
| 26 | ≈68,000 counts/s; wraps ≈ once a second | INF | 15 cycles/loop at 1.0205 MHz → 68,032/s, 0.963 s; Aldridge "less than a second" | re-run 12 Sep |
| 27 | Counter moves only while KEYIN waits; polling `$C000` doesn't advance it | DOC code + consensus | ROM; Applefritter 2021 | |
| 28 | Apple's advice: `X=RND(-1*(PEEK(78)+256*PEEK(79)))` | DOC | Aldridge 1987 | |
| 29 | Both counter bytes 0 → `RND(0)` path, no reseed | INF | `SIGN` returns 0 | |
| 30 | HFIND is at `$F5CB` and not called by any Applesoft routine | DOC | S-C DocuMentor | |
| 31 | No `JSR`/`JMP $F5CB` anywhere in `$D000–$FFFF` of the ][+ ROM | checked | byte scan 12 Sep | re-run 12 Sep |
| 32 | HFIND budget `$F5CB–$F5FF` = 53 bytes; `$F600` is an RTS that the branch at `$F59C` targets | checked | byte scan 12 Sep | re-run 12 Sep |
| 33 | `RND`, the constants, the seed and the init loop are byte-identical in ][+, IIe, enhanced IIe | DOC | AppleWin ROM images compared | |
| 34 | Microsoft's source has a hardware-timer `RND(0)` for Commodore only | DOC | BASIC-M6502 `IFE REALIO-3` | |
| 35 | Apple inserted `STX SPEEDZ` inside the seed-copy loop | DOC | ROM `$F157` vs Microsoft source | |
| 36 | Aldridge's memory experiment: repeated lists went to the first subjects each day | DOC | Aldridge 1987 | |
| 37 | Call-A.P.P.L.E. "RND is Fatally Flawed", Jan 1983, pp. 29–34 | DOC (title/pages via AAL) | author name unverified: don't print one | |
| 38 | Gleason 1988 tested IIe RND and suggested seeds | DOC abstract only | ERIC EJ372427; paper not read | |
| 39 | Debian OpenSSL CVE-2008-0166: 2006 change removed nearly all entropy; found May 2008 | DOC (public advisory) | Debian DSA-1571 | not re-fetched for this package |
| 40 | C `rand()` without `srand()` behaves as if seeded with 1 | DOC | ISO C standard, `srand` | |

## OPEN (never put these on a slide as fact)
- What `$CD` holds at power-on on any real machine, and whether DOS 3.3 or ProDOS writes it.
- What `Patch_lc.bin` does, and its length. The binary isn't in these files.
- ][+ Language Card / //e / //c behavior after Ctrl-RESET with the patch installed.
- The //c and IIgs Applesoft bytes.
- The edition and part number of the manual scans on slide 7.
- License fee figures ($21,000 vs $31,000 conflict). Keep them off slides.
