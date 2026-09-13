# Edits to Jeff Robison's deck

**Original:** `00_Original_Deck/Applesoft_Loaded_Dice_Deck_1.pptx` (untouched)
**Edited:** `01_Edited_Deck/Applesoft_Loaded_Dice_Deck_1_EDITED.pptx`
**Rebuild:** `_build/edit_original_deck.py`

These are recommendations for the presenter. Every change keeps Jeff's layout, fonts and colours, and all ten slides stay in their original order. Slide numbers below are file order (1–10), and the badge shown on screen is in brackets.

Evidence labels: **[DOC]** primary source · **[EMU]** measured by running the real ROM code · **[INF]** inference to verify.

---

## Slide 1 [0] — Title
- **Notes rewritten.** The demo is now a **power-cycle** (switch off, then on). The old note said "reboot". Ctrl-RESET and PR#6 leave the fifth seed byte alone, so the number changes and the demo fails. [DOC Aldridge 1987; EMU]
- Notes add that Applesoft is Microsoft's BASIC, which sets up slide 6.

## Slide 2 [1] — The Problem
- **Added** in green: "Rerun the program: different numbers. Power-cycle: the same ones again." This is why the bug hid for years. [DOC Aldridge]
- **Added** Aldridge's sentence as the on-screen source: "exactly the same sequence each time the machine is powered on." [DOC]
- **Notes replaced.** The old notes were a byte-identical copy of slide 3's. The new notes prepare the answer to "my machine prints a different number."

## Slide 3 [2] — What a random number generator is
- Title changed to **"Pseudo-random means repeatable"**.
- Amber line: "Entropy is the key to sufficient randomness and unpatterned results." → **"Same starting number → same 'random' numbers. Entropy only picks the start."** The original mixed up seed entropy with output quality, and "sufficient" was never defined.
- Notes trimmed to 30 seconds. They keep the "amber line" cue, which belongs to this slide.

## Slide 4 [3] — Integer BASIC, 1977
| Before | After | Evidence |
|---|---|---|
| Known period with limited range | 15-bit shift register: repeats every 32,767 calls | [EMU] `tools/intbasic_rnd_emu.py`: taps = bit 14 XOR bit 13, and every start state tested has period 32,767 |
| No Floating point | RND(n) returns the register MOD n (integers only) | [DOC] `JMP MOD` at `$EF7D` |
| Sufficiently random | Plenty for games. Not for statistics. | [DOC] Woz: "intended primarily for games" (Byte, May 1977) |
| Built-in Seed | Seeded by your keypress timing | |
| …Integer BASIC reads it. | …Integer BASIC's generator *is* that counter: RND reads it, scrambles it, writes it back. | [DOC] `ROL MON_RNDL/RNDH` in slide 5's own image |
| Sander-Cederlof, AAL, Aug 1981. | + "Integer BASIC disassembly: Paul Santa-Maria, via Andy McFadden" | credit |

The notes add the "56 bytes" line and concede Integer BASIC's weaknesses before anyone in the audience raises them.

## Slide 5 [4] — Built-in Entropy Source
- "Present in some form in all Apple II ROMs" → **"Same counter in the II, II+, IIe and IIc ROMs shown"**. The IIgs and later IIc ROMs weren't checked, and "all" invites that question.
- Notes: "tens of thousands of times" → **about 68,000 counts a second, wrapping about once a second**. [INF, from 15 cycles per loop at 1.0205 MHz; Aldridge says "less than a second"]
- Notes add that the counter only moves while KEYIN waits, the Wozniak/Baum monitor credit, and a cue to walk only the left column.

## Slide 6 [5] — Applesoft, 1978
- Title → **"Applesoft II: Microsoft's RND"**. The listing at `$EFAE` is the ][+ ROM (1979), so the new title drops the year. Naming Microsoft keeps the audience from reading this as Woz's regression. [DOC Microsoft BASIC-M6502 source]
- The empty subtitle box now reads "Microsoft wrote this generator. Apple licensed it and shipped it unchanged in ROM."
- Red header → "Seed: $C9, filled from ROM". The body → **"$4E/$4F still counts. Applesoft never reads it."** This is the thesis, and the original stated it as an aside.
- "What it does": "adds" → "adds (lost to precision)". "Swaps two bytes around" → "swaps the high and low mantissa bytes". Added "Nothing else touches $C9." [DOC listing; EMU: the add changed 5 of 57,021 steps]
- **Added a caption** crediting the listing and comments to Sander-Cederlof via McFadden, noting that the comments are his and not Microsoft's.
- **Image alt text** changed from the build path `/home/claude/rnd_listing.png` to a real description.
- **Notes:** "Twenty-six instructions" → **twenty-eight** (`$EFAE–$EFE7`). Added the Commodore-build contrast and "say nobody connected it, not nobody knew."

## Slide 7 [5 → 6] — Applesoft Manual
- **Badge fixed: 5 → 6.**
- **Added** under the `.973136996` screenshot: "…starting here, every power-on."
- **Added caption panel:** "Repeatable on purpose: documented. Repeatable by accident: not."
- **Notes replaced.** The old notes were a byte-identical copy of slide 6's.

## Slide 8 [7] — Sources → "Found. Published. Worked around."
| Before | After | Why |
|---|---|---|
| Kaner & Vokey, 1982 — First published account. Dr. Kaner sent me the paper directly. | Kaner & Vokey (1982; MICRO, 1984) — RND fell into an endless loop of 202 numbers. | The paper was published June 1984, after Call-A.P.P.L.E. (Jan 1983), so "first published" is wrong. The notes cited a "202 figure" that appeared nowhere. [DOC] |
| Call A.P.P.L.E., Jan 1983 | + pp. 29–34 | [DOC via AAL May 1984] |
| Sander-Cederlof — Found the startup bug. The seed copy is off by one. | Seed copy is off by one ($F151: $1C→$1D). Repeats at number 37,758. | Specific enough for this audience [DOC] |
| Aldridge 1987, Gleason 1988 — Behavior Research Methods. ERIC EJ372427. | Split into two rows. Aldridge, BRMIC 19(4), 1987: "Each day's first subject got the same 'random' word list." Gleason, Collegiate Microcomputer, 1988: "…published suggested seeds. ERIC EJ372427." | The original merged two papers. EJ372427 is Gleason's. Aldridge is the stakes story. [DOC] |
| Empson — Built Moore's LFSR for the Apple II. | Wrote up R. C. Moore's 1989 shift-register RNG, seeded from $4E/$4F. | Empson wrote up Moore's generator; he didn't build it. [DOC GS WorldView, Nov 1999] |

The notes lead with the harm (Aldridge's memory experiment) and tie 202 and 37,758 to one generator with different uncopied bytes.

## Slide 9 [9 → 8] — Two Part Solution → "The Fix: Put the Counter Back"
- **Badge fixed: 9 → 8.**
- The labels now read **"Part 1 · LC_Loader.bin"** and **"Part 2 · Patch_lc.bin"**, so the title's "two parts" are named.
- "(may impact HFIND, supposedly unused by AppleSoft.)" → **"over HFIND, which no Applesoft routine calls."** S-C DocuMentor says "not called by any Applesoft routine". My ROM scan found no `JSR`/`JMP $F5CB` anywhere in `$D000–$FFFF`. [DOC + checked]
- The dangling "1." item → two lines: the behavior line, then **"Fixes the seed, not the generator. Needs a language card."**
- **Added panel "Just seed it first."** It puts the rebuttal on screen, citing Apple's own advice to Aldridge's lab.
- **Added panel "Patch budget":** HFIND spans `$F5CB–$F5FF` (53 bytes), and `$F600` is an RTS that HLIN branches to (`$F59C`). [checked on the ][+ ROM image]
- The notes add a pre-show confirmation checklist (below).

## Slide 10 [none → 9] — Try it yourself
- **Badge added: 9**, to match the title slide.
- **Added the three takeaway lines** above the byline.
- **Added an amber placeholder** for the link text and QR code. **Nothing was on this slide before, and the link wasn't supplied, so none was invented.**
- **Notes:** corrected the Commodore answer. The timer-seeded `RND(0)` and `TI` were written by Microsoft for the Commodore build in 1977; they aren't Commodore's own addition. Also added the "and Now" parallel (Debian OpenSSL, CVE-2008-0166) and two more expected questions.

## Metadata
- Document title "PptxGenJS Presentation" → "Applesoft's Loaded Dice (edited)".

---

## Not changed: needs Jeff

**Must confirm before the show**
1. **What the patch does on positive `RND`.** Does it reseed on every call, once, or when the counter changes? `Patch_lc.bin` and `LC_Loader.bin` aren't in the files we have, so the slide 9 behavior line repeats Jeff's claim without verifying it. A tight loop with no keypress must not return near-identical values.
2. **Patch length ≤ 53 bytes**, and HPLOT TO / DRAW / XDRAW still work after install.
3. **The demo machine's number.** Power-cycle it three times and confirm it repeats. See `03_Collateral/HARDWARE_TEST_PLAN.md`.
4. **Link and QR** for slide 10.
5. **Manual edition** for the slide 7 scans. The title says 1978, but printings differ. Confirm the part number before citing a year.

**Recommended, not applied** (these are structural choices for the presenter)
- Show slide 7 (manual) **before** slide 6 (code): the promise, then the reality. Swap the badges if you do.
- Re-crop `image4` on slide 5 (IIc `$CC71`) so the `INC RNDH` row isn't cut off.
- Crop the RND(−n) manual scan to its two key sentences. People past row 3 can't read seven lines.
- Add a 90-second closing demo that proves the fix: power on, load, `PRINT RND(1)`, power-cycle, repeat, different number.
- Swap the badges for PowerPoint slide-number fields so reordering can't break them again.
