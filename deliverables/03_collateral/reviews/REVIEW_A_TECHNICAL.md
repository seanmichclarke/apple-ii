# Review A — Technical Adversary

**Talk:** "Applesoft's Loaded Dice: The Truth About Randomness on the Apple II, Then and Now" (Jeff Robison, VCF Midwest 21, 2026)
**Deck reviewed:** `deck/extract/ppt/slides/slide1..10.xml`, including the embedded images (`ppt/media/image1..11.png`)
**Thesis under attack:** seed regression. Integer BASIC's RND reads the KEYIN counter at `$4E/$4F`. Applesoft seeds `$C9` from a fixed ROM value, so every cold boot prints `PRINT RND(1)` = `.973136996`.
**Reviewer stance:** I'm the hardest person in the room. I own a ][+, I've read the S-C DocuMentor, and I brought a laptop running an emulator.

Severity key: **TALK-ENDING** means the presenter loses the room or the thesis. **EMBARRASSING** means a correct heckle the presenter can't answer. **MINOR** means a pedant scores a point.

The speaker notes (`notesSlideN.xml`) hold nothing but page numbers, so there's no backup material behind any slide. Every finding below has to be answered on stage from memory, or the deck has to change.

---

## How I checked (so you can reproduce it)

- Applesoft listing: 6502disassembly.com `a2-rom/Applesoft.html`. This is McFadden's SourceGen conversion of Bob Sander-Cederlof's S-C DocuMentor, built from AppleWin's `Apple2_Plus.rom`.
- I ran the **real ROM code** for `RND` at `$EFAE` under py65, using the team's own harness `research/tools/rnd_emu.py`. ROM images came from the AppleWin repo `resource/` directory: `Apple2_Plus.rom` (SHA-1 `33a24f5489ba9195b44be77d9afb2252594cb5c7`), `Apple2e.rom` and `Apple2e_Enhanced.rom`. Scratch files are in `/tmp` only. Nothing was written to the project outside `review/`.
- I ran `woz/intbasic_rnd_emu.py` as-is.
- I checked the AAL citations against the txbobsc.com archive: `aal8108.html` and `aal8405.html`.
- I could **not** check the //c ROM's Applesoft region. The 6502disassembly //c listing leaves `$D000-$F7FF` as undisassembled junk. I also couldn't check `LC_Loader.bin` or `Patch_lc.bin`, because neither file is anywhere in the workspace.

---

## 1. TALK-ENDING: `.973136996` doesn't come from a fixed ROM seed. It depends on a byte the ROM never sets.

**Slides:** 2 (the hook), 6, and the whole corrected thesis. Slide 8 cites the source that contradicts it.

**Weakness.** The cold-start copy loop at `$F150` (`LDX #$1C` / `LDA GENERIC_CHRGET-1,X` / `STA CHRGET-1,X`) is off by one. It copies 4 of the 5 seed bytes (`$80 $4F $C7 $52`) into `$C9-$CC`. The 5th byte, `$58`, never reaches `$CD`. The deck's own source, Sander-Cederlof in *AAL* May 1984, says exactly this, and slide 8 lists it as "Found the startup bug. The seed copy is off by one." The same article goes on: "not copying the last byte could make the numbers generated a little more random from one run to the next."

`$CD` is the least significant mantissa byte of the seed. `RND` then swaps `FAC+1` and `FAC+4` at `$EFCC-$EFD2`, which moves the low byte of the product into the **most** significant position of the result. So the uninitialized byte ends up driving the leading digits.

**I measured this on the genuine ROM code:**

| `$CD` at first `RND(1)` | First `RND(1)` |
|---|---|
| `$00` | .270011996 |
| `$55` | .504386996 |
| `$58` (the value the ROM *meant* to copy) | .512199496 |
| `$AA` | .738761996 |
| `$FE` or `$FF` | **.973136996** |

The 256 possible values of `$CD` give **181 distinct first outputs**. Only `$FE` and `$FF` give the number on slide 2. The results are identical on the ][+, unenhanced //e and enhanced //e ROMs: the `RND` routine, the seed table and the copy loop are byte-identical in all three.

So slide 2 is reproducible only because `$CD` happens to hold `$FE` or `$FF` when `RND` first runs. The ROM doesn't put it there. Maybe power-on RAM on that machine settles to `$FF`, or some earlier code leaves it that way. The deck doesn't say. Also note that nothing in the ][+ Applesoft or Autostart F8 listings writes `$CD` (I searched both for zero-page writes to `$CD` and found none). DOS 3.3, ProDOS/BASIC.SYSTEM and the //e/c firmware weren't checked.

**Hostile questions:**
> "Your own slide 8 says the seed copy is off by one. So the fifth seed byte is uninitialized RAM. How is `.973136996` 'a fixed value from ROM'? What's in `$CD` on your machine, and why?"

> "My emulator zeroes RAM at power-on and prints .270011996. Is my Apple broken, or is your thesis?"

> "After I've run any program that calls RND, I type PR#6. Cold start copies four bytes, `$CD` still holds whatever the last RND left there, and I get a different number. So 'every cold boot' means 'every *power-on* where RAM comes up as `$FF`'. Yes?"

**What the presenter must add or change:**
- Reword the thesis. Something like: "Applesoft copies a *nearly* fixed seed from ROM. The byte it forgets depends on RAM state, which is usually the same at power-on, so in practice you usually see the same number." That's still a regression argument, but it's honest.
- Establish on **real hardware**, before the talk, what `$CD` holds at first `RND` on each target: ][+, //e, enhanced //e, //c, IIgs if claimed. Do it after a true power-on, after PR#6, after a DOS 3.3 boot and after a ProDOS/BASIC.SYSTEM boot. Put the table on a backup slide.
- If slide 2 is a live demo, do a true power cycle, not PR#6 or Ctrl-Reset. Know what you'll say if the number differs.
- Name the off-by-one on the main thesis slide instead of burying it in the sources slide. It's the most interesting detail in the story, and it's currently hidden on the slide that undercuts you.

---

## 2. TALK-ENDING: The patch is the "solution," and nobody can see what it does.

**Slide:** 9

**Weakness.** Slide 9 describes how the loader installs the patch: copy the ROM to the language card, put code at `$F5CB`, put a `JMP` at `$EFAE`. It never says what the code does to a *positive-argument* `RND`. "Relying on the KEYIN counter" could mean any of several things, and each one fails differently:

| If the patch… | Then… |
|---|---|
| reseeds from `$4E/$4F` on **every** `RND(1)` | The counter only moves while KEYIN is waiting. A `FOR I=1 TO 52: C(I)=RND(1): NEXT` with no keyboard I/O in between reads the same counter 52 times. The result is identical or near-identical values, which is far worse than stock Applesoft. |
| mixes the counter into the LCG state on every call | It breaks the **documented** contract shown on slide 7: "If a particular negative argument is used… subsequent random numbers generated with positive arguments will follow the same sequence each time." Any INPUT or GET between calls changes the sequence, so repeatable simulations and debugging break. Slide 9 claims negative functionality is "preserved," but the negative contract *is* the repeatability of what follows. |
| seeds **once** on the first positive call | It needs a "seeded" flag. Where is it stored? The language card is write-protected at run time, and zero page belongs to Applesoft. Does RUN, NEW or CLEAR reset it? Does `RND(-n)` clear it? If the flag lives in RAM that isn't initialized, the first-boot problem from finding 1 comes back. |
| builds a negative seed from the counter internally | When the counter reads `$0000`, `SIGN` (`$EB82`) returns 0, not −1. The call then goes down the `RND(0)` path, returns the old seed, and never reseeds. That happens rarely, but it's real, and someone in the room will spot it. |

The slide also says zero-argument behavior is "preserved." In stock Applesoft, `RND(0)` returns the seed unchanged (`$EFBC BEQ RTS_19`). If the patch changes the state *after* producing a value, `RND(0)` no longer returns "the most recent previous random number generated", which is the wording of the manual text on slide 7.

**Hostile questions:**
> "Put Patch_lc.bin on the screen. Every byte. What does `RND(1)` do on the second call in a tight loop with no keypress?"

> "Your slide 7 quotes the manual's promise that `RND(-n)` then `RND(1)` repeats. Does it still repeat if I do a GET between calls?"

**What the presenter must add or change:**
- Add a slide with the annotated patch listing: addresses, bytes and mnemonics. This audience won't accept a `.bin` filename in place of code.
- Add a demo or backup table showing stock and patched output side by side for:
  1. `RND(-1)` followed by five `RND(1)`, run twice, with a GET in between the second time.
  2. `RND(0)` right after `RND(1)`.
  3. 52 `RND(1)` calls in a tight loop.
  4. A turnkey HELLO program that calls `RND(1)` before any keyboard input.
- State in one sentence what "preserves negative and zero functionality" means, and show that the test above confirms it.

---

## 3. TALK-ENDING for "Try it yourself": the language-card loader conflicts with the systems people actually boot.

**Slides:** 9 and 10 ("Try it yourself")

**Weakness.** Slide 10 invites the audience to run this. The loader overwrites all of `$D000-$FFFF` in language-card RAM. That region is **already in use** in most real setups.

**Failure cases:**

1. **ProDOS 8.** The ProDOS kernel lives in language-card RAM. Running the loader under ProDOS/BASIC.SYSTEM overwrites the operating system. And even if it survived, BASIC.SYSTEM runs Applesoft from ROM and pages the LC in for MLI calls, so the patched copy would never be the one executing. *Hostile:* "I BRUN'd it from my ProDOS 2.4 disk and it hung on the next CAT. Did you test it under ProDOS at all?"
2. **DOS 3.3 with a language card.** The System Master loads the *other* BASIC into the LC, and `FP`/`INT` flip the LC switches. After the loader: does `INT` now enter patched Applesoft? Does `FP` switch back to ROM and **silently remove** the patch? What happens with a HELLO program that does either? *Hostile:* "I typed FP. Am I still patched? How would I know?"
3. **Original Apple II with Integer BASIC in ROM.** On that machine, Applesoft is the thing living in the LC. The loader copies motherboard ROM, which is *Integer BASIC*, over it, then writes `JMP $F5CB` at `$EFAE`. In Integer BASIC that address is the middle of other code (Integer's RND starts at `$EF4E`). The loader has to check the machine ID byte and refuse. *Hostile:* "What does your loader do on my Rev 0 with Applesoft loaded in the language card?"
4. **RESET.** On the //e and //c, RESET forces ROM read, so one Ctrl-Reset silently turns the patch off. For the ][+ Language Card and third-party 16K/32K/128K cards, whether RESET changes LC state has to be checked per card. Don't assert anything until it's tested. *Hostile:* "Press Ctrl-Reset, type RUN. Are you still patched?"
5. **Bank 1 vs bank 2.** `$D000-$DFFF` has two banks. The slide doesn't say which switches the loader uses: `$C081`×2 then `$C080`, versus the `$C089`/`$C088` family. If code later selects the other bank for reading, Applesoft's `$D000-$DFFF` disappears. Also, write-enable needs **two** consecutive *reads* of the switch. A single access, or a write, doesn't enable it, and a buggy loader "works" in some emulators and fails on real cards.
6. **Any program that uses the LC.** Plenty of software loads into or clears the language card: Pascal, CP/M-80 cards with LC, assemblers, many commercial programs, RAM-disk drivers, and the //e `/RAM` using aux LC with `ALTZP`. Any of these either destroys the patch or gets destroyed by it. *Hostile:* "So it's incompatible with anything that uses the 16K it takes over?"
7. **//c and IIgs.** Finding 1's ROM comparison covered only the ][+ and //e family, where `RND`, the seed table, the copy loop and `$F5CB-$F600` are byte-identical. The **enhanced** //e differs from the ][+ in 179 Applesoft bytes elsewhere, so "Applesoft is Applesoft" is already false. Nobody has verified the //c ROM revisions (255, 0, 3, 4, IIc Plus) or the IIgs ROM 01/03 Applesoft. *Hostile:* "Which //c ROM revision did you test on?"
8. **Interrupts on the //c, and mouse or serial IRQs on the //e.** With LC read enabled, vectors at `$FFFA-$FFFF` come from the LC copy. The copy made at load time *should* hold the same vectors, but that needs a test with a mouse card or //c serial port active. It's low probability, but it's a question the presenter should have an answer to.

**What the presenter must add or change:**
- Publish a **compatibility matrix** on a backup slide: machine × ROM revision × DOS 3.3 / ProDOS / no DOS × RESET behavior × FP/INT. Mark each cell tested on real hardware, tested in an emulator (name it), or untested.
- Make the loader **detect and refuse** when the ROM isn't Applesoft (check the ID byte), when ProDOS is present, or when the LC is already occupied. Say on the slide that it does.
- Or pick an installation that doesn't need the LC. A `USR` or `&` hook in main RAM (the approach in *AAL* May 1984 and the Call-A.P.P.L.E. Jan 1983 article, both already on slide 8) avoids nearly every failure above. The trade-off is that programs must call `USR` instead of `RND`. If the presenter keeps the LC approach, they need one sentence explaining why transparent `RND` replacement is worth this list of failures.

---

## 4. EMBARRASSING, possibly TALK-ENDING: the `$F5CB` / HFIND hedge

**Slide:** 9 ("may impact HFIND, supposedly unused by AppleSoft")

**What's actually established.** The S-C DocuMentor listing says, at `$F5CB`: `* HFIND - calculates current position of hi-res cursor * (not called by any Applesoft routine)`. A search of the listing finds no reference to `HFIND` other than its definition. So "supposedly unused *by Applesoft*" has a source, and the word "supposedly" is **self-inflicted damage**. Cite Sander-Cederlof and drop it.

**What isn't established, and is where the attack will land:**

1. **Nobody outside Applesoft calling it isn't the same as Applesoft not calling it.** HFIND is an ROM entry point in the hi-res package next to `HPOSN`, `HPLOT`, `HLIN` and `DRAW`. Machine-language hi-res utilities and games that read the hi-res cursor position after `DRAW` or `HPLOT` have a reason to `JSR $F5CB`. I haven't verified whether it appears in published entry-point lists from the period (the Apple II Reference Manual, Applesoft manual appendices, *What's Where in the Apple*, Nibble or Call-A.P.P.L.E. hi-res articles). **The presenter has to check before standing on it.** *Hostile:* "HFIND is a documented hi-res entry point. My shape-table editor calls it. What does it do after your patch?"
2. **Size limit.** HFIND runs from `$F5CB` to `$F5FF`, which is **53 bytes**. The next byte, `$F600`, is `RTS_22`, and it's **shared**: `HLIN` branches to it at `$F59C` (`BEQ RTS_22`) when a line finishes. `DRAW` starts at `$F601`. Any patch longer than 53 bytes breaks `HPLOT TO` line drawing (the branch lands in patch code), and a longer one also breaks `DRAW`/`XDRAW`. This layout is identical on the ][+, //e and enhanced //e ROMs I checked. *Hostile:* "How many bytes is your patch? Did you draw a line with HPLOT TO after installing it?"
3. **"May impact"** is the phrase that loses the room. For a patch to ROM, the only acceptable wording is "overwrites HFIND; here are the known callers; here's the test that shows HGR, HPLOT, HPLOT TO, DRAW, XDRAW and SCALE/ROT still work."

**What must be established before presenting:**
- The patch's exact byte length, with proof that it's ≤ 53 bytes and leaves `$F600` untouched.
- A search of period documentation for HFIND/`$F5CB` as a published entry point, with the result stated honestly on the slide.
- A hi-res regression demo or backup: shape-table DRAW, XDRAW, HPLOT TO, after patching.
- Or move the patch somewhere nobody would argue about. Ideally explain on the slide why `$F5CB` is the least-bad location in `$D000-$FFFF`, for example that no other 50-byte gap exists.

---

## 5. EMBARRASSING: "both are bad." The regression argument's weakest point.

**Slides:** 4, 6, and the thesis

**What a skeptic will say, all of it checkable:**

1. **Integer BASIC's generator is a 15-bit LFSR with a single cycle.** The team's own emulator, `woz/intbasic_rnd_emu.py`, confirms that feedback = bit14 XOR bit13, `RNDH` is masked with `AND #$7F`, and every start state tested lands in **the same cycle of 32,767**. A "seed" in Integer BASIC only picks a *position in one fixed 32,767-long sequence*. Any two runs are the same sequence, offset. With only 32,767 states, anyone who sees a few `RND(n)` outputs can brute-force where in the sequence they are. Slide 4 calls this "Sufficiently random."
2. **The state is exposed.** Integer BASIC `RND(n)` returns the 15-bit state `MOD n` (`JMP MOD` at `$EF7D`). A large `n` gives away most of the state in one call, and any `n` that isn't a power of two is biased.
3. **Integer BASIC only gets entropy if a human pressed a key.** The counter advances only inside KEYIN (the loop at `$FD1B`, shown on slide 5). A turnkey program that calls `RND` before any keyboard input, including one run from a HELLO file, starts from whatever the boot left in `$4E/$4F`. That's the same "predetermined starting point" the talk condemns in Applesoft. Games that poll `$C000` directly instead of calling KEYIN never advance the counter at all.
4. **The entropy was never taken away from Applesoft.** The KEYIN counter still runs while Applesoft waits at INPUT, GET or the `]` prompt. Slide 6 says so: "the seed for Integer BASIC remains." An Applesoft program can seed itself in one line with `X = RND(-(PEEK(78) + 256*PEEK(79)))`. Expect someone to say it was common knowledge in 1980. I haven't verified how widely it was published, so the presenter should find out. *Hostile:* "Why do I need a language-card ROM patch instead of one line of BASIC that every magazine printed?"
5. **Applesoft's cold-boot seed isn't fully fixed either.** See finding 1. A pedant can even argue the off-by-one gives Applesoft *more* boot-time variation than Integer BASIC's counter, which isn't touched until a key wait.
6. **The generator itself.** *AAL* May 1984 (on slide 8) reports the stock generator looping at the 37,758th number and calls the algorithm ruined by the byte-swap tweak. Call-A.P.P.L.E. Jan 1983 calls it "fatally flawed." The corrected thesis says "not skewed distribution." But if the patch (finding 2) keeps Microsoft's LCG and only fixes seeding, the talk has fixed the *less* serious flaw its own sources describe. The team's `research/tools/rnd_experiments.py` already has `mkcycles` and `classify` modes for exactly this. Run them and report what fraction of 16-bit seeds fall into short cycles. If most counter-derived seeds land in the same short attractor cycles, a better seed buys very little.

**Does the talk survive "both are bad"?** Yes, but only if the regression is stated precisely: **the regression is in the default, not the capability.** Integer BASIC gave you keystroke-timing variation *automatically*, because the generator state and the KEYIN counter are the same bytes. Applesoft kept the counter running and ignored it, so programmers who didn't know to add the PEEK got the same sequence every power-on. Claim that, concede points 1–3 and 6 openly on a slide, and the talk is stronger. Claim "Integer good, Applesoft bad" and it collapses.

**What the presenter must add:**
- A side-by-side slide: state size (15 bits vs ~32 bits of mantissa), period (32,767 vs *measured*, with a number), entropy source (automatic on key wait vs none by default), predictability, and the failure mode each one has.
- A slide on the one-line PEEK idiom, including an honest answer to "why patch at all?" Transparency for existing, unmodified programs is a reasonable answer, but it has to be said.
- The measured cycle structure of the Applesoft LCG for counter-derived seeds, or at least a statement of what's unknown.

---

## 6. EMBARRASSING: "Sufficient" is never defined, and slide 3 mixes up two properties.

**Slides:** 3 ("Entropy is the key to sufficient randomness and unpatterned results") and 4 ("Sufficiently random")

**Weakness.**
- **Sufficient for what?** A Lo-Res dice game, a card shuffle someone might count, a psych-lab stimulus schedule (the Behavior Research Methods papers on slide 8 came from exactly this use), Monte Carlo, or cryptography? Each needs something completely different, and the deck never picks one.
- **Slide 3 is technically wrong as worded.** Entropy in the *seed* makes the *starting point* unpredictable. It does nothing about "unpatterned results," which are a property of the *generator*: period, lattice structure, correlation between successive outputs. A perfectly random seed fed into Integer BASIC's 15-bit LFSR still gives outputs that are linear over GF(2). A perfectly random seed fed into Applesoft still enters the short loops *AAL* 1984 measured. Anyone in the room who has read Knuth Vol. 2 will say so.
- Slide 4 calls Integer BASIC "Sufficiently random" *and* "Known period with limited range" but gives no period or range. The period is 32,767 per the team's own emulator. The range is `0..n-1` for `n` ≤ 32,767.

**Hostile questions:**
> "Define 'sufficiently random.' Sufficient for a game of Hammurabi, or sufficient to pass a chi-square test? Which test did Integer BASIC pass?"

> "A random seed doesn't give unpatterned output. Your slide 3 confuses seeding with generator quality. Which one is the talk actually about?"

**What the presenter must change:**
- Rewrite slide 3's last line to separate the two ideas, for example: "A PRNG needs two things: an unpredictable *seed* (entropy) and a generator whose output has no visible *pattern*. This talk is about the first."
- Replace "Sufficiently random" with a concrete, defensible claim: "Period 32,767. Good enough that a player can't see a repeat in a game session. Useless for statistics." Put the numbers on the slide.
- State the use case once, early, and judge both BASICs against it.

---

## 7. EMBARRASSING: slide 6's plain-English description of the code is wrong in details this room will read off the listing on the same slide.

**Slide:** 6 (text, plus embedded image `image6.png` of `$EFAE-$EFE7`)

1. **"multiplies, adds"**: the add does nothing. `CON_RND_2` has exponent `$68`, and the comment in the listing on this very slide says "<<< this does nothing, due to small exponent >>>". The team even has a `nofadd` experiment in `rnd_experiments.py` to test it. *Hostile:* "Your own screenshot says the add does nothing. Which is it?"
2. **The multiplier constants are truncated.** `CON_RND_1` and `CON_RND_2` are 4 bytes each, but `FMULT`/`FADD` read 5-byte packed values. The multiplier's last mantissa byte is actually the first byte of `CON_RND_2` (`$68`). This is one of the most-cited bugs in the routine, and the slide skips it.
3. **"swaps two bytes around"**: which two? The code swaps `FAC+1` and `FAC+4` (`$EFCC-$EFD2`), the most and least significant mantissa bytes. *AAL* May 1984 describes it as "reversing the middle two bytes," which is wrong. If the presenter repeats the AAL wording from memory, the listing on their own slide contradicts them.
4. **The comments aren't Microsoft's.** "very poor RND algorithm," "to supposedly make it more random" and "this does nothing" are **Sander-Cederlof's DocuMentor annotations**, carried into McFadden's SourceGen listing. The image has no attribution. If the audience thinks Microsoft's source said "very poor RND algorithm," the presenter will be corrected publicly. Credit it: "Disassembly: S-C DocuMentor (Sander-Cederlof), via 6502disassembly.com (McFadden)."
5. The `.eq`/label names (`LOAD_FAC_FROM_YA`, `STORE_FAC_AT_YX_ROUNDED`) are McFadden's naming, not the original Microsoft labels. That's minor, but credit it along with item 4.

---

## 8. EMBARRASSING: dates and product names on slides 4, 6 and 7

- **Slide 6, "Applesoft, 1978," shows `$EFAE`.** That address is *Applesoft II in ROM*. Per the listing header, the image is from the Apple ][+, which shipped in 1979. Applesoft in 1977–78 existed as RAM-loaded versions (the original Applesoft, then Applesoft II from tape or disk, and the Applesoft firmware card) at different addresses. *Hostile:* "In 1978 Applesoft didn't live at `$EFAE`. Does the tape version have the same off-by-one and the same cold-boot number?" **Fix:** say "Applesoft II, ][+ ROM (1979)," or establish that the RAM versions share the bug.
- **Slide 7, "Applesoft Manual, 1978."** Which edition and part number? The scan's typography (slashed zeros, `\aexpr\`) should be matched to a specific printing. Revisions exist, and someone may own a different one.
- **Slide 4** cites "Sander-Cederlof, Apple Assembly Line, August 1981." I verified that it exists ("Random Number Generator from Integer BASIC"). Note that the article calls `$EF51`, *inside* RND after `GET16BIT`, not `$EF4E`. That's consistent, but be ready to explain the 3-byte difference if someone checks.
- **Slides 4–5 attribution.** "Woz wrote a generator at `$EF4E`" (slide 4) is fine. The Integer BASIC disassembly in `image2.png` on slide 5 is Paul Santa-Maria's. Credit it the same way as slide 6.

---

## 9. EMBARRASSING: slide 5, "Present in some form in all Apple II ROMs"

**Weakness.** The slide shows KEYIN/GETKEY on the original F8 ROM (`$FD1B`), the Autostart F8 (`$FD1B`), the unenhanced //e 80-column firmware (`$CC71`, and also `$C2D5` `IK2A`, which the slide doesn't show) and the //c (`$CB15`). "All" also covers the IIc Plus and the **IIgs**, and nothing on the slide covers those.

It also matters *when* the counter runs. It advances only in the keyboard-wait loop that belongs to whichever input routine is active. Programs that poll `$C000` directly, and custom `KSW` input hooks that don't chain to KEYIN, never advance it.

**Hostile question:** "All? The IIgs? And does the counter move while my game polls `$C000`, which is how every action game reads the keyboard?"

**Fix:** say "all 8-bit Apple II monitor and 80-column firmware ROMs shown here," and add the qualifier "only while a KEYIN-based routine waits for a key."

The //e 80-column firmware at `$CC71` also does more than `INC`: it goes on to `LDA RNDH / INC RNDH / EOR RNDH`. Be ready to say what that extra code is for (probably cursor-blink timing) and whether it changes the loop rate. Don't guess on stage.

**Rate claims to have ready.** The team's emulator assumes 15 CPU cycles per KEYIN loop, which gives about 68,000 increments per second and a full 16-bit wrap roughly every 0.96 s on a ][+. That's a good number to put on a slide, because it's *why* human timing looks uniform. But it's specific to the tight F8 loop. The //e and //c firmware loops are longer, so measure those before quoting any figure for them.

---

## 10. MINOR: slide 8 source-list details a pedant will check

- **"Kaner & Vokey, 1982 — First published account."** A priority claim is a challenge to the audience. Give the full citation (journal, volume, pages) and soften it to "earliest account I've found," unless the presenter has done a priority search.
- **"Aldridge 1987, Gleason 1988 — Behavior Research Methods. ERIC EJ372427."** That's two papers and one ERIC number. Give each its own citation.
- **"Empson, GS WorldView 1999 — Built Moore's LFSR for the Apple II."** What is "Moore's LFSR"? And why is a IIgs-era publication the source for an 8-bit BASIC fix? Clarify or cut.
- **Call-A.P.P.L.E. Jan 1983, "RND is Fatally Flawed"**: confirmed by *AAL* May 1984, which cites it as pages 29–34. Add the page numbers.
- **A structural gap:** the deck lists the 1983–84 fixes (the Call-A.P.P.L.E. `USR` routine, the S-C routines) but doesn't say how the patch differs from or improves on them. Someone will ask "how is yours better than the 1984 one?"

---

## 11. MINOR: deck hygiene the room will notice

- The on-slide page labels are wrong. Slide 2 reads "1", slide 3 "2", slide 4 "3", slide 5 "4", slides 6 **and** 7 both read "5", slide 8 reads "7", slide 9 reads "9", and slide 10 has no number. That's a duplicate plus gaps at 6 and 8. It reads as though slides were deleted.
- Slide 9's final line is labeled "1." and there's no "2." The title says "Two Part Solution" but never names the two parts. Is it `LC_Loader.bin` and `Patch_lc.bin`, or something else? Label them.
- The image on slide 6 carries the alt-text `/home/claude/rnd_listing.png`, a build path. Screen-reader users and anyone who opens the `.pptx` will see it. Replace it with a real description and credit.
- The speaker notes are empty. For this audience, the presenter needs backup notes on every slide listed in findings 1–5.

---

## Priority order for fixes

1. **Finding 1:** re-test `.973136996` on real hardware, rewrite the thesis around the off-by-one, and add the `$CD` table.
2. **Finding 2:** put the patch listing on a slide and show the stock-vs-patched behavior tests.
3. **Finding 3:** add the compatibility matrix and loader refusal logic, or switch to a `USR`/`&` hook. At minimum, add "not for ProDOS" to slide 10.
4. **Finding 4:** state the patch length (≤ 53 bytes, `$F600` intact), cite S-C for HFIND, search for external callers, and add a hi-res regression test.
5. **Finding 5:** reframe as "regression of the default, not the capability," add the side-by-side and PEEK-idiom slides, and measure the LCG cycles for counter seeds.
6. **Finding 6:** define "sufficient" and fix slide 3's conflation of seed entropy with output quality.
7. **Findings 7–11:** correct slide 6's description, fix dates and attributions, qualify "all ROMs," complete citations, and clean up the deck.

## Open items this review couldn't resolve (the presenter needs answers)

- What `$CD` holds at first `RND` on real ][+, //e, //c and IIgs hardware, under each boot path.
- The contents and length of `Patch_lc.bin` and `LC_Loader.bin` (not in the workspace).
- Whether HFIND/`$F5CB` appears as a published entry point in period documentation, and whether known software calls it.
- Whether the //c (all ROM revisions) and IIgs Applesoft are byte-identical at `$EFAE`, `$F123`, `$F150` and `$F5CB-$F600`.
- The RESET behavior of the ][+ Language Card and common third-party RAM cards.
- The cycle structure of the stock Applesoft LCG for seeds of the form `RND(-(0..65535))`. Run `rnd_experiments.py classify` for this.
- How widely `RND(-PEEK(78)-256*PEEK(79))` was published before 1984.
