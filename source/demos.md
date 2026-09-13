# Live demonstration programs

Every program below was typed, character for character, into an emulated Apple ][+
(AppleWin II+ ROM on a py65 6502 core; no DOS). The expected output blocks are the
emulator's actual screen output, and `tools/verify.py` re-runs each block and diffs it.
**Not yet tried on real hardware or on AppleWin itself**; do one rehearsal on the show
machine.

Conventions: Applesoft demos assume `]` with no DOS unless noted. Applesoft `LIST` will
re-space lines (`INT (R * T)`), which is normal.

---

## Demo 1 — Post-cold-start determinism (thesis item 3)

### Demo 1A: straight after power-on

Type immediately after a cold start (power-on, no disk, or `CALL -151` then `E000G` —
but see the note on `$CD`).

```basic
10 FOR I = 201 TO 205: PRINT PEEK (I);" ";: NEXT I: PRINT
20 FOR I = 1 TO 5: PRINT RND (1): NEXT I
RUN
```

Expected, on a machine or emulator whose RAM held `$00` at `$CD`:

```text
128 79 199 82 0 
.270011996
.139756248
.690102028
.141352116
.152267027
```

**What it proves:** the generator starts from a constant burned into ROM
(`80 4F C7 52` at `$F123`). The fifth byte (`PEEK(205)`) is leftover RAM because
the cold-start copy loop is one byte short. Run it on two machines: if byte 205 matches,
the "random" numbers match. With `$CD = 255` the first line reads `128 79 199 82 255` and
the numbers are `.973136996 .103117626 .0177148333 .779343355 .551834438`. A second
`RUN` continues the sequence rather than repeating it. Ctrl-RESET does **not** restore
the seed (both emulated).

### Demo 1B: exact replay anywhere

```basic
10 POKE 201,128: POKE 202,79: POKE 203,199: POKE 204,82: POKE 205,0
20 FOR I = 1 TO 5: PRINT RND (1): NEXT I
RUN
RUN
```

Expected, identical on both runs:

```text
.270011996
.139756248
.690102028
.141352116
.152267027
.270011996
.139756248
.690102028
.141352116
.152267027
```

**What it proves:** the entire future of `RND` is those five bytes. Line 10 writes
exactly what `COLD.START` leaves (with `$CD=0`), and every run reproduces the power-on
sequence on any Apple ][+ or //e.

---

## Demo 2 — A stuck low-order bit (thesis item 1)

```basic
10 T = 33554432: U = 16777216: N = 0: M = 0
20 FOR I = 1 TO 200
30 R = RND (1)
40 X = INT (R * T): IF X / 2 <> INT (X / 2) THEN N = N + 1
50 Y = INT (R * U): IF Y / 2 <> INT (Y / 2) THEN M = M + 1
60 NEXT I
70 PRINT "BIT 25 SET: ";N;" OF 200"
80 PRINT "BIT 24 SET: ";M;" OF 200"
RUN
```

Expected, when run straight after a cold start with `$CD=0`:

```text
BIT 25 SET: 200 OF 200
BIT 24 SET: 93 OF 200
```

From any other starting point the first line reads **196–200**. That range comes from
every 200-call window of a 57,021-call run. The second line wanders around 100: 72–127
across the same windows.

**What it proves:** the 25th binary digit of `RND(1)` is (almost) always 1, while its
neighbour behaves like a coin. `T` = 2²⁵ and `U` = 2²⁴ are typed as literals, because
Applesoft's `^` goes through `LOG`/`EXP` and is not exact. Multiplying by a power of two
and taking `INT` is exact in Applesoft's 32-bit mantissa.

Cause, for the slide: `RND` swaps the top and bottom mantissa bytes. The top byte always
has its normalization bit set, so that bit lands at weight 2⁻²⁵ every time
(`applesoft-rnd.md` §5.3).

Honest scope: this is a *stuck bit*. The high-order digits of `RND` pass simple
serial-pair tests at this scale, so do not present this demo as "RND values are
correlated".

Runtime on real hardware is not measured. 200 iterations with two `INT`s each should be
well under a minute. **(c)**

---

## Demo 3 — `RND(0)` and negative seeds (thesis item 4)

```basic
10 PRINT "RND(-1) = "; RND ( - 1)
20 FOR I = 1 TO 3: PRINT RND (1): NEXT I
30 X = RND ( - 1): PRINT "RESEEDED:"
40 FOR I = 1 TO 3: PRINT RND (1): NEXT I
50 PRINT "RND(0) = "; RND (0)
60 PRINT "RND(0) = "; RND (0)
70 FOR K = 1 TO 4: PRINT "RND(-";K;") = "; RND ( - K): NEXT K
80 FOR I = 1 TO 3: X = RND ( - 7): PRINT RND (1): NEXT I
RUN
```

Expected, the same every run, from any state:

```text
RND(-1) = 2.99196472E-08
.738207502
.272707136
.299733446
RESEEDED:
.738207502
.272707136
.299733446
RND(0) = .299733446
RND(0) = .299733446
RND(-1) = 2.99196472E-08
RND(-2) = 2.99205567E-08
RND(-3) = 4.48217179E-08
RND(-4) = 2.99214662E-08
.808482028
.808482028
.808482028
```

**What it proves:**
* A negative argument **is** the seed. Same argument, same sequence (lines 10–40), and
  nothing about it is random.
* The value `RND(-K)` *returns* is not in a useful range: small integers give ≈3×10⁻⁸.
  Code that does `X = INT(RND(-S) * 100)` gets 0.
* `RND(0)` returns the **last** value again (lines 50–60). The Applesoft II manual (Aug
  1978) says "X<=0 starts a new sequence of random numbers using X". For X=0 the ROM does
  not do that. Microsoft's source comment agrees with the ROM: "IF ARG=0, THE LAST RANDOM
  NUMBER GENERATED IS RETURNED."
* Line 80 is the classic misuse: reseeding inside the loop repeats one number forever.

---

## Demo 4 (optional) — The keyboard-timing seed idiom (thesis item 2)

```basic
10 PRINT "PRESS ANY KEY";: GET A$: PRINT
20 S = PEEK (78) + 256 * PEEK (79)
30 X = RND ( - S)
40 PRINT "SEED ";S;" -> ";RND (1)
RUN
```

The output depends on the counter reached while waiting. The emulated key waits for
Demo 4 were 4,660 loops, 4,661 loops, and 30,000 loops. Program entry adds 1 per
keystroke to each run, which is why the seeds shown are 132 higher than the waits.

```text
PRESS ANY KEY
SEED 4792 -> .69903216
```
```text
PRESS ANY KEY
SEED 4793 -> .521940801
```
```text
PRESS ANY KEY
SEED 30132 -> .0401755319
```

**What it proves:** the "randomness" is `$4E/$4F`, a 16-bit count of how long you took
to press a key (≈68,000 counts/s, `keyboard-seed.md`). There are at most 65,536 possible
games. If S happens to be 0, `RND(-0)` does not reseed at all. Live: `RUN` it twice,
pressing the key quickly once and slowly once. The 16-bit counter runs through all
65,536 values about once a second, so the seed is just the fraction of a second at which
you happened to press the key: a stopwatch, not an entropy source.
Emulation checked the three wait counts above. The per-second rate is the
`keyboard-seed.md` estimate, not a measurement.

---

## Integer BASIC contrast (optional; needs Integer BASIC: `INT` from DOS, or a II/Language Card)

```basic
10 FOR I=1 TO 8
20 PRINT RND(100);" ";
30 NEXT I
40 PRINT
50 END
RUN
```

Expected: **different on every run by a human**. In emulation with every keystroke
waiting exactly one loop, the output was

```text
71 4 52 54 4 67 47 7 
```

That output was identical on a second cold boot with identical timing. With
different timing it was `17 47 66 25 69 0 16 96`.

**What it proves:** Integer BASIC's `RND` state *is* the `$4E/$4F` counter, so
keystroke timing feeds in automatically. Applesoft's does not. Also try `PRINT RND(0)` →
`*** >32767 ERR`.
