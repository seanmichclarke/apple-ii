# Q&A prep

Questions this audience is likely to ask, with short answers Jeff can give from the
stage. Evidence labels match `FACT_SHEET.md`:

- **(a)** documented
- **(E)** measured on the ROM code
- **(c)** inference

Questions marked **[needs Jeff]** depend on something in `OPEN_ITEMS_FOR_JEFF.md`.

---

## About the number

**"I rebooted and got a different number."**
Only a power-on repeats. A warm restart leaves the fifth seed byte holding whatever the
last `RND` put there.
(a) Aldridge 1987; AAL May 1984.

**"My IIe prints a different number than yours."**
One seed byte is never set. The ROM copies 4 of 5 bytes, so your machine's power-on RAM
chooses the fifth. Your machine will still repeat *its own* number every power-on. Of
256 possible values, 181 give different first numbers.
(a) + (E).

**"My emulator prints .270011996."**
Your emulator zeroes RAM at power-on, so `$CD=$00`. That's the same bug, just with a
different byte.
(E).

**"So is it a fixed seed or not?"**
Four fixed bytes plus one leftover byte. On a given machine that's effectively fixed,
and that's what Aldridge's lab saw.
(a) + (c).

## About the generator

**"Is this an LCG? What about Marsaglia's planes?"**
Not a textbook LCG. It has no modulus. It does a float multiply, swaps the highest and
lowest mantissa bytes, and renormalizes. Lattice theory doesn't carry over. Its
documented failures are short loops and seeding.
(a) code; (c).

**"What's the period?"**
There isn't one period. Depending on the seed, it falls into one of several loops. The
two published figures are both right:

- Kaner & Vokey saw 202.
- Sander-Cederlof saw 37,758.

Across all 256 cold-start bytes: 43% → 37,758, 30.5% → 32,366, 23% → 202, and the rest
→ 4,082 or 12,559.
(a) + (E).

**"The listing says the add does nothing."**
Those are Bob Sander-Cederlof's comments, not Microsoft's. The addend is so small it's
lost to precision. Running the ROM, it changes the stored seed in 5 of 57,021 steps.
(E).

**"The constants are truncated."**
Yes. Each is 4 bytes, but the loader reads 5. So the multiplier picks up `$68`, the first
byte of the next constant, and actually runs as 11,879,546.40625. The truncation is in
Microsoft's source.
(a).

**"Are the leading digits patterned?"**
Not visibly. They pass uniformity and serial-pair χ² tests. What you *can* show:
- the short loops
- fraction bit 25, which is set 99.75% of the time
- the seed problem

(E).

## About who did it

**"So Woz broke it?"**
No. Woz's Integer BASIC took its randomness from you, the keyboard counter. Applesoft is
Microsoft's 6502 BASIC. Its generator ignores the counter the monitor was still running.
(a).

**"Why didn't Microsoft use `$4E/$4F`?"**
No record explains it. Microsoft's source had two `RND`s: one for Commodore that read
hardware timers, and one for everyone else. Apple got the everyone-else version. Apple
edited code inside the very loop that drops the seed byte (it added `STX SPEEDZ`), and
still never connected the counter. Say "nobody connected it," not "nobody knew."
(a) evidence; (c) motive.

**"Does the C64 have this?"**
Same Microsoft generator, same constants. But Microsoft's Commodore build made `RND(0)`
read hardware timers and added `TI`, starting with the first PET ROM in 1977. Commodore
carried that forward to the C64. On a Commodore the idiom is `RND(-TI)`. On the Apple
it's `RND(-(PEEK(78)+256*PEEK(79)))`.
(a).

**"Was Integer BASIC's generator actually good?"**
For games, yes: a 15-bit maximal shift register, period 32,767, stirred by every key
wait. For statistics, no: `RND(X)` is state `MOD X`, and every program shares one
32,767-step cycle.
(a) + (E).

## About the fix

**"Just seed it first."**
Agreed, for new code. Apple told Aldridge's lab exactly that in 1987. But you can't edit
software you didn't write. The failure is silent, so only people who already know can
fix it. And this machine used to do it automatically.
(a) Aldridge.

**"Why not replace the generator?"**
Three reasons:
- Speed.
- There's no room.
- `RND(-n)` has to keep producing the same sequence, because programs depend on it.

The patch fixes the seed, not the generator.

**"Does the patch fix the 202 loop?"**
No. It fixes where the sequence starts. A seed from the counter can still land in the
202-loop. Both `RND(-52894)` and `RND(-22258)` do.
(E).

**"What's at `$F5CB`?"**
HFIND: 53 bytes, marked "not called by any Applesoft routine." No `JSR` or `JMP` to it
exists anywhere in the II Plus ROM. `$F600` right after it is an `RTS` that HLIN branches
to, so the patch stays within 53 bytes. The only thing that breaks is a program doing
`CALL 62923` itself.
(a). Byte count **[needs Jeff]**.

**"What does `RND(1)` do twice in a tight loop with no keypress?"**
**[needs Jeff]**. Answer from the patch listing.

**"Does `RND(-1)` then `RND(1)` still repeat if I `GET` in between?"**
**[needs Jeff]**. Must be yes for "works as documented" to hold.

**"What about a turnkey game that calls `RND` before any key?"**
The counter only moves while something waits for a key. Before the first key wait, it
holds whatever boot left there. Aldridge flagged the same limit for Apple's own advice.
(a) + (c).

**"Does it work under ProDOS?"**
**[needs Jeff]**. Likely not as written: ProDOS lives in language-card RAM.

**"Press Ctrl-Reset. Still patched?"**
**[needs Jeff]**. On the IIe and IIc, RESET forces ROM read.

**"I typed `FP`. Am I still patched?"**
**[needs Jeff]**. Under DOS 3.3, `FP`/`INT` flip the language-card switches.

**"How is yours better than the 1984 fixes?"**
The 1983–84 fixes (Call-A.P.P.L.E., AAL, Kaner & Vokey) replaced `RND` through `USR`,
so programs had to change. This one keeps `RND` and fixes the default, so unmodified
programs benefit.
(a) for the earlier fixes.

## About "Now"

**"Does anyone still make this mistake?"**
Yes, as a parallel, not as a lineage. In 2006 a Debian change removed nearly all the
entropy from OpenSSL's random number generator. The output still looked random, and keys
were predictable until the 2008 disclosure (CVE-2008-0166). The shape is the same: the
entropy input was silently disconnected, and nothing looked wrong.
(a).
