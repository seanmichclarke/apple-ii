# Design Intent: Why the Apple II's Random Numbers Were Built This Way

*WOZNIAK / DESIGN-INTENT agent output for "The Problem of the Apple II RNG". Written 2026-09-12.*

This document argues the other side. The critique is about the machine as a whole: it had no entropy source, only the appearance of one. This document is here to make sure that critique hits the right target, for the right reasons, and with the right person's name on it.

## Evidence labels

Every claim carries one of these labels:

- **(a) documented fact:** primary source, ROM bytes, original listing, or a first-person quote.
- **(b) community consensus:** well-regarded secondary source, or broad agreement among historians and disassemblers.
- **(c) inference:** my reasoning. When I checked an inference by computation, I say how.

Source keys like [S1] resolve in the source list at the end.

---

## 0. The attribution in one paragraph (read this first)

The Apple II had **two unrelated RNGs by two different authors**:

- **Integer BASIC `RND`** at `$EF4E`, together with the **monitor's `$4E/$4F` keyboard counter** at `KEYIN $FD1B`, is Apple code.
  - Integer BASIC is by Steve Wozniak. [S1] (a)
  - The monitor ROM is credited "S. Wozniak, A. Baum". [S2] (a)
- **AppleSoft `RND`** at `$EFAE`, with its floating-point LCG, is **Microsoft's code**. It is byte-for-byte and instruction-for-instruction identical to `RND` in Microsoft's own released 6502 BASIC source. [S4][S5] (a)
  - That source credits its 6502 port to Weiland & Gates. [S5][S6] (a)
  - The math package it descends from is credited to Monte Davidoff in the 8080 source. [S8] (b: the 8080 credit line as quoted by Steil, primary not inspected; c that RND specifically was his)
  - Apple adapted and shipped AppleSoft and wrote its manuals. Apple did **not** write or modify its RNG. [S4][S5] (a)

**The LCG, its constants, its fixed cold-start seed, and the dropped fifth seed byte are not Woz's work.**

---

## 1. Design constraints of 1977

### 1.1 ROM: the byte budget

| Constraint | Value | Label / source |
|---|---|---|
| ROM sockets on the original Apple II board | Six sockets, `D0` `D8` `E0` `E8` `F0` `F8`, 2K each (`$D000–$FFFF`) | (a) Red Book memory map [S14] |
| Sockets populated at launch | `D0`, `D8`: "Spare". `E0`, `E8`: "BASIC". `F0`: "1K of BASIC, 1K of utility". `F8`: "Monitor". | (a) [S14] |
| ROM Woz describes | "the Apple-II's mask programmed 8 K bytes of read only memory" | (a) Byte, May 1977 [S10] |
| Monitor size | 2,048 bytes, up from 256 bytes on the Apple-1 | (b) [S13] |
| Integer BASIC region | `$E000–$F7FF`, shared with Woz's floating-point routines (`$F425…`), the Wozniak/Baum mini-assembler, and SWEET16 | (a) listing headers [S1] |
| Hi-res graphics routines | **Did not fit in ROM**; shipped on tape instead | (a) Woz: "(Even with 8 K bytes for the read only memory space, there sometimes isn't enough room to fit all the needed features.)" [S10] |
| Cost of the keyboard entropy collector | **6 bytes** (`$FD1B–$FD20`: `E6 4E D0 02 E6 4F`) | (a) bytes [S2]; count computed from addresses |
| Integer BASIC `RND`, complete | **50 bytes** (`$EF4E–$EF7F`) | (a) bytes [S1]; count computed from addresses |
| AppleSoft II, for comparison | ~10K (`$D000–$F7FF`, filling all five BASIC sockets) | (a) disassembly starts at `$D000` [S4]; (b) size [S18] |

(c) The whole Integer BASIC RNG, collector plus generator, cost **56 bytes** of an 8K ROM that could not even hold the hi-res routines. A dedicated seeding routine, a stored seed, or documentation strings would have competed with `PLOT`, `HLIN` and the paddle reader for that space.

### 1.2 No assembler: why retrofits were expensive

(a) Woz wrote Integer BASIC by hand and assembled it by hand:

> "I completely wrote and debugged Apple BASIC using the monitor as my only software development tool. It was of course the first hand assembled program I wrote for the system."
> — Wozniak, *Byte*, May 1977 [S10]

> "The BASIC, which we shipped with the first Apple II's, was never assembled – ever. There was one handwritten copy, all handwritten, all hand-assembled. So we were in an era that we could not afford tools."
> — Wozniak, quoted in Connick, *Call-A.P.P.L.E.*, Oct 1986, via [S13]

> "If I discovered that - oh my gosh - I've got to add a few bytes to this one routine, I had to put a jump out to somewhere else, do what was needed, then jump back in. It was absolute memory locations. So it was extremely clumsy."
> — Wozniak, interview with J. Szczepaniak, 2012 [S12]

(a) The disassembly header confirms: "there is no original assembly file for Integer BASIC. The entire program was written out by hand." [S1]

(c) This matters for the RNG. Any later improvement, such as a seed statement or a better generator, meant hand-patching absolute addresses in shipping mask ROM. Woz gives this exact reason for never wiring his own floating-point ROM routines into BASIC: "When you code by hand … it's hard to make changes in the middle structure of things that have to be at fixed addresses." [S11] (a)

### 1.3 Chips, parts, and money

| Item | Value | Label / source |
|---|---|---|
| Retail price, 4K | US$1,298 | (b) [S19] |
| Retail price, 48K | US$2,638 | (b) [S19] |
| 16K RAM chip cost during the design | "about $500" | (b) [S13] |
| Paddle "ADC" | No ADC chip. One 558 quad timer plus a software counting loop. | (a) Woz, Byte 1977 [S10]; (b) [S19] |
| Woz on part count | "I designed everything using very few parts. I was known for that at Hewlett-Packard." | (a) [S12] |
| DRAM refresh | No refresh circuit; the video scan refreshes memory for free | (a) [S10] |
| Total IC count, per-part ROM cost | **Not established.** None of the sources consulted gives a reliable total chip count or 1977 unit price for the 2K mask ROMs. I have not invented one. | stated gap |

### 1.4 Cycles

| Item | Value | Label / source |
|---|---|---|
| CPU clock | 1.0205 MHz average (65 CPU cycles per 912 master-oscillator periods; one cycle per line is stretched) | (b) [S22] |
| Cycles per video frame | ~17,000 (1.0205 MHz ÷ ~60 Hz) | (c) computed |
| Paddle read resolution | "12 μs per count" (Woz) / "[actually 11]" (Red Book listing comment); max count 255, so up to ~2.8 ms per read | (a) [S10][S2]; ms figure (c) computed |
| Interrupts | The monitor reads the keyboard by **polling** `$C000`. The IRQ handler only vectors through the user hook at `$3FE`. Nothing in the ROM runs on interrupts. | (a) [S2] |
| Interrupt hardware | The slot bus does support "prioritized interrupts" | (a) [S10] |
| Real-time clock | None on the motherboard. Byte 1977 lists every standard peripheral (keyboard, cassette, four paddles, three switches, four annunciators, speaker); no clock or timer chip appears. | (a) [S10] |

### 1.5 What the machine was for

(a) Woz, describing Integer BASIC in 1977: "It is intended primarily for games and educational uses." [S10]

(a) "I kept about 50 chronological folders of papers throughout all my BASIC design work. Each one was labelled GAME BASIC." [S11]

(a) "A lot of features of the Apple II went in because I had designed Breakout for Atari. I had designed it in hardware. I wanted to write it in software now." [S13]

---

## 2. What Woz built and why

### 2.1 The entropy collector: monitor `KEYIN`, `$FD1B`

From the original Apple II monitor ROM listing (Red Book, Jan 1978), via McFadden's SourceGen transcription. McFadden converted the comments to mixed case but otherwise left the wording unchanged. [S2] (a)

```
RNDL    EPZ  $4E
RNDH    EPZ  $4F

FD0C: A4 24     RDKEY   LDY CH
FD0E: B1 28             LDA (BASL),Y   ;set screen to flash
FD10: 48                PHA
FD11: 29 3F             AND #$3F
FD13: 09 40             ORA #$40
FD15: 91 28             STA (BASL),Y
FD17: 68                PLA
FD18: 6C 38 00          JMP (KSWL)     ;go to user key-in

FD1B: E6 4E     KEYIN   INC RNDL
FD1D: D0 02             BNE KEYIN2     ;incr rnd number
FD1F: E6 4F             INC RNDH
FD21: 2C 00 C0  KEYIN2  BIT IOADR      ;key down?
FD24: 10 F5             BPL KEYIN      ; loop
FD26: 91 28             STA (BASL),Y   ;replace flashing screen
FD28: AD 00 C0          LDA IOADR      ;get keycode
FD2B: 2C 10 C0          BIT KBDSTRB    ;clr key strobe
FD2E: 60                RTS
```

- (a) **Intent is on the page.** The 1978 listing comments the increment as "incr rnd number", and the zero-page cells are named `RNDL`/`RNDH`. This is a deliberate random-number facility, not an accident later exploited.
- (a) The same `KEYIN` code, at the same address, survives in the Apple II Plus Autostart ROM ("Steve Wozniak … Modified Nov 1978 By John A"). [S3]
- (c) **Rate.** The waiting loop is `INC zp` (5 cycles) + `BNE` taken (3) + `BIT abs` (4) + `BPL` taken (3) = 15 cycles. At 1.0205 MHz that is about **68,000 increments per second**, so the 16-bit counter wraps about every **0.96 s**.
- (c) **Consequence.** A human keypress timed to within tens of milliseconds lands on a counter value whose low byte is effectively unpredictable. That holds for game purposes, not against an adversary.
- (a) **Scope.** The counter advances only while the CPU sits in `KEYIN` waiting for a key. `KEYIN` is reached through `RDKEY` → `JMP (KSWL)` when the input hook points at `$FD1B`. [S2]
  - Code that polls `$C000` directly never reaches `KEYIN`. That includes Integer BASIC game loops using `PEEK(-16384)` and AppleSoft `WAIT 49152,128`, so the counter does not move.
  - (b) The `WAIT` case was observed in practice. [S21]
- (c) **Not verified here.** Whether the counter still advances when DOS 3.3 or an 80-column card replaces `KSW` depends on whether the hook chains to `$FD1B`. The review team should check before claiming either way.

### 2.2 Why a keyboard-wait counter was a reasonable entropy proxy in 1977

- (a) **No other free source was running.** No RTC, no timer chip, no interrupt-driven tick. [S10][S2]
- (c) **Zero added hardware, 6 bytes of ROM.** The loop already burned CPU cycles waiting for the operator, so turning dead time into state cost nothing.
- (c) **The one truly nondeterministic input was the human.** For a single-user machine running Breakout, the moment the player hits a key is the unpredictable event that matters.
- (c) **Always on.** The counter re-stirs at every keyboard wait (every `INPUT`, every command line), so it never needs an explicit seeding step the programmer could forget.

### 2.3 Integer BASIC `RND(X)`, `$EF4E`

From the Santa-Maria disassembly of the hand-assembled ROM. Labels as in [S1]. (a)

```
         ; Token $2f RND
EF4E: 20 15 E7  RND     JSR GET16BIT      ; X (the limit) -> ACC
EF51: A5 4E             LDA MON_RNDL      ; low byte of result = counter low
EF53: 20 08 E7          JSR LE708
EF56: A5 4F             LDA MON_RNDH
EF58: D0 04             BNE LEF5E
EF5A: C5 4E             CMP MON_RNDL      ; if RNDH=0: A = 1 iff RNDL=0
EF5C: 69 00             ADC #$00          ;   (zero-state guard)
EF5E: 29 7F     LEF5E   AND #$7F          ; keep 15 bits
EF60: 85 4F             STA MON_RNDH
EF62: 95 A0             STA NOUNSTKC,X    ; high byte of result
EF64: A0 11             LDY #$11          ; 17 iterations
EF66: A5 4F     LEF66   LDA MON_RNDH
EF68: 0A                ASL A
EF69: 18                CLC
EF6A: 69 40             ADC #$40
EF6C: 0A                ASL A             ; C = bit14 XOR bit13
EF6D: 26 4E             ROL MON_RNDL
EF6F: 26 4F             ROL MON_RNDH      ; shift feedback into bit 0
EF71: 88                DEY
EF72: D0 F2             BNE LEF66
EF74: A5 CE             LDA ACC
EF76: 20 08 E7          JSR LE708
EF79: A5 CF             LDA ACC+1
EF7B: 95 A0             STA NOUNSTKC,X
EF7D: 4C 7A E2          JMP MOD           ; result = state MOD X
```

Behaviour, derived from the bytes above and verified by exact emulation (`woz/intbasic_rnd_emu.py`):

- (c, verified) `RND(X)` returns the current 15-bit value of `$4E/$4F` **MOD X**.
- (c, verified) It then advances the state **17 steps** of a Fibonacci LFSR with feedback `bit14 XOR bit13`, the polynomial x¹⁵ + x¹⁴ + 1. The emulator confirms the feedback identity for all 65,536 register values.
- (c, verified) The state is written **back into the monitor's counter cells**, so `KEYIN` and `RND` share one register.
- (c, verified) Without keypresses, successive calls cycle with period **32,767** from every start state tested. The LFSR is maximal, and 17 is coprime to 32,767 = 7·31·151.
- (a) The `CMP`/`ADC #$00` pair forces an all-zero state to `$0100`. That is the textbook guard against LFSR zero lock-up.
- (c) The guard is evidence Woz knew what an LFSR needed.
- (a) **Documented semantics.** Red Book: `RND(expr)` "Gives random number between [0] and (expression expr -1) if expression expr is positive; if minus, it gives random number between [0] and (expression expr +1)." [S14] The bracketed zeros are dropped in the archive.org OCR text and restored here from context; check against the page scan before putting this on a slide.
  - (a) Raskin's *Apple II BASIC Programming Manual* says only that the values are "for most practical purposes, unpredictable". On negative arguments it says: "You can find out what it does with just a few experiments." [S15]
- (a) **No seed syntax.** Integer BASIC has no `RANDOMIZE` and no negative-argument reseed. The only seed is the keyboard counter. [S1]

(c) **Design reading.** This is a coherent, deliberate two-part design:

- a free, continuously re-stirred entropy pool (the keyboard counter), and
- a cheap whitening/stepping function (the 17-step LFSR) so that repeated calls between keypresses still vary.

It is the kind of thing a hardware engineer who "designed everything using very few parts" builds. It is not a naive `PEEK` of a counter.

---

## 3. Attribution

### 3.1 Who wrote what

| Component | Address | Author | Evidence | Label |
|---|---|---|---|---|
| `$4E/$4F` counter in `KEYIN` | `$FD1B` | Apple monitor ROM, credited "S. Wozniak, A. Baum" | Red Book listing header [S2] | (a) |
| Same, split between the two | — | Which of the two wrote `KEYIN` is **not documented**. Baum is described as helping with screen text and windowing. | [S13] | (b) |
| Same, Apple II Plus | `$FD1B` | Autostart ROM: "Steve Wozniak", "Modified Nov 1978 By John A"; `KEYIN` unchanged | [S3] | (a) |
| Integer BASIC `RND` | `$EF4E` | Steve Wozniak | ROM header "By Steve Wozniak"; hand-written, no source file [S1] | (a) |
| AppleSoft `RND` and constants | `$EFA6–$EFE9` | **Microsoft** | Byte-identical to `RND`/`RMULZC`/`RADDZC` in Microsoft's M6502 source [S4][S5] | (a) |
| AppleSoft cold-start seed | `$F123` | **Microsoft** | Same 5 bytes as Microsoft's seed constant [S4][S5] | (a) |
| Dropped fifth seed byte at init | `$F150` | **Microsoft** | Bug is in Microsoft's source (`LDXI RNDX+4-CHRGET`) and in every 9-digit Microsoft 6502 BASIC [S5][S7] | (a) source; (b) "every version" |
| Adapting AppleSoft to the Apple II, manuals, ROM integration in the II Plus | — | Apple staff, including Randy Wigginton | [S18] | (b) |

### 3.2 The proof that AppleSoft `RND` is Microsoft's code

**1. The constants match byte for byte.** (a)

The AppleSoft II ROM, from Sander-Cederlof's disassembly [S4]:

```
EFA6: 98 35 44 7A   CON_RND_1   ; multiplier
EFAA: 68 28 B1 46   CON_RND_2   ; addend
F123: 80 4F C7 52 58            ; initial seed ≈ .811635157
```

Microsoft `m6502.asm`, v1.1, released by Microsoft under the MIT licence in Sept 2025 [S5]. This code sits in the math package, which is assembled under `RADIX 8` ("!!!! ALERT !!!!", line 4847), so the values are octal:

```
; math package, RADIX 8 (lines ~6343-6352)
RMULZC: 230  065  104  172     ; octal = $98 $35 $44 $7A  -> 11879546
RADDZC: 150  050  261  106     ; octal = $68 $28 $B1 $46  -> 3.927677739E-8

; RAM-code section, RADIX 10 (lines 978-982)
RNDX:   128  79  199  82  IFN ADDPRC,<89>   ; "THE INITIAL RANDOM NUMBER."

; init-data copy, RADIX 10 (lines 6692-6696)
        128  79  199  82  IFN ADDPRC,<88>   ; = $80 $4F $C7 $52 $58
```

(The octal-to-hex conversion and floating-point decoding were computed and checked against the ROM bytes above. The source holds two copies of the seed. The first four bytes are identical in both; the fifth is 89 in the `RNDX` copy and 88 in the copy used at initialisation. The AppleSoft ROM at `$F123` has `$58` = 88, matching the initialisation copy. Steil independently reports the 89→88 change between versions 1.0 and 1.1. [S7] Because of the copy bug in §5.6, the fifth byte never reaches page zero anyway.)

**2. The routine matches instruction for instruction.** (a)

| Microsoft source [S5] | AppleSoft ROM [S4] |
|---|---|
| `RND: JSR SIGN` / `TAX` / `BMI RND1` | `EFAE: JSR SIGN` / `TAX` / `BMI LEFCC` |
| `LDWDI RNDX` / `JSR MOVFM` | `LDA #RNDSEED`… / `JSR LOAD_FAC_FROM_YA` |
| `TXA` / `BEQ RANDRT` | `TXA` / `BEQ RTS_19` |
| `LDWDI RMULZC` / `JSR FMULT` | `LDA #<CON_RND_1`… / `JSR FMULT` |
| `LDWDI RADDZC` / `JSR FADD` | `LDA #<CON_RND_2`… / `JSR FADD` |
| `RND1: LDX FACLO / LDA FACHO / STA FACLO / STX FACHO` | `LDX FAC+4 / LDA FAC+1 / STA FAC+4 / STX FAC+1` |
| `CLR FACSGN / LDA FACEXP / STA FACOV / LDAI 200 / STA FACEXP / JSR NORMAL` | `LDA #$00 / STA FAC_SIGN / LDA FAC / STA FAC_EXTENSION / LDA #$80 / STA FAC / JSR NORMALIZE_FAC_2` |
| `LDXYI RNDX / JMP MOVMF` | `LDX #RNDSEED… / JMP STORE_FAC_AT_YX_ROUNDED` |

Even the shared `RTS` matches: `RANDRT` is the last line of Microsoft's polynomial evaluator, directly above `RND`. In the ROM that same `RTS` is `RTS_19` at `$EFA5`, directly above `$EFA6`.

**3. Microsoft's own comment describes the algorithm.** (a) [S5]

```
;PSUEDO-RANDOM NUMBER GENERATOR.
;IF ARG=0, THE LAST RANDOM NUMBER GENERATED IS RETURNED.
;IF ARG .LT. 0, A NEW SEQUENCE OF RANDOM NUMBERS IS
;STARTED USING THE ARGUMENT.
;   TO FORM THE NEXT RANDOM NUMBER IN THE SEQUENCE,
;MULTIPLY THE PREVIOUS RANDOM NUMBER BY A RANDOM CONSTANT
;AND ADD IN ANOTHER RANDOM CONSTANT. THE THEN HO
;AND LO BYTES ARE SWITCHED, ...
```

**4. The source has an Apple build target.** (a)

`REALIO=4 ;4=APPLE.`, and the banner `IFE REALIO-4,<DT"APPLE BASIC V1.1">` followed by `"COPYRIGHT 1978 MICROSOFT"`. [S5]

(b) Steil reports that AppleSoft I printed "APPLE BASIC V1.1 / COPYRIGHT 1977 BY MICROSOFT CO." [S7]

**5. Apple's own manual says so.** (a)

The *Applesoft Reference Manual*, August 1978, carries both notices: "Copyright 1978 Apple Computer Inc." and "Copyright 1977 Microsoft Inc." [S16]

**6. Apple did not wire the keyboard counter into AppleSoft.** (a)

No instruction in the AppleSoft II ROM uses `$4E` or `$4F` as a zero-page operand. The only hits for those byte values are in keyword-name strings and in the seed constant `$F123`. Checked by scanning every code line of [S4].

**7. Woz's own account of the handoff.** (a)

> "They walked in the door, they had a BASIC for the 6502 microprocessor, and I was working on a floating point BASIC at the time, and I thought 'Oh my gosh, that'll free me up to work on other things.' So I was happy to go along with licensing it."
> — Wozniak [S12]

(b) Apple reportedly paid a flat US$31,000 for an eight-year licence. [S18] (a) Microsoft states Commodore paid US$25,000. [S6]

### 3.3 Who at Microsoft? (contested; say so on the slide)

The individual authors credited for Microsoft's 6502 BASIC vary by source:

| Claim | Source | Label |
|---|---|---|
| "The 6502 port was completed in 1976 by Bill Gates and Ric Weiland." | Microsoft, 2025 [S6] | (a), Microsoft's own statement |
| Easter-egg text in the source: `"WRITTEN BY WEILAND & GATES"` | m6502.asm [S5] | (a) |
| "Ric Weiland, Bill Gates and Monte Davidoff … wrote MOS 6502 BASIC in the summer of 1976 by converting the Intel 8080 version." | Steil [S7] | (b) |
| AppleSoft "developed by Marc McDonald and Ric Weiland" | Wikipedia [S18] | (b), weakest; no primary cited |
| 8080 source: "MONTE DAVIDOFF WROTE THE MATH PACKAGE." | quoted by Steil [S8] | (b): primary 8080 listing not inspected directly; quote widely reproduced |
| `RND` lives in the 6502 math package (octal region, `SUBTTL POLYNOMIAL EVALUATOR AND THE RANDOM NUMBER GENERATOR.`) | [S5] | (a) |
| The 6502 `RND` algorithm was written by Davidoff | — | **(c) inference only.** The 6502 file does not name RND's author, and I have not compared it with the 8080 math package. |

**Recommended slide wording:** "AppleSoft `RND` is Microsoft's 6502 BASIC generator (port credited to Weiland & Gates, derived from the Gates/Allen/Davidoff 8080 BASIC), shipped unmodified by Apple." Do not name a single individual as the LCG's author.

### 3.4 An instructive detail: Microsoft had a hardware-seeded `RND(0)` for Commodore

(a) The same Microsoft source compiles a different `RND` for `REALIO=3` (Commodore PET). There, `RND(0)` does not replay the last value; it loads the free-running VIA timers into the floating-point accumulator [S5]:

```
IFE REALIO-3,<
        BNE QSETNR
                ;TIMERS ARE AT 9044(L0),45(HI),48(LO),49(HI) HEX.
                ;FIRST TWO ARE ALWAYS FREE RUNNING.
        LDA CQHTIM
        STA FACHO ...
```

- (c) Microsoft seeded from hardware when the target had cheap free-running timers. The Apple II had no timer chip (§1.4), so the Apple build fell back to the generic fixed-seed LCG.
- (c) The Apple II **did** have a free entropy register at `$4E/$4F`. Neither Microsoft's Apple target nor Apple's AppleSoft adaptation used it. That was a missed integration opportunity. The record does not show whose decision it was.
- (c) Same keyword, opposite meaning. `RND(0)` meant "replay the last number" on the Apple and "read hardware timers" on the PET. That is a real trap when porting programs.

### 3.5 Phrasing guardrails for the deck

| Do not say | Say instead |
|---|---|
| "Woz's LCG" | "Microsoft's LCG in AppleSoft" |
| "Woz's RND(0) bug" | "Microsoft's RND(0) semantics, documented by Apple" |
| "the Apple II ROM's LCG" | "AppleSoft II ROM (II Plus onward) contains Microsoft's LCG" |
| "Woz used a keyboard counter as a seed for RND" (as a criticism of AppleSoft) | "Woz's Integer BASIC used the counter directly. AppleSoft never touched it; the `RND(-PEEK(78)-256*PEEK(79))` idiom was the programmer's job." |

Allowed: "Woz/Baum's monitor counter is the only entropy the machine had, and it is only as good as human keypress timing." (a)+(c)

---

## 4. The charitable reading

**Fit for purpose.**

- (a) Woz designed "GAME BASIC", "intended primarily for games and educational uses". [S10][S11]
- (c) For Breakout, Lemonade Stand or dice, the requirement is "the player can't predict it", not "an adversary can't predict it". A counter sampled at ~68 kHz against human reaction-time jitter meets the first requirement easily.

**The cheapest possible real entropy.**

- (c) Adding a noise source meant parts: a zener or transistor noise generator, a comparator, an addressable latch. That is board space and cost in a machine whose designer counted parts.
- (a)+(c) The keyboard counter cost six bytes and no parts, and used cycles the CPU was already wasting in a wait loop.

**Continuously reseeded, with a correct whitening step.**

- (a) Integer BASIC `RND` shares its state with the counter. [S1]
- (c) So every keyboard wait perturbs the stream, and there is no single power-on sequence that every Integer BASIC game replays.
- (c) The fixed-cold-start-seed failure mode belongs to AppleSoft, not to Integer BASIC programs that take any keyboard input before calling `RND`.
- (a) The 17-step LFSR has the zero-lock guard a maximal LFSR needs. (c, verified) It is maximal, with period 32,767.

**The alternatives were worse, or didn't exist yet.** (Addresses from [S2] unless noted.)

| Candidate source | Address | Chips needed | Cycle cost | Why not chosen (c unless marked) |
|---|---|---|---|---|
| Keyboard wait timing | `$C000` polled in `KEYIN` | 0 | 0 extra (idle loop) | **Chosen.** Human-driven, always available. |
| Cassette input | `TAPEIN $C060`, bit 7 (a) | 0 (input already on board, (a) [S10]) | Must sample repeatedly | Needs a signal or noise on the jack. With nothing plugged in the input is static. |
| Paddle timer | `PTRIG $C070` / `PADDL0 $C064`, `PREAD $FB1E` (a) | 0 (558 already on board) | Up to ~2.8 ms per read (c) | Returns the pot position, a user-controlled and steady value, not noise. Jitter in the count is small and unquantified here. |
| Floating bus (video "vapor") | Unused soft-switch reads, e.g. `$C050–$C057` (b) [S23] | 0 | Cheap | A function of screen contents and beam position, so deterministic. The technique was popularised later (Bob Bishop, *Softalk* 1982; Don Lancaster) (b) [S23]. |
| Vertical blank flag | none on Apple II / II Plus (b) [S23] | would need added logic | — | Did not exist; a VBL soft switch came with later models. |
| Real-time clock | none (a) [S10] | a clock chip plus a card | — | Not part of the design. |
| Interrupt-driven timer tick | IRQ vector `$3FE` exists, unused by ROM (a) | a timer source | ISR overhead | Would need hardware and would slow a 1 MHz machine for a feature games didn't need. |

**1977 practice agreed with this.**

- (a) Microsoft's own portable BASIC used a fixed-seed LCG on every non-Commodore target. [S5]
- (a) Apple's AppleSoft II manual presents repeatability as a feature: negative arguments "initialize (or 'seed') a repeatable sequence of random numbers. This is particularly helpful in debugging programs that use RND." [S17]
- (c) No 1977 Apple II document I found treats `RND` as a security primitive. Cryptographic unpredictability was not a design requirement.

**Hand-assembly locked the design in.**

- (a) Woz could not cheaply revise a hand-assembled ROM. [S11][S12]
- (a) Once Apple licensed Microsoft's floating-point BASIC, it was no longer Woz's code to fix. [S12]

---

## 5. Where the defense runs out

Even granting every constraint above, these are genuine failures. Where it matters, each is attributed to the party responsible.

**1. Integer BASIC never told users where the randomness came from.** Apple documentation; Woz's design.

- (a) The Red Book and Raskin's manual describe the range of `RND`. (c, absence claim from a full-text search of the archive.org OCR) Neither explains where its unpredictability comes from. [S14][S15]
- (a) The "incr rnd number" comment exists only in the ROM *source listing*. [S2][S14]
- (c) A programmer had no way to learn that randomness depended on keyboard waits, or that a game loop polling `PEEK(-16384)` never stirs the pool.
- (a) Negative arguments are documented only in a single Red Book line; the tutorial tells users to "find out … with just a few experiments". [S14][S15]

**2. Integer BASIC's generator is cheap in ways the whitening doesn't hide.** Woz; cost-driven.

- (c, verified) The whole state is 15 bits. Every program's `RND` stream is a window onto the same 32,767-step cycle, and the keyboard only chooses the starting point.
- (c) The output is `state MOD X`, which has modulo bias whenever X is not a power of two, and successive outputs are 17-step decimations of one LFSR.
- **Handoff to the research agent:** the statistical consequences (low-bit structure, serial correlation of decimated LFSR outputs) are not analysed here and need proper treatment.

**3. AppleSoft abandoned the one entropy source the machine had.** Microsoft's code; Apple's integration.

- (a) AppleSoft `RND` never reads `$4E/$4F` (§3.2 point 6), and the cold-start seed is a constant. [S4]
- (c) So every AppleSoft program that calls `RND` with a positive argument before any explicit reseed gets the same sequence on every cold start.
- (c) Apple put AppleSoft into the II Plus ROM alongside a monitor that still maintained the counter, and did not connect them. That step was Apple's to take.
- (c) The fix idiom, `X = RND(-(PEEK(78)+256*PEEK(79)))`, lived in folklore. It does not appear in the four 1978 Apple manuals searched. The search was of OCR text, so this is an absence claim, not proof. [S14–S17]

**4. Apple's documentation of AppleSoft `RND` was inconsistent and incomplete.** Apple.

- (a) The August 1978 *Applesoft Reference Manual* says: "X<=0 starts a new sequence of random numbers using X. Calling RND with the same X starts the same random number sequence." [S16] (OCR text; the `<=` should be checked against the scan.)
- (a) That contradicts the code and Microsoft's own comment, under which `RND(0)` returns the last value. [S4][S5]
- (a) The *Applesoft II BASIC Programming Reference Manual* (©1978; its order relative to the blue book is not established here) gives the correct `RND(0)` semantics. It says positive arguments generate "a new random number each time it is used". (c, absence claim from an OCR full-text search) It never says the sequence restarts identically at power-on. [S17]
- (b) In 1987 J. W. Aldridge published *Behavior Research Methods* 19(4):397–399, which the publisher summary describes as covering "undocumented characteristics of the pseudorandom number generators in Applesoft BASIC and Apple Pascal … that cause identical sequences". Wikipedia summarises the paper as saying this behaviour is "contrary to how Apple's documentation describes the function". [S20][S18]
  - **Caveat:** I could not retrieve the paper's full text (publisher bot-block). The research or review agent should read it before it is quoted on a slide.

**5. `RND(0)` and negative-argument semantics were opaque.** Microsoft's design; Apple's documentation.

- (a) "Negative starts a sequence, zero replays, positive advances" is Microsoft's convention. [S5]
- (a) Integer BASIC used negative arguments to mean a negative range instead. [S14]
- (a) On Commodore machines the same Microsoft keyword read hardware timers. [S5]
- (c) Three meanings for one function across one company's code and one competitor's port is a usability failure, whatever the ROM budget.

**6. A shipped initialisation bug nobody noticed.** Microsoft.

- (a) Only four of the five seed bytes are copied to `$C9–$CD` at cold start. The disassembler flags "the last byte of the random seed is not copied into page zero". [S4] The loop bound in Microsoft's source is `LDXI RNDX+4-CHRGET`. [S5]
- (b) Steil: "This bug exists in every known version of Microsoft BASIC." [S7]
- (b) Sander-Cederlof's annotations also call the addend "truncated" and say it "does nothing, due to small exponent". [S4] The research agent should verify this numerically before it is stated as fact.
- (c) Low practical impact, but it shows nobody examined the generator after it was written.

**7. The flaw is mostly in later uses and unexamined assumptions.** Shared.

- (c) The design failures above are real but modest for 1977 games.
- (c) The serious failures came when the same `RND` was used for simulations, education and research. Aldridge's venue, a behavioural-research methods journal, shows these uses were happening by 1987. Nobody revisited assumptions made for Breakout.
- (c) That is the thesis the deck should land: **the Apple II had no entropy source, only the appearance of one**. The appearance was good enough for its designer's purpose and was then trusted far beyond it.

---

## 6. Open items for other agents

1. **Research agent.** Statistical analysis of:
   - the 17-step decimated 15-bit LFSR combined with `MOD X` (Integer BASIC);
   - the Microsoft LCG, including verification of Sander-Cederlof's "addend does nothing" note.
2. **Review agent.**
   - Retrieve full-text Aldridge (1987) before it is quoted. A 3-page scan is at https://www.apple.asimov.net/documentation/programming/misc/random%20number%20generation%20note.pdf. It is image-only with no text layer, so it needs OCR or a human read.
   - Check the scan of the Aug 1978 blue-book manual for the exact `X<=0` / `X<0` wording.
   - Verify whether DOS 3.3's keyboard hook still reaches `KEYIN $FD1B`, which decides whether the counter advances under DOS.
3. **Source agent.** The listings in §2.1, §2.3 and §3.2 are taken from [S1][S2][S4][S5] and can be dropped straight into `source/`. Addresses and labels match those disassemblies.

---

## 7. Attribution audit of the existing deck, "Applesoft's Loaded Dice"

- **Audited artifact:** `deck/Applesoft_Loaded_Dice_Deck_1.pptx`.
  - The title slide names **Jeff Robison, VCF Midwest 21, 2026** as presenter; the file metadata shows `lastModifiedBy` Jeff Robison. The recommendations below are written for the presenter.
- **What was read:**
  - Every slide's text (`ppt/slides/slideN.xml`) and speaker notes (`ppt/notesSlides/notesSlideN.xml`).
  - All 11 embedded images. Slide 5 has five disassembly screenshots. Slide 6 has the AppleSoft RND disassembly. Slide 7 has four manual excerpts plus the `.973136996` screen capture.
- **Numbering:** slide numbers here follow **file order (1–10)**. The page labels printed on the slides disagree with file order: file slides 3–9 are labelled 2, 3, 4, 5, **5**, 7, 9.

### 7.1 Headline finding

**The deck's attribution is sound.** Slide 4 credits Woz with the Integer BASIC generator at `$EF4E`, and slides 6–7 treat Applesoft separately, with its own seed at `$C9`. Nothing in the deck blames Woz for Microsoft's LCG.

Only three pieces of residual ambiguity remain; each is optional polish, not an error:

1. **No slide names Microsoft.** "Microsoft" appears once, in slide 10's speaker notes. One clause on slide 6 would pre-empt anyone in the room who assumes Applesoft was written in-house. Evidence is in §3.2.
2. **The slide 6 screenshot comments are not the ROM's own.** "very poor RND algorithm" and "to supposedly make it more random" are Bob Sander-Cederlof's annotations, reproduced by McFadden. A one-line caption fixes it.
3. **Slide 10's notes credit Commodore for timer seeding that Microsoft wrote for Commodore.** It was already in the first PET ROM in 1977. See §9.2.

(The per-slide table below was written before the brief was corrected. Where it is stricter than this summary, this summary governs.)

### 7.2 Slide-by-slide audit

| Slide | What it says (verbatim) | Attribution verdict | Recommended exact wording |
|---|---|---|---|
| **1** | "Applesoft's Loaded Dice / The Truth About Randomness on the Apple II, Then and Now" | **Correct.** "Applesoft" is the product name; the title names no author. Mildly ambiguous for anyone who doesn't know Applesoft is Microsoft BASIC. | Keep the title. Add to the speaker notes: *"Applesoft is Microsoft's 6502 BASIC, licensed by Apple. Keep that in mind; it matters on slide 6."* |
| **2** | "The Problem / PRINT RND(1) / .973136996" | **Neutral**, no author implied. | No attribution change. Technical caution in §8, slide 2. Notes 2 duplicate notes 3 ("The amber box … Slide 4 depends on it"), which doesn't fit a slide with no amber box; replace. |
| **3** | "Truly random … Pseudo-random … Entropy is the key to sufficient randomness and unpatterned results." | **Neutral.** | Optional accuracy tweak that supports the seed-regression thesis: *"Entropy decides where the sequence starts. The formula decides what the sequence looks like."* (c) Entropy does not make a formula's output "unpatterned"; it makes the starting point unpredictable. |
| **4** | "Integer BASIC, 1977 / Woz wrote a generator at $EF4E / Known period with limited range / No Floating point / Sufficiently random / Built-in Seed / There's a counter at $4E and $4F that goes up while the monitor sits waiting for a keypress. Integer BASIC reads it. / Sander-Cederlof, Apple Assembly Line, August 1981." | **Correct.** Woz wrote Integer BASIC `RND` at `$EF4E` (a) [S1]. The citation checks out: AAL Aug 1981, "Random Number Generator from Integer BASIC", which labels the code "WOZNIAK'S ALGORITHM" and uses `MON.RNDL .EQ $4E` [S25]. The slide does not say who wrote the counter, which is right: the monitor is credited "S. Wozniak, A. Baum" [S2]. | Sharpen: *"Woz wrote a generator at $EF4E: a 15-bit shift register, period 32,767"* and *"The monitor's keyboard-wait counter at $4E/$4F **is** its state. RND reads it, scrambles it, and writes it back."* (c, verified by E1) Change "Sufficiently random" to *"Sufficiently random for games"*, which is Woz's stated purpose [S10]. |
| **5** | "Built-in Entropy Source / $4E/$4F / Integer BASIC, at $EF4E / Present in some form in all Apple II ROMs" plus links; images of `KEYIN $FD1B` (II), `$EF4E` RND, `$FD1B` (II Plus), IIc `$CC71`, IIe `GETKEY $CB15`. Notes: "Woz wrote Integer BASIC with no assembler…" | **Correct.** The notes' hand-assembly claim is documented (a) [S1][S10][S13]. "All Apple II ROMs": verified for the original II, II Plus, unenhanced IIe (80-column firmware `GETKEY $CB15`, `IK2A $C2D5`) and the 16K IIc (`$CC71` "update seed") [S2][S3][S26][S27]. The enhanced IIe, later IIc ROMs and IIgs were **not checked**. | Change to *"Present in every Apple II ROM from the II through the IIc"*, or verify the rest before keeping "all". Add to notes: *"The monitor listing credits S. Wozniak and A. Baum."* Replace "Sit there two seconds and it's gone round tens of thousands of times" with *"The loop is 15 CPU cycles, so about 68,000 counts a second. The 16-bit counter wraps roughly once a second."* (c, computed) |
| **6** | "Applesoft, 1978 / Applesoft relies on different seed / However, the seed for Integer BASIC remains. / What it does: Takes the seed at $C9, multiplies, adds, swaps two bytes around, forces the result under 1, writes it back to $C9." Image: AppleSoft `$EFAE–$EFE7` with comments "very poor RND algorithm", "to supposedly make it more random". Notes: "Twenty-six instructions." | **Sound.** The code is described accurately. Residual (optional): the author is not named on the slide. The comments in the screenshot are **Bob Sander-Cederlof's annotations**, not Microsoft's or Apple's original comments [S4]. Unlabelled, they read as the ROM's own confession. The notes' count is wrong: `$EFAE–$EFE7` is **28** instructions. | Title: ***"Applesoft II, 1978: Microsoft's RND"***. First line: ***"Microsoft wrote this generator. Apple licensed it and shipped it unchanged."*** Second line: ***"The monitor still bumps $4E/$4F. Applesoft never reads it."*** Caption under image: ***"Code: Microsoft BASIC M6502 v1.1 (open-sourced 2025). Disassembly and comments: Bob Sander-Cederlof, S-C DocuMentor, via Andy McFadden."*** Notes: *"Twenty-eight instructions"*, and *"four of $C9's five bytes get a fixed value from ROM at boot"*. |
| **7** | "Applesoft Manual, 1978 / RND(n) / RND(-n) / RND(0)" with excerpts from the *Applesoft II BASIC Programming Reference Manual* | **Correct.** The manual is Apple's documentation, and it documents Microsoft's semantics accurately [S5][S17]. | Caption: *"Applesoft II BASIC Programming Reference Manual, Apple Computer, ©1978 (030-0013-03)."* Strongly recommended, and the cheapest attribution proof in the deck: add *"Apple's own Aug 1978 Applesoft manual: 'Copyright 1978 Apple Computer Inc. / Copyright 1977 Microsoft Inc.'"* [S16]. Notes 7 duplicate notes 6 ("This is the whole thing. Twenty-six instructions…"); replace. |
| **8** | "Sources / Kaner & Vokey, 1982 … / Call A.P.P.L.E., Jan 1983 'RND is Fatally Flawed.' / Sander-Cederlof, AAL May 1984: Found the startup bug. The seed copy is off by one. / Aldridge 1987, Gleason 1988 … / Empson, GS WorldView 1999 …" | **Sound; optional precision on the bug's owner.** AAL May 1984 does describe the bug: loop at `$F150`, fix `$F151` from `$1C` to `$1D` [S28]. But the off-by-one is **in Microsoft's source** (`LDXI RNDX+4-CHRGET`) [S5], and Steil reports it in every Microsoft 6502 BASIC [S7]. "Found" also overclaims: AAL May 1984 itself cites Call-A.P.P.L.E. Jan 1983, pp. 29–34, as earlier, and I have not established who reported the seed bug first. | ***"Sander-Cederlof, AAL May 1984: documented the startup bug at $F150. Microsoft's seed copy is off by one, in every Microsoft 6502 BASIC."*** Add two attribution sources: ***"Microsoft, BASIC-M6502 source (github.com/microsoft/BASIC-M6502, 2025)"*** and ***"Steil, pagetable.com, 'Create your own Version of Microsoft BASIC for 6502'."*** Notes 8 cite "the 202 figure", which appears on no slide; add it or cut it. Kaner & Vokey, Aldridge, Gleason and Empson are **not verified by me**. |
| **9** | "Two Part Solution … Writes the patch code into the LC at $F5CB. (may impact HFIND, supposedly unused by AppleSoft.) Writes JMP $F5CB at $EFAE in the LC copy … Preserves negative and zero RND() functionality while relying on the KEYIN counter present in the ROM." | **Correct** (no author implied). The HFIND claim holds up: Sander-Cederlof annotates `HFIND` "(not called by any Applesoft routine)" [S4]. | Replace the hedge with checked facts: ***"Patch lives in the LC copy at $F5CB, over HFIND ($F5CB–$F600, 54 bytes), which no Applesoft routine calls."*** The patch must be **≤ 54 bytes** or it overruns into `DRAW0` at `$F601`. (c) User programs that `CALL` HFIND directly would break; say so if asked. |
| **10** | "Try it yourself". Notes: "does the C64 have this too (yes, same Microsoft code, but Commodore wired RND(0) to hardware timers and gave people TI)" | **Partly correct; one correction (full evidence in §9.2).** Verified correct:
- The C64 runs the same Microsoft generator, with the same constants.
- The C64's `RND(0)` reads hardware (CIA1 timer A and the TOD clock).
- `TI` exists.

Needs correcting: the timer-seeded `RND(0)` and `TI` are in **Microsoft's own source** for the Commodore target (`IFE REALIO-3`, `TIME==1`) [S5], and in the first PET ROM, Commodore BASIC 1 (1977) [S31]. Commodore later re-targeted it to the C64. | ***"Yes, same Microsoft generator, same constants. But Commodore's machines got the platform integration. Microsoft's own Commodore build made RND(0) read the PET's timers and added TI, back in the first PET ROM in 1977, and Commodore carried it forward to the C64. The Apple build got the plain version, and Apple never connected the counter its own monitor was already running. On a Commodore the idiom is RND(-TI); on the Apple it's RND(-PEEK(78)-256*PEEK(79))."*** |

### 7.3 One-sentence framing the deck can adopt

(a)+(c) ***"In 1978 Apple swapped Woz's BASIC for Microsoft's, and Microsoft's RND ignores the keyboard counter that Woz's monitor still maintains."***

This keeps the regression thesis intact, puts each piece of code under the right name, and matches Woz's own account of why Apple licensed Microsoft BASIC: "that'll free me up to work on other things" [S12].

---

## 8. Support for the existing deck

Where the deck would benefit from 1977-constraints context (§1) or the charitable reading (§4). Keyed to file-order slide numbers.

- **Slide 2 (cold-boot value).** Technical caution for the review agent. Only four of the five seed bytes are copied at cold start; `$CD` keeps whatever was in RAM [S4][S5].
  - Sander-Cederlof speculated in 1984 that this "could make the numbers generated a little more random from one run to the next" [S28] (b).
  - (c) `.973136996` may be reproducible only when `$CD` powers up the same way, as in an emulator or on one machine's RAM pattern.
  - Before the live demo, verify on more than one real II Plus, or add "on this machine". Someone in this audience will try it on theirs.
- **Slide 4 (Integer BASIC).** Best place for the constraints:
  - (a) 8K of mask ROM that "sometimes isn't enough room to fit all the needed features"; hi-res didn't fit [S10].
  - (a) Hand-assembled with no source file [S1][S13].
  - (a) "intended primarily for games and educational uses" [S10].
  - (c) The whole Integer BASIC RNG is 56 bytes: 6 in `KEYIN`, 50 in `RND`.
  - Suggested speaker line: *"This isn't a toy generator; it's a 15-bit maximal shift register with a zero-lock guard, in 50 hand-assembled bytes."* (a)+(c, verified E1)
- **Slide 5 (entropy source).** Supports the existing "not a jiffy clock" note:
  - (a) No RTC, no timer chip, and the ROM uses no interrupts; the keyboard is polled [S2][S10]. So a keyboard-wait loop was the only free entropy on the board.
  - (c) The alternatives table in §4 (cassette `$C060`, paddles `$C064`, floating bus, no VBL) answers "why didn't he use X?" if asked.
- **Slide 6 (AppleSoft).** Charitable context for *Microsoft*, so the room doesn't swing to the opposite strawman:
  - (a) A fixed-seed LCG was Microsoft's generic, hardware-agnostic default on every non-Commodore target [S5].
  - (c) The Apple II had no timer for Microsoft to read.
  - (a) Apple's manual sells repeatability as a debugging feature [S17].
  - (b) Woz was busy with the Disk II, which is why Apple licensed rather than extended Integer BASIC [S18][S19]; Woz's own words are in [S12].
  - The failure is integration: nobody connected the counter that was already there. §5.3.
- **Slide 7 (manual).** Where the defense runs out:
  - (c, from an OCR search) The manual never says the sequence restarts identically at power-on.
  - (a) The Aug 1978 blue-book manual describes `RND(0)` differently from the code [S16]; check the scan before quoting it.
  - This is Apple's documentation failure and belongs on this slide.
- **Slide 8 (sources).** Add Microsoft's source release and Steil for attribution. If the review agent confirms Aldridge (1987), it shows the generator trusted in research settings far beyond its design brief (§5.7).
- **Slide 9 (patch).** Caveat for "this machine used to do it automatically":
  - (a) The counter advances only while input waits in `KEYIN` [S2]. Programs that poll `$C000` with `PEEK(-16384)` or `WAIT 49152,128` never advance it [S21].
  - (c) The patch inherits that limit: a program that seeds before any `KEYIN` wait gets whatever `$4E/$4F` held.
  - (c) Whether DOS 3.3's input hook still passes through `$FD1B` is unverified (§6).
- **Slide 10 (Q&A).** Likely question: "So was Woz's version actually good?" Answer:
  - (c, verified E1) "For games, yes: 15-bit state, 32,767 period, stirred by every keyboard wait."
  - (c) "Not for anything statistical: `MOD X` bias, and one short cycle every program shares."

### Additional sources for §7–8

- **[S25]** B. Sander-Cederlof, "Random Number Generator from Integer BASIC", *Apple Assembly Line*, Aug 1981. http://www.txbobsc.com/aal/1981/aal8108.html
- **[S26]** Apple //e (unenhanced) 80-column firmware disassembly (`GETKEY $CB15`, `IK2A $C2D5` increment `$4E/$4F`). https://6502disassembly.com/a2-rom/Unenh_IIe_80col.html
- **[S27]** Apple //c 16K firmware disassembly (`$CC71 inc RNDL ;update seed`). https://6502disassembly.com/a2-rom/IIc_16kb.html
- **[S28]** B. Sander-Cederlof, "Random Numbers for Applesoft", *Apple Assembly Line*, May 1984 (seed-copy bug at `$F150`/`$F151`; cites Call-A.P.P.L.E. Jan 1983 pp. 29–34). http://www.txbobsc.com/aal/1984/aal8405.html

---

## 9. The regression: why Applesoft never read `$4E/$4F`, how Commodore differed, and what Apple could have changed

This section answers the three questions the talk's regression thesis raises:

1. why Applesoft didn't use the counter;
2. whether Commodore did the integration Apple didn't;
3. whether Apple could have fixed it.

Written for Jeff Robison's VCF Midwest 21 audience, which will check addresses live.

### 9.0 Bottom line

- **No primary record explains the seed decision.** I looked in:
  - Microsoft's source comments and its 2025 release post;
  - Steil's pagetable.com analyses;
  - *Apple II History* chapters 3 and 16, including the Huston brothers' 2010 interview as summarised there;
  - Sander-Cederlof's *Apple Assembly Line* articles of 1981 and 1984;
  - the four 1978 Apple manuals.

  Every statement about motive below is inference and is labelled that way.
- **Best-supported reading.** (c, built on (a) evidence)
  - Microsoft's portable BASIC had two `RND`s: a hardware-seeded one for Commodore, and a fixed-seed one for every other target. Apple got the second.
  - Machine-specific integration on the Apple II was Apple's own job. Apple demonstrably rewrote the code *around* the seed and never connected it.
  - "Portability" does not hold up as a technical reason.
- **The Commodore contrast is real, but the credit goes to a different party.** The hardware-seeded `RND(0)` was written into Microsoft's source for Commodore and shipped in the first PET ROM in 1977; Commodore carried it forward to the C64.
  - Fairest one-liner: **"Commodore bought platform integration from Microsoft. Apple did its own, and skipped RND."**

### 9.1 Why didn't Applesoft read `$4E/$4F`?

| Hypothesis | Evidence | Verdict |
|---|---|---|
| **Portability.** 6502 BASIC couldn't assume Apple's monitor. | **Against, all (a) [S5]:** Microsoft's source already had Apple-only code. `IFE REALIO-4,<ORG 80> ;ROOM FOR APPLE PAGE 0 STUFF.` (line ~790). `INCHR: JSR CQINCH ;FD0C FOR APPLE COMPUTER.` (~1756). An Apple-specific `ISCNTC` reading `^O140000` = `$C000` (~2221). Bit-7 handling for Apple output (~2838). Commodore got a machine-specific `RND` in the same file. **The counter even runs under Applesoft:** the ROM calls `MON_GETLN $FD6A` at `$D530` and `MON_RDKEY $FD0C` at `$D553`, and `RDKEY` jumps through `KSW` to `KEYIN` [S2][S4] (a). | **Refuted** as a technical constraint. (c) The counter ticked through every Applesoft keyboard wait and was never read. |
| **Ignorance of the counter.** | (a) `ORG 80` = `$50`: Microsoft reserved `$00–$4F` for Apple, and `$4E/$4F` are its last two bytes. (c) That shows awareness of the *region*, not of the counter's purpose. (a) The counter is documented as `RNDL`/`RNDH`, "incr rnd number", in the Jan 1978 Red Book listing [S2][S14]. (b) Microsoft delivered v1.1 to Apple in late 1977 [S32]. Whether Microsoft ever saw the monitor listing is not recorded. (b) Apple's own staff, led by Wigginton, did the Apple-specific integration [S32]; the ROM was Apple's own. | **Plausible for Microsoft, unprovable.** Not credible for Apple. |
| **Schedule.** | (b) Huston called the delivered source "a mess" that needed considerable bug fixing. Applesoft I was cross-assembled over a 110-baud link to Call Computer. A tape failure there in Dec 1977 destroyed months of work, and Applesoft I shipped on cassette in Jan 1978 [S32]. (a) But `RND`, the seed and the init loop are byte-identical in the II Plus, IIe **and enhanced IIe** Applesoft ROMs [S33]. | **Explains 1977; does not explain the later ROM revisions.** (c) |
| **Deliberate tradeoff.** | (a) The documented contract is that a negative argument starts a *repeatable* sequence (Microsoft's source comment [S5]). Apple's manual sells that repeatability as "particularly helpful in debugging" [S17]. (c) Mixing the live counter into every `RND(1)` would break that contract. **A one-time seed would not:** `RND(-n)` still reseeds deterministically. That is what the deck's slide 9 patch shows. (c) The natural moment is at `RUN` or the first `RND` after keyboard input, not at cold start: at autostart boot no key has been pressed, so `$4E/$4F` holds leftovers. | **A real constraint on *how* to fix it. Not a reason to leave it unfixed.** |
| **Microsoft's generic default.** | (a) In the v1.1 source `RND` comes in exactly two variants: Commodore (`IFE REALIO-3`, hardware timers) and everyone else (KIM, OSI, Apple, STM, PDP-10 simulator; fixed-seed LCG) [S5]. (b) Steil: the Apple target "contains no customizations other than some changes around I/O handling" [S8]. (c) The Apple II has no timer chip, so there was no Apple analogue of the Commodore code to write. `$4E/$4F` is a *software* counter in Apple's monitor that runs only during keyboard waits, not something a port would find in a hardware spec. | **Best supported.** |

**Suggested slide or speaker line** (c, every clause backed by (a)): *"Microsoft's BASIC had two RNDs: one for Commodore that read hardware timers, and one for everyone else. Apple got the everyone-else version, and nobody at either company plugged in the counter the monitor was already running."* Say "nobody connected it", not "nobody knew".

### 9.2 Commodore: what slide 10's notes claim, verified

Claim (slide 10 notes): *"same Microsoft code, but Commodore wired RND(0) to hardware timers and gave people TI."*

| Part of the claim | Status | Evidence |
|---|---|---|
| Same Microsoft code on the C64 | **Confirmed** | (a) C64 BASIC V2 `RND` at `$E097`; constants at `$E08D` `98 35 44 7A 00` (11879546) and `$E092` `68 28 B1 46 00` (3.927677739E-8), the same values as Applesoft `$EFA6`/`$EFAA` [S29]. **Research-agent note:** the C64 stores each constant as 5 bytes with a trailing `$00`. Applesoft, PET BASIC 1/2 and Microsoft's source store 4, so Applesoft's multiplier picks up `$68` from the next constant as its fifth byte. (a) bytes [S4][S29][S31]; (c) the numerical effect is unanalysed. |
| C64 `RND(0)` reads hardware | **Confirmed** | (a) `$E09E JSR $FFF3` (KERNAL IOBASE), then reads I/O offsets +4/+5 and +8/+9 into the FAC mantissa [S29]. (b) On the C64 that is CIA1 timer A and the TOD tenths/seconds registers. TOD is not started by default, so in practice about 16 bits vary [S30]. |
| "**Commodore** wired it" | **Correction needed** | (a) Microsoft's v1.1 source, `IFE REALIO-3`: `;TIMERS ARE AT 9044(L0),45(HI),48(LO),49(HI) HEX. ;FIRST TWO ARE ALWAYS FREE RUNNING.` with `CQHTIM=^O164104` = `$E844` [S5]. (a, via Steil's byte-exact reconstruction [S7][S31]) **Commodore BASIC 1**, the first PET ROM of 1977, builds this `RND(0)` under `CONFIG_CBM_ALL` with `ENTROPY = $9044`; **Commodore BASIC 2** uses `ENTROPY = $E844`. (c) The 1978 source's comment still names BASIC 1's `$9044` while its code uses BASIC 2's `$E844`, so the address change was made in Microsoft's own file. (b) Steil: "initially it was Microsoft adapting their source for the different computers … Features like file I/O and time support seem to have been specifically developed for Commodore" [S8]. (b) Jim Butterfield, via Steil: "Commodore paid Microsoft an additional fee to write a revision to the original BASIC" [S9]. (a, Microsoft's statement) The v1.1 garbage-collector fixes were "jointly implemented in 1978 by Commodore engineer John Feagans and Bill Gates" [S6]. (c, strong) The C64 version reaches the timer through the KERNAL's `$FFF3` rather than a fixed address, which is Commodore re-targeting the idea to later hardware. |
| "gave people TI" | **Confirmed, same nuance** | (a) Microsoft's source sets `TIME==1` for the Commodore target [S5]. (a) C64 `TI`/`TI$` read the KERNAL clock via `JSR $FFDE` (RDTIM) at `$AF84`, and the KERNAL IRQ advances it with `JSR $FFEA` (UDTIM) at `$EA31` [S29]. (c) The BASIC `TI` variable is Microsoft-for-Commodore code; the jiffy clock underneath is Commodore's KERNAL. |
| Don't oversell Commodore | caveat | (b) C64-Wiki documents `RND(0)` as poorly distributed; its typical idiom is `X = RND(-TI)` once, then `RND(1)` [S30]. The integration gave Commodore users a *seed source*, not a better generator. |

### 9.3 How much could Apple actually change? Evidence says: a lot, including the seed loop itself

**1. Apple had, edited and assembled the full source.** (b) [S32] [S7]

- Wigginton cross-assembled Applesoft at Call Computer, then on Cliff Huston's IMSAI.
- For Applesoft II (spring 1978), Apple "took this new Microsoft revision and made other changes": fixed known bugs, added the hi-res commands, and renamed the lo-res commands.
- Steil: Apple "licensed an improved and bugfixed version of BASIC, and merged their old changes into it."

**2. Apple modified Microsoft's generic code, not just the Apple extensions.**

- (b) Applesoft I replaced "OK" with "]" and "ERROR" with "ERR". Applesoft II dropped the MEMORY SIZE and TERMINAL WIDTH questions. [S7]
- (a) The ROM confirms it:
  - Microsoft's `INIT` prints "MEMORY SIZE" and reads a line of input (source ~6760–6775) [S5].
  - Applesoft's `COLD_START` instead probes RAM silently, complementing the first byte of each page from `$0800` and rounding down to a 4K multiple (`$F177–$F19D`) [S4].

**3. Apple edited the very loop that drops the seed's last byte.** (a)

Microsoft source, line ~6733 [S5]:

```
        LDXI    RNDX+4-CHRGET
MOVCHG: LDA     INITAT-1,X,
        STA     CHRGET-1,X,     ;MOVE TO RAM.
        DEX
        BNE     MOVCHG
```

Applesoft II ROM [S4]:

```
F150: A2 1C        LDX #$1C               ; same short count
F152: BD 0A F1     LDA GENERIC_CHRGET-1,X
F155: 95 B0        STA CHRGET-1,X
F157: 86 F1        STX SPEEDZ             ; inserted by Apple
F159: CA           DEX
F15A: D0 F6        BNE LF152
```

- (a) `SPEEDZ` (`$F1`) backs Apple's `SPEED=` command (`$F265–$F26A`). `SPEED`, `TRACE` and `LOCK` do not exist in Microsoft's v1.1 source; checked by text search [S4][S5].
- (a) The same routine also contains other Apple insertions:
  - `JSR NORMAL` at `$F13B`, Apple's text-mode command;
  - `STX TRCFLG` at `$F15C`, Apple's TRACE;
  - `STY LOCK` at `$F1AD`, Apple's auto-run flag.
- (c) Apple's engineers worked instruction by instruction inside this routine and kept `#$1C`.
- (a) The fix Sander-Cederlof published in 1984 is a single byte: `$F151` from `$1C` to `$1D` [S28].
- (c) Connecting the counter would take more than one byte, but the routine was plainly open to Apple.

**4. Apple revised the Applesoft ROM again and still left RND alone.** (a, computed from ROM images [S33])

- **Apple IIe:** Applesoft `$D000–$F7FF` differs from the II Plus in 1 byte (`$F7FF`).
- **Enhanced IIe:** differs in **179 bytes**, in ranges `$D56D–$DB27`, `$E006`, `$F3B7`, `$F3D3` and `$F775–$F7FF`.
- **In all three ROMs**, `RND` and its constants (`$EFA6–$EFE9`), the seed (`$F123`) and the init loop including `LDX #$1C` (`$F150`) are byte-identical.
- The IIc and IIgs ROMs were not checked.

**5. Licence.** (b)

- Flat fee, eight years [S18]. *Apple II History* says Apple paid "$10,500 … for the first half" in Aug 1977, citing Manes & Andrews, *Gates* (1993) [S32]. That implies $21,000, which **conflicts** with Wikipedia's $31,000; don't put a figure on a slide without resolving it.
- (c) Nothing suggests the licence stopped Apple modifying the code, and Apple's own changes show it didn't. "Contractually couldn't" is not a credible defence.

**6. Charitable counterweights to say out loud.** (c)

1. The regression is silent: you only see it by rebooting and comparing first values, which almost nobody did in 1978.
2. Apple's manual described deterministic seeding as a feature, so engineers reading their own documentation saw `RND` working as specified.
3. Changing `RND`'s output would have altered sequences existing programs might depend on. That argues only against mixing the counter into every call, not against a one-time seed.

**Suggested speaker line:** *"Apple wasn't locked out of this code. Apple's engineers edited the loop that loads the seed; they added an instruction for SPEED= right inside the loop that drops the seed's last byte. It shipped that way in the II Plus, the IIe, and the enhanced IIe."*

### 9.4 Optional slide: "Why 1978 got worse"

Fits between slides 7 and 8.

- **Microsoft's BASIC had two RNDs:** hardware-seeded for Commodore, fixed-seed for everyone else. (a) [S5][S31]
- **Apple got the fixed-seed build.** (a) [S4][S5]
- **The counter kept running under Applesoft's own keyboard input.** (a) [S2][S4]
- **Apple rewrote the code around the seed and left it**, in every Applesoft ROM checked through the enhanced IIe. (a) [S4][S33]

Speaker notes: the motive is not recorded. Say "nobody connected it", not "nobody knew" or "Microsoft was careless".

### Additional sources for §9

- **[S29]** M. Steil et al., C64 ROM disassembly (English), c64ref. https://github.com/mist64/c64ref (file `src/c64disasm/c64disasm_en.txt`; RND `$E097–$E0F8`, TI `$AF84`).
- **[S30]** C64-Wiki, "RND". https://www.c64-wiki.com/wiki/RND
- **[S31]** M. Steil, *msbasic*, byte-exact reconstruction of Microsoft 6502 BASIC variants: `rnd.s` (`CONFIG_CBM_ALL` branch), `defines_cbm1.s` (`ENTROPY = $9044`), `defines_cbm2.s` (`ENTROPY = $E844`). https://github.com/mist64/msbasic
- **[S32]** S. Weyhrich, *Apple II History*, ch. 16 "Languages" (Applesoft I/II development; Huston brothers interview, RetroMacCast #153, 2010; Manes & Andrews 1993). https://www.apple2history.org/history/ah16/
- **[S33]** ROM images `Apple2_Plus.rom`, `Apple2e.rom`, `Apple2e_Enhanced.rom` as distributed with AppleWin (https://github.com/AppleWin/AppleWin, `resource/`). Compared byte-wise over `$D000–$F7FF`; images not copied into the workspace. (Provenance: emulator distribution, not dumped by me.)

---

## Sources

- **[S1]** Integer BASIC ROM disassembly, Paul R. Santa-Maria; SourceGen port by Andy McFadden. Floating-point, mini-assembler and SWEET16 sections from the Red Book, by Sean Gugler. https://6502disassembly.com/a2-rom/IntegerBASIC.html
- **[S2]** Original Apple II monitor ROM ("S. Wozniak, A. Baum"), from the *Apple II Reference Manual* listing, p.155; SourceGen by McFadden. https://6502disassembly.com/a2-rom/OrigF8ROM.html
- **[S3]** Apple II Plus Autostart monitor ROM ("Steve Wozniak … Modified Nov 1978 By John A"). https://6502disassembly.com/a2-rom/AutoF8ROM.html
- **[S4]** Applesoft II disassembly, from Bob Sander-Cederlof's *S-C DocuMentor: Applesoft*; SourceGen by McFadden. https://6502disassembly.com/a2-rom/Applesoft.html
- **[S5]** Microsoft, *BASIC M6502 8K VER 1.1* source (`m6502.asm`), released Sept 2025. https://github.com/microsoft/BASIC-M6502. Line refs: `RADIX 8` at 4847; RND at ~6329–6397; seed at 978 and 6695; init loop at 6733; banners at 6915–6944.
- **[S6]** Microsoft Open Source Blog, "Bringing BASIC back: Microsoft's 6502 BASIC is now Open Source", 2025-09-03. https://opensource.microsoft.com/blog/2025/09/03/microsoft-open-source-historic-6502-basic/
- **[S7]** M. Steil, "Create your own Version of Microsoft BASIC for 6502", pagetable.com. https://www.pagetable.com/?p=46
- **[S8]** M. Steil, "Microsoft BASIC for 6502 Original Source Code [1978]", pagetable.com. https://www.pagetable.com/?p=774
- **[S9]** M. Steil, "Bill Gates' Personal Easter Eggs in 8 Bit BASIC", pagetable.com. https://www.pagetable.com/?p=43
- **[S10]** S. Wozniak, "System Description: The Apple-II", *BYTE* 2(5), May 1977. Reprint: https://www.informationweek.com/it-infrastructure/system-description-the-apple-ii-by-stephen-wozniak
- **[S11]** S. Wozniak, "How Steve Wozniak Wrote BASIC for the Original Apple From Scratch", Gizmodo, 2014-05-01. https://gizmodo.com/how-steve-wozniak-wrote-basic-for-the-original-apple-fr-1570573636
- **[S12]** J. Szczepaniak, "Steve Wozniak discusses early Apple years and BASIC" (interview), Game Developer, 2012. https://www.gamedeveloper.com/programming/steve-wozniak-discusses-early-apple-years-and-basic
- **[S13]** S. Weyhrich, *Apple II History*, ch. 3, quoting J. Connick, "…And Then There Was Apple", *Call-A.P.P.L.E.*, Oct 1986. https://www.apple2history.org/history/ah03/
- **[S14]** *Apple II Reference Manual* ("Red Book"), Apple, Jan 1978. https://archive.org/details/Apple_II_Reference_Manual_1978-01_Apple
- **[S15]** J. Raskin, *Apple II BASIC Programming Manual*, Apple, 1978. https://archive.org/details/Apple_II_Basic_Programming_Manual_1978_Apple
- **[S16]** *Applesoft Reference Manual* ("blue book"), Apple, Aug 1978 (©1978 Apple, ©1977 Microsoft). https://archive.org/details/Applesoft_Reference_Manual_1978-_bluebook
- **[S17]** *Applesoft II BASIC Programming Reference Manual*, Apple, ©1978 (030-0013-03). https://archive.org/details/applesoft-ii-ref
- **[S18]** Wikipedia, "Applesoft BASIC". Secondary: licence fee via Hertzfeld/folklore.org, Wigginton, Aldridge summary. https://en.wikipedia.org/wiki/Applesoft_BASIC
- **[S19]** Wikipedia, "Apple II (original)". Secondary: prices, 558 timer. https://en.wikipedia.org/wiki/Apple_II_(original)
- **[S20]** J. W. Aldridge, "Cautions regarding random number generation on the Apple II", *Behavior Research Methods, Instruments, & Computers* 19(4):397–399, 1987. doi:10.3758/BF03202585. **Abstract fragment only; full text not read.**
- **[S21]** Applefritter forum, "Random number generation on the Apple II with AppleSoft BASIC" (WAIT vs GET seeding observation). https://www.applefritter.com/content/random-number-generation-apple-ii-applesoft-basic
- **[S22]** A. McFadden, Apple II ROM disassembly index, "The Oft-Misunderstood WAIT" sidebar (average clock 1.0205 MHz). https://6502disassembly.com/a2-rom/
- **[S23]** Floating bus / vapor lock: http://www.deater.net/weave/vmwprod/megademo/vapor_lock.html; Applefritter, "'Vaporlock' technique from Don Lancaster's *Enhancing Your Apple II and IIe*", https://www.applefritter.com/content/vaporlock-technique-don-lancasters-enhancing-your-apple-ii-and-iie; comp.sys.apple2.programmer, "Vertical Blank on Apple ][+".
- **[S24]** R. Rankin & S. Wozniak, "Floating Point Routines for the 6502", *Dr. Dobb's Journal*, Aug 1976. https://www.applefritter.com/node/6876
- **[E1]** `woz/intbasic_rnd_emu.py`: exact emulation of `$EF4E–$EF72`. Checks the feedback identity for all 65,536 register values, the cycle length, and the `KEYIN` rate.
