# Applesoft's Loaded Dice
### The truth about randomness on the Apple II, then and now
Jeff Robison · VCF Midwest 21 · 2026

---

## The problem
Power on an Apple II Plus or IIe and type `PRINT RND(1)`. Then switch it off and back on,
and type it again. You get the same number.

A psychology lab found this out the hard way. In a 1987 memory experiment, every day's first
subject got the same "individually randomized" word list, because that subject was always
tested right after the computer was switched on. *(Aldridge, 1987)*

## Why nobody noticed
Only a power-on repeats the sequence. Running the program again, rebooting DOS, or pressing
Ctrl-Reset all give different numbers, so from the programmer's desk everything looked random.

## 1977 vs 1978
- **Integer BASIC (Woz, 1977)**
  - `RND` at `$EF4E` is a 15-bit shift register with a period of 32,767.
  - Its state *is* the counter at `$4E/$4F`, which the monitor's `KEYIN` loop increments about
    68,000 times a second while it waits for a key.
  - So the seed came from you: how long you took to press a key.
- **Applesoft II (Microsoft's 6502 BASIC, licensed by Apple)**
  - `RND` at `$EFAE` keeps its own seed at `$C9–$CD`, filled from ROM at power-on.
  - It never reads `$4E/$4F`, even though the counter keeps running.

## One byte short
The cold-start loop at `$F150` (`LDX #$1C`) copies only four of the five seed bytes. The fifth,
`$CD`, is whatever RAM held at power-on.

| `$CD` at power-on | first `RND(1)` |
|---|---|
| `$FE` / `$FF` | .973136996 |
| `$00` | .270011996 |
| `$58` (the byte Microsoft intended) | .512199496 |

Across all 256 possible values there are 181 different first numbers. Each machine still
repeats its own. Sander-Cederlof published the one-byte fix in 1984: change `$F151` from `$1C`
to `$1D`.

## Two published loops, one generator
- Kaner & Vokey found `RND` falling into a loop of **202** numbers.
- Sander-Cederlof saw repetition start at the **37,758th** number.

Both were right. Which loop you land in depends on that uncopied byte.

## Seed it yourself
```
10 PRINT "PRESS A KEY" : GET A$
20 X = RND(-(PEEK(78) + 256 * PEEK(79)))
```
This is what Apple advised in 1987. It only works after a key wait. On a Commodore, the
equivalent is `RND(-TI)`.

## Try it yourself
The patch and loader are at: **[URL: Jeff to supply]**

## Further reading
- Aldridge, "Cautions regarding random number generation on the Apple II," *Behavior Research Methods, Instruments, & Computers* 19(4), 1987
- Kaner & Vokey, "A Better Random Number Generator for Apple's Floating Point BASIC," *MICRO*, June 1984
- Sander-Cederlof, "Random Numbers for Applesoft," *Apple Assembly Line*, May 1984 (txbobsc.com)
- Applesoft disassembly with S-C DocuMentor comments: 6502disassembly.com/a2-rom/Applesoft.html
- Microsoft BASIC M6502 source: github.com/microsoft/BASIC-M6502
