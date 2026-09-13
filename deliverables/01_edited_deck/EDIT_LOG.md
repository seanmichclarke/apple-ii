# Edit log: *Applesoft's Loaded Dice* (edited copy)

**For:** Jeff Robison. Every change here is a proposal, and the call on each one is Jeff's.

| | |
|---|---|
| **Original, untouched** | `deck/Applesoft_Loaded_Dice_Deck_1.pptx` (revision 2) |
| **Edited copy** | `01_edited_deck/Applesoft_Loaded_Dice_Deck_1_EDITED.pptx` |
| **Rebuild** | `.venv/bin/python deliverables/_build/edit_jeff_deck.py` |

**Scope.** Only mechanical fixes, factual corrections, and the smallest wording changes that remove
a heckle. Layout, colors, fonts, images and slide order are Jeff's. Structural recommendations,
such as swapping the manual and code slides or adding a proof demo, are applied in the new deck
(`02_new_deck/`) instead, so the two can be compared.

**Labels.** Each change is tagged with its kind:

- **[MECH]** mechanical defect
- **[FACT]** factual or citation error
- **[WORD]** wording that invites a correct heckle
- **[ADD]** missing content the notes already call for

**Slide numbers** below are file order (1–10). The badge numbers on the slides now run 0–9.

---

## Deck-wide

| Change | Kind | Why |
|---|---|---|
| Badge numbers: slide 7 `5`→`6`, slide 9 `9`→`8`, slide 10 gets `9` | MECH | The badges read 0,1,2,3,4,5,5,7,9 and none. That's two 5s, and 6 and 8 are missing. |
| Speaker notes rewritten on all 10 slides | MECH + FACT | Notes 2 and 3 were identical, and so were notes 6 and 7. Slide 7 had no notes of its own. "Twenty-six instructions" is wrong: `$EFAE–$EFE7` is 28. |
| File title: "PptxGenJS Presentation" → "Applesoft's Loaded Dice" | MECH | Shows in PDF exports and file browsers. |

## Slide 1: Title

| Change | Kind | Why |
|---|---|---|
| Notes: "reboot" → "power-cycle", with an explanation | FACT | A warm restart (PR#6, Ctrl-Reset) leaves the fifth seed byte in RAM and prints a *different* number. The opening demo fails as written. Source: Aldridge 1987, AAL May 1984. |
| Notes: "Applesoft is Microsoft's 6502 BASIC" | ADD | Primes the slide-6 attribution. |

## Slide 2: The Problem

| Change | Kind | Why |
|---|---|---|
| On screen: Aldridge's sentence "…exactly the same sequence each time the machine is powered on", with citation | ADD | The deck's central claim had no source on screen. |
| Notes: "your machine may print a different number" answer (the `$CD` byte) | FACT | Of 256 possible `$CD` values, 181 give different first numbers. Only `$FE`/`$FF` gives `.973136996`. Re-verified on the ROM. |

## Slide 3: What a random number generator is

| Before | After | Kind |
|---|---|---|
| "Entropy is the key to sufficient randomness and unpatterned results." | "Entropy decides where the sequence starts. The formula decides what it looks like." | WORD |

**Why:** entropy in the seed makes the *starting point* unpredictable. It does nothing for "unpatterned
results", which is a property of the generator. Anyone who has read Knuth Vol. 2 will say so.
"Sufficient" was also undefined.

## Slide 4: Integer BASIC, 1977

| Before | After | Kind |
|---|---|---|
| Known period with limited range | 15-bit shift register: repeats every 32,767 calls | FACT |
| No Floating point | Integers only: RND(X) is the state MOD X | WORD |
| Sufficiently random | Good enough for games, its stated purpose | WORD |
| *(none)* | 56 bytes in all: 6 in KEYIN, 50 in RND | ADD |
| Built-in Seed | Seeded by you | WORD |
| "…Integer BASIC reads it." | "…Integer BASIC's generator is that counter: RND scrambles it and writes it back." | FACT |

**Why:**
- The period is measured and the byte counts come from the ROM addresses. See `FACT_SHEET.md`.
- "Sufficiently random" invites "sufficient for what?". Woz's own stated purpose was games (BYTE, May 1977).
- The counter *is* the generator's state (`$EF5E–$EF6F`), which is a stronger point than "reads it."

## Slide 5: Built-in Entropy Source

| Before | After | Kind |
|---|---|---|
| Present in some form in all Apple II ROMs | Same counter in the II, II Plus, IIe and IIc ROMs | WORD |
| Notes: "gone round tens of thousands of times" | ≈68,000 counts/s, wraps ≈ once a second | FACT |
| Notes: *(none)* | Credit S. Wozniak & A. Baum; tell the room to walk the left side only | ADD |

**Why:** "all" invites "what about the IIgs?", and the IIgs, enhanced IIe and later IIc ROMs weren't
checked. The rate is 15 CPU cycles per loop at 1.02 MHz.

**Not changed (Jeff's call):** the IIc crop (`image4`) cuts through the row that shows the high byte
incrementing. Re-crop `$CC70–$CC79` if you want that on screen.

## Slide 6: Applesoft, 1978

| Before | After | Kind |
|---|---|---|
| Applesoft, 1978 | Applesoft II: Microsoft's RND | FACT |
| *(empty subtitle)* | Microsoft's 6502 BASIC, licensed by Apple | ADD |
| Applesoft relies on different seed | Seed at $C9, from ROM | WORD |
| However, the seed for Integer BASIC remains. | $4E/$4F still counts. Applesoft never reads it. | WORD |
| "…multiplies, adds, swaps two bytes around…" | "…multiplies, adds a constant too small to matter, swaps the top and bottom bytes…" | FACT |
| *(no credit)* | Caption: "II Plus ROM. Comments: Bob Sander-Cederlof (S-C DocuMentor), via Andy McFadden… Code: Microsoft BASIC M6502." | FACT |
| Image alt text `/home/claude/rnd_listing.png` | Real description | MECH |

**Why:**
- `$EFAE` is the II Plus ROM (1979). The 1978 Applesoft releases loaded into RAM at other addresses.
- No slide named Microsoft.
- The listing's own comment says the add "does nothing". Running the ROM shows it changes the seed
  in 5 of 57,021 steps, which is "effectively nothing".
- The comments in the screenshot ("very poor RND algorithm") are Sander-Cederlof's, not Microsoft's.
  Unlabelled, they read as the ROM's own confession.
- The thesis line ("never reads it") was phrased as an aside.

## Slide 7: Applesoft Manual, 1978

| Change | Kind | Why |
|---|---|---|
| Title → "The Applesoft Manual" | FACT | Which printing the scans come from isn't established (open item B1). "1978" is plausible but unverified. |
| Label under the `.973136996` screenshot: "…starting here, every power-on." | ADD | The slide never said what to look at. |
| Panel: "Repeatable on purpose: documented. / Repeatable by accident: not." | ADD | That is the slide's whole point. |
| New notes of its own | MECH | Slide 7 had slide 6's notes. |

**Not changed (Jeff's call):** crop the `RND(-n)` scan to the two sentences that matter (it's 7 lines
of typewriter text). Consider swapping slides 6 and 7 so the promise comes before the reality. The
new deck does this.

## Slide 8: Sources

| Before | After | Kind |
|---|---|---|
| Sources | Found, reported, worked around | WORD |
| Kaner & Vokey, 1982 / "First published account. Dr. Kaner sent me the paper directly." | Kaner & Vokey, MICRO 1984 / "Written 1982. RND fell into an endless loop of 202 numbers." | FACT |
| Call A.P.P.L.E., Jan 1983 / "RND is Fatally Flawed." | Call-A.P.P.L.E., Jan 1983 / "…Flawed," pp. 29–34. | FACT |
| Sander-Cederlof, AAL May 1984 / "Found the startup bug. The seed copy is off by one." | "Seed setup copies 4 of 5 bytes (fix: $F151 $1C→$1D). Repetition starts at the 37,758th number." | FACT |
| Aldridge 1987, Gleason 1988 / "Behavior Research Methods. ERIC EJ372427." | Aldridge, BRMIC 1987 / "A memory experiment gave each day's first subject the same "random" word list." | FACT |
| *(merged into the row above)* | Gleason, 1988 / "Collegiate Microcomputer. Tested Apple IIe RND; suggested seeds that pass." | FACT |
| Empson, GS WorldView 1999 / "Built Moore's LFSR for the Apple II." | "Write-up of Robert Moore's 1989 shift-register generator, seeded from $4E/$4F." | FACT |

**Why:**
- The notes cite "the 202 figure", but it wasn't on the slide.
- Kaner & Vokey were published in 1984, after Call-A.P.P.L.E.'s January 1983 article, so they weren't "first published".
- EJ372427 is Gleason's paper, in *Collegiate Microcomputer*, not *Behavior Research Methods*.
- Aldridge's memory experiment is the deck's best evidence of real damage, and it was hidden inside a citation.
- The personal line about Kaner moves to the notes, to be said aloud.

## Slide 9: Two Part Solution

| Before | After | Kind |
|---|---|---|
| Two Part Solution | The Fix: Put the Counter Back | WORD |
| "Writes the patch code into the LC at $F5CB. (may impact HFIND, supposedly unused by AppleSoft.)" | "Writes the patch code into the LC at $F5CB, over HFIND (53 bytes), which no Applesoft routine calls." | FACT |
| "1. Preserves negative and zero RND() functionality while relying on the KEYIN counter present in the ROM." | "Keeps RND(−n) and RND(0) working as documented; positive arguments draw on the KEYIN counter." + "Fixes the seed, not the generator. Needs a language card." | WORD + ADD |
| Notes | HFIND facts, the 53-byte limit, the questions to expect, and the limits to state | ADD |

**Why:**
- "Supposedly" was self-inflicted. The S-C DocuMentor says "not called by any Applesoft routine", and
  a byte search of the II Plus ROM finds no `JSR` or `JMP` to `$F5CB`.
- The list was numbered "1." with no "2.".
- The scope line answers "does it fix the 202 loop?" before anyone asks.

> ⚠️ **The 53-byte limit.** `$F600` is an `RTS` that HLIN reaches from `BEQ` at `$F59C`. A patch longer
> than 53 bytes breaks `HPLOT … TO`. Jeff needs to confirm the patch size (open item A3).
>
> ⚠️ **"Positive arguments draw on the KEYIN counter"** is Jeff's own claim, restated. What the patch
> actually does on repeated calls is unverified (open item A2).

## Slide 10: Try it yourself

| Change | Kind | Why |
|---|---|---|
| Three takeaway lines above the title | ADD | The talk never states its goals. |
| `[ URL: Jeff to supply ]` in amber, plus a dashed QR placeholder | ADD | The notes say "Link and QR", but the slide had neither. The URL is also needed as text for people in the back rows and for the PDF. |
| Badge `9` | MECH | Matches the title slide's `0`. |
| Notes: Commodore answer corrected | FACT | The timer-seeded `RND(0)` and `TI` were written into *Microsoft's* source for Commodore and shipped in the first PET ROM in 1977. Crediting "Commodore wired it" alone will be corrected from the floor. |

---

## Deliberately not changed

- **Subtitle "Then and Now".** The deck still doesn't deliver a "Now". Either add the "Now" slide from
  the new deck or cut it from the subtitle (open item B7).
- **Slide order.** Unchanged.
- **Slide 5 walking all five listings.** Only the notes now suggest summarizing the right column.
- **Images and crops.** Unchanged.
