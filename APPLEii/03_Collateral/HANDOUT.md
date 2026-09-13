# Applesoft's Loaded Dice: one-page handout
*Jeff Robison · VCF Midwest 21 · 2026*

## The problem
Power on an Apple ][+ or //e and type `PRINT RND(1)`, then power-cycle it and type it again. You get the **same number** every time. Rerun the program, or reboot DOS, and you get different numbers. That's why the problem went unnoticed for years.

> "exactly the same sequence each time the machine is powered on." (J. W. Aldridge, 1987)

## Why
- **Integer BASIC (1977, Wozniak)** used the monitor's keyboard-wait counter at `$4E/$4F` (78/79) directly as its generator state. Every wait for a keypress stirred it.
- **Applesoft II (Microsoft's 6502 BASIC, licensed by Apple)** keeps its own seed at `$C9–$CD` (201–205). At cold start it copies the seed from ROM (`$F123: 80 4F C7 52 58`), but the copy loop at `$F150` (`LDX #$1C`) is **off by one**. Only four bytes are copied, and `$CD` keeps whatever RAM held.
- The counter still runs under Applesoft, but `RND` never reads it.

## What your machine might print
| `PEEK(205)` at power-on | First `RND(1)` |
|---|---|
| 255 / 254 | .973136996 |
| 0 | .270011996 |
| 88 | .512199496 |

These values come from running the real ROM routine in an emulator. The 256 possible byte values give 181 different first numbers.

## The generator itself falls into short loops
Every cold start ends in a loop of **37,758**, **32,366**, **202**, **4,082** or **12,559** numbers, out of a seed space of about 4 billion. Kaner & Vokey reported 202, and Sander-Cederlof reported 37,758. Both came from the same generator, started from a different uncopied byte.

## Who got hurt
In Aldridge's 1987 memory experiment, each subject was supposed to get an individually randomized word list. The subjects tested first thing each day, right after power-on, all got the same list.

## Fix it in your own programs
```
10 PRINT "PRESS A KEY" : GET A$
20 X = RND(-(PEEK(78) + 256*PEEK(79)))
```
This is the advice Apple gave Aldridge's lab. The seed comes from how long you took to press the key. Call it after a keypress. If both bytes are 0, the call acts as `RND(0)` and does not reseed.

## Fix it for programs you can't edit
The presenter's language-card patch copies ROM to language-card RAM and routes `RND` through a small front end at `$F5CB`. That address is HFIND, which no Applesoft routine calls. `RND(-n)` and `RND(0)` behave as documented. The patch fixes the seed, not the generator.
**Link and QR:** *[presenter to add]*

## Read more
- Aldridge, *Behavior Research Methods, Instruments, & Computers* 19(4), 1987
- Sander-Cederlof, *Apple Assembly Line*, May 1984 (txbobsc.com/aal)
- Kaner & Vokey, *MICRO*, June 1984 (kaner.com/pdfs/random.pdf)
- McFadden, 6502disassembly.com
- Microsoft BASIC-M6502 source, github.com/microsoft/BASIC-M6502
