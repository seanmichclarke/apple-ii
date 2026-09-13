# Integer BASIC `RND` — the contrast case

**Status: VERIFIED against 2 ROM dumps + 1 disassembly + emulation.** AppleWin
`Apple2.rom` and apple2js `intbasic.ts` are identical over all of `$E000–$F7FF`. Labels
come from Paul R. Santa-Maria's disassembly as ported by Andy McFadden
(`IntegerBASIC.html`). **Caveat:** only one disassembly was found. Woz's original source
was not located, so the *label names* rest on a single source. The *bytes* rest on two
dumps, and the *behaviour* on emulation plus a Python model that reproduced the ROM's
output exactly (300 of 300 consecutive calls). `tools/verify.py` re-checks the bytes.

Labels: **(a)** documented, **(E)** emulated, **(c)** inference.

---

## 1. Listing

```
; ROM: integer
;               Integer BASIC, (C) 1977 Apple — S. Wozniak.  Token $2F RND
EF4E: 20 15 E7     RND       JSR GET16BIT         ; ACC ($CE/$CF) = argument N
EF51: A5 4E                  LDA MON_RNDL         ; low byte of result-to-be
EF53: 20 08 E7               JSR LE708            ; push A as low byte of a new noun-stack value
EF56: A5 4F                  LDA MON_RNDH
EF58: D0 04                  BNE LEF5E
EF5A: C5 4E                  CMP MON_RNDL         ; RNDH=0: carry set only if RNDL=0 too
EF5C: 69 00                  ADC #$00             ; ...so state $0000 becomes $0100 (no lock-up)
EF5E: 29 7F        LEF5E     AND #$7F             ; clear bit 15 -> 15-bit value
EF60: 85 4F                  STA MON_RNDH
EF62: 95 A0                  STA NOUNSTKC,X       ; high byte of pushed value
EF64: A0 11                  LDY #$11             ; 17 shift steps
EF66: A5 4F        LEF66     LDA MON_RNDH
EF68: 0A                     ASL A
EF69: 18                     CLC
EF6A: 69 40                  ADC #$40             ; bit 7 of (2*RNDH + $40) = RNDH.b6 XOR RNDH.b5
EF6C: 0A                     ASL A                ; ...into carry
EF6D: 26 4E                  ROL MON_RNDL         ; shift the 16-bit register left,
EF6F: 26 4F                  ROL MON_RNDH         ; feedback bit enters at bit 0
EF71: 88                     DEY
EF72: D0 F2                  BNE LEF66
EF74: A5 CE                  LDA ACC
EF76: 20 08 E7               JSR LE708            ; push N
EF79: A5 CF                  LDA ACC+1
EF7B: 95 A0                  STA NOUNSTKC,X
EF7D: 4C 7A E2               JMP MOD              ; result = value MOD N
```

Zero-page equates from the same listing: `MON_RNDL = $4E`, `MON_RNDH = $4F`,
`NOUNSTKL = $50`, `NOUNSTKH = $78`, `NOUNSTKC = $A0`, `ACC = $CE`. **(a)**

## 2. Walkthrough

1. Evaluate the argument N into `ACC`.
2. Take the **current** 16-bit `$4E/$4F`, clear bit 15, and push that 15-bit value as the
   operand. (If the register is all zero it is forced to `$0100` first.)
3. Clock the register **17 times** as a shift register. Feedback = bit 14 XOR bit 13,
   entering at bit 0. The pushed value is the pre-shift state; the shifted state is what
   the *next* call sees. **(a)**
4. Push N and fall into the `MOD` operator: `RND(N) = value MOD N`.

The low 15 bits form a Fibonacci LFSR with polynomial x¹⁵ + x¹⁴ + 1. A model of this
code has period **32,767** (2¹⁵−1, maximal) from a nonzero state **(E, model)**. But
`KEYIN` **adds** its wait count to the same register every time the program or user
waits for a key. So each keypress knocks the LFSR to a new, timing-dependent point in its
cycle. **(a)** from §1 and `keyboard-seed.md`.

## 3. Behaviour (emulated on the ROM) **(E)**

| Expression | Result |
|---|---|
| `RND(10)`, 400 calls | min 0, max 9 |
| `RND(-10)`, 400 calls | min −9, max 0 |
| `RND(1)` | always 0 |
| `RND(0)` | `*** >32767 ERR` (from `MOD`) |

The 1978 Red Book's Integer BASIC summary (OCR, partly garbled) says the same thing:
"Gives random number between 0 and (expression −1) if expression is positive; if minus,
it gives random number between 0 and (expression +1)." **(a)**

The same 5-line program, typed and `RUN` on a cold boot **(E)**:

| Simulated key-wait per keystroke | Output |
|---|---|
| 1 loop each (run 1) | `71 4 52 54 4 67 47 7` |
| 1 loop each (run 2, identical timing) | `71 4 52 54 4 67 47 7` |
| 200–20,000 loops (fixed pseudo-random timing) | `17 47 66 25 69 0 16 96` |

Output depends only on keystroke timing. Identical timing gives identical output. A
human cannot reproduce timing to the loop iteration, so in practice it differs per run.

## 4. Contrast with Applesoft

| | Integer BASIC `RND(N)` | Applesoft `RND(X)` |
|---|---|---|
| Type | 15/16-bit LFSR, integer result `0..N-1` | FP multiply + byte swap + renormalize, result in (0,1) |
| State | `$4E/$4F` (2 bytes), shared with `KEYIN` | `$C9-$CD` (5 bytes), private |
| Keyboard timing | **mixed in automatically** at every key wait | **never** read; programmer must `PEEK(78)/PEEK(79)` |
| After power-on | depends on uninitialized `$4E/$4F` + every keystroke wait | fixed 4 bytes + uninitialized `$CD` |
| Reseed API | none (no negative/zero semantics; `RND(0)` is an error) | `RND(-X)` reseeds; `RND(0)` repeats the last value |
| Short-term structure | successive states 17 LFSR steps apart (c) | observed cycles 37,758 / 32,366 (E) |

Framing for the slide **(c)**: Woz's Integer BASIC couples its generator directly to the
only timing source the machine has. Microsoft's floating-point BASIC, dropped into the
same machine, decouples from it. Its `RND` is deterministic unless the programmer knows
to fold in `PEEK(78)`. Neither has an entropy source in the modern sense.
