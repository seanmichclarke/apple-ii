# Q&A prep: the hard questions this audience will ask

Short answers first, followed by the evidence behind each. Labels: **[DOC]** primary source, **[EMU]** measured on the real ROM code, **[INF]** inference, **[TEST]** only real hardware can answer.

---

### The number itself
**"I rebooted and got a different number."**
Only a power cycle repeats. Cold start copies 4 of the 5 seed bytes, and the fifth (`$CD`) keeps whatever the last run left there. [DOC Aldridge 1987, AAL May 1984; EMU]

**"My IIe prints a different number than yours."**
`$CD` depends on that machine's power-on RAM. The 256 possible values give 181 different first numbers. Your machine still gives the same number every time you power it on. [EMU; the power-on RAM contents are INF]

**"So it isn't a fixed seed from ROM?"**
Four bytes are fixed. The fifth is leftover RAM because of Microsoft's off-by-one, `LDX #$1C` at `$F150`. The fix is one byte: `$F151` from `$1C` to `$1D`. [DOC]

**"My emulator zeroes RAM and prints .270011996."**
That matches `$CD = $00`. [EMU]

### The generator
**"Is it an LCG? Where's the spectral test?"**
Not a textbook one. It's a floating-point multiply, then a byte swap, then a renormalize, with no modulus. Lattice theory doesn't transfer to it directly, and nobody has published a spectral test of it. Its documented failures are short loops and seeding. [DOC listing; INF]

**"What's the period?"**
There isn't a single period. Every cold start ends in one of five loops: 37,758, 32,366, 202, 4,082 or 12,559 calls. That covers both published figures: Kaner & Vokey saw 202 and Sander-Cederlof saw 37,758. [EMU sweep of all 256 `$CD` values]

**"Your slide says the add does nothing."**
It's lost to precision. With the add removed, the sequence first diverges at call 3,886, and across the trajectory the add changed 5 of 57,021 steps. [EMU]

**"The constants are truncated."**
Yes. Each is 4 bytes, and the loader reads 5. The multiplier picks up `$68` from the next constant, making it 11,879,546.40625. The truncation is in Microsoft's source, not Apple's port. [DOC]

**"Which two bytes does it swap?"**
`FAC+1` and `FAC+4`, the highest and lowest mantissa bytes. AAL 1984 says "the middle two bytes", which is wrong. [DOC listing and Microsoft source]

### Attribution
**"So Woz broke it?"**
No. Woz's Integer BASIC read the counter. Applesoft is Microsoft's 6502 BASIC, which Apple licensed. [DOC]

**"Who at Microsoft wrote RND?"**
The record doesn't say. The 6502 port is credited to Weiland & Gates, and the math package descends from Davidoff's 8080 work. Don't name one person. [DOC / contested]

**"Why didn't Microsoft or Apple use `$4E/$4F`?"**
No record says why. Microsoft's source had two RNDs: the Commodore build read hardware timers and every other target got a fixed seed. Apple edited the seed-copy loop itself, adding `STX SPEEDZ`, and kept the short count. Say "nobody connected it", not "nobody knew". [DOC for the facts; the motive is INF]

**"Does the C64 have this too?"**
It has the same generator with the same constants. But Microsoft's own Commodore build made `RND(0)` read hardware timers and added `TI`, back in the first PET ROM in 1977. The idiom there is `RND(-TI)`. [DOC]

**"The comment says 'very poor RND algorithm'."**
That's Bob Sander-Cederlof's annotation in S-C DocuMentor, not Microsoft's source. [DOC]

### Integer BASIC
**"Integer BASIC's generator is bad too."**
Agreed: 15 bits, one 32,767-step cycle, and MOD bias. The claim is about the *default*. Integer BASIC used your keypress timing automatically, and Applesoft threw it away. [EMU; DOC]

**"Integer BASIC also repeats if no key is pressed."**
True. The counter moves only while KEYIN waits, and a game polling `$C000` never advances it. [DOC]

**"Is `$4E/$4F` a clock?"**
No. It's a loop counter inside KEYIN, about 68,000 counts per second, and it wraps about once a second. The Apple II has no timer. [DOC; rate INF]

### The fix
**"Why not just `RND(-(PEEK(78)+256*PEEK(79)))`?"**
For new code, do exactly that. It's what Apple told Aldridge's lab. The patch is for existing programs, which you can't edit and which fail silently. Watch the edge case: if both bytes are 0, the call becomes `RND(0)` and doesn't reseed. [DOC; INF]

**"What's at `$F5CB`?"**
HFIND. S-C DocuMentor says it's "not called by any Applesoft routine", and the ][+ ROM has no `JSR` or `JMP` to it. Only a program that calls 62923 directly would break. [DOC; checked]

**"How big is the patch? Did you test HPLOT TO?"**
It must fit in `$F5CB–$F5FF`, which is 53 bytes. `$F600` is the RTS that HLIN branches to. **[TEST: presenter confirms length and runs T8]**

**"What does RND(1) do in a tight loop with no keypress?"** **[TEST T4: presenter must know]**

**"Does RND(−n) still repeat?"** It should. **[TEST T5]**

**"Does it fix the 202 loop?"**
No. It fixes the seed, not the generator. Replacing the generator would break programs that rely on `RND(-n)` repeating, and there's no room in ROM. [INF]

**"ProDOS lives in the language card."**
Answer only with what you've tested. **[TEST T9]** If it's untested, say "not for ProDOS yet."

**"Ctrl-RESET on my IIe."** **[TEST T9]**

**"How is this better than the 1983–84 fixes?"**
Call-A.P.P.L.E., Sander-Cederlof, Kaner & Vokey and Moore all replaced RND with a `USR` routine, so programs had to change. This patch is transparent: existing programs get a seeded RND unmodified. The trade-off is that it needs a language card.
