# Review B: Narrative and Completeness

**Deck:** *Applesoft's Loaded Dice: The Truth About Randomness on the Apple II, Then and Now*, Jeff Robison, VCF Midwest 21 (2026), 10 slides (`deck/Applesoft_Loaded_Dice_Deck_1.pptx`)
**Reviewer:** B (narrative and completeness)
**Date:** 2026-09-12

**Scope.** I reviewed the deck at its real length (10 slides, live cold-boot demo, QR close). I used `slides/OUTLINE.md` only as a checklist and did not try to push the deck toward 32 slides.

**Evidence labels:**
- **[DOC]** documented in a primary source, quoted or cited
- **[EMU]** measured by emulating the real ROM code (`research/tools/rnd_experiments.py`, `woz/intbasic_rnd_emu.py`; raw results copied to `review/evidence/`)
- **[INF]** plausible inference that the presenter should verify

**What I checked.** I read all 10 slides and their notes, the relationship files, and every embedded image. I also checked `presentation.xml` (the slide order matches the file numbers and no slides are hidden). Outside sources:
- McFadden's Applesoft disassembly (6502disassembly.com/a2-rom/Applesoft.html)
- Aldridge 1987 (*BRMIC* 19(4):397–399)
- Kaner and Vokey (MICRO, June 1984)
- Sander-Cederlof, *Apple Assembly Line* (AAL), May 1984
- The ERIC record for EJ372427

---

## 0. Two findings that outrank everything below

### 0.1 The opening demo can fail as written

Slide 1's note says: *"boot the machine cold, PRINT RND(1), **reboot**, same number."*

Aldridge (1987) is explicit **[DOC]**:

> "The function thus appears to be generating a new sequence every time a program is rerun, **even if the machine has been rebooted**. It is only when a machine is **powered off and back on** that the sequence begins repeating itself."

The mechanism **[DOC + EMU]**:
- `COLD_START` copies only 4 of the 5 seed bytes into `$C9–$CD`. The disassembly at `$F123` says *"<<< the last byte is not copied >>>"*. AAL May 1984 gives the fix: change `$F151` from `$1C` to `$1D`.
- `$CD` therefore keeps whatever it held before. After a PR#6 or Ctrl-Reset reboot it holds the last RND state, so the first number comes out different.

**Fix:**
- In the note, change "reboot" to **"power-cycle: power switch, wait, power on."**
- Rehearse the demo on the exact machine you will use at the show.

### 0.2 The headline number depends on one byte that is never set

Running the real Applesoft RND code with different power-on values in `$CD` gives **[EMU]**:

| `$CD` at power-on | First `RND(1)` | Where the sequence ends up |
|---|---|---|
| `$FF` | **.973136996** | 37,758-number cycle, entered after 6,818 calls |
| `$00` | .270011996 | 37,758-number cycle, entered after 19,263 calls |
| `$58` (the value ROM *meant* to copy) | .512199496 | **202-number cycle**, entered after 15,382 calls |
| `$7A` | .605949496 | 202-number cycle, entered after 12,155 calls |

What this means:
- `.973136996` is what you get when `$CD` powers up as `$FF`. That the RAM powers up the same way on a given machine is **[INF]**. Someone in this room *will* power up their own IIe at the swap meet and get a different number.
- The **fact** you can defend is Aldridge's: *"exactly the same sequence each time the machine is powered on."*
- Bonus: this table ties together the deck's two published numbers. Sander-Cederlof's 37,758 and Kaner and Vokey's 202 are the same generator, starting from different values of the uncopied byte.

**Fix:**
- Put Aldridge's sentence on slide 2 as the on-screen source for the claim.
- Add this line to the slide 2 notes: *"Your machine may show a different number. It'll still be the same one every power-on. One seed byte is never initialized: Sander-Cederlof, AAL, May 1984."*
- Your own slide 8 already cites that AAL article. Don't let someone in Q&A connect it to slide 2 before you do.

---

## 1. Mechanical defects, with exact fixes

### 1.1 On-slide numbering: confirmed broken

The badge in the top-right corner is hard-coded text (`Text 1` inside `Shape 0`), not a slide-number field.

| Slide | Shows | Should show (zero-indexed, matching the "0" on the title) |
|---|---|---|
| 1 | 0 | 0 |
| 2 | 1 | 1 |
| 3 | 2 | 2 |
| 4 | 3 | 3 |
| 5 | 4 | 4 |
| 6 | 5 | 5 |
| **7** | **5** | **6** |
| 8 | 7 | 7 |
| **9** | **9** | **8** |
| **10** | *(no badge)* | **9**, or no badge on purpose. Either is fine; just match the title slide's treatment. |

**Quick fix:** slide 7 `5` → `6`; slide 9 `9` → `8`.

**Durable fix:**
- Set `firstSlideNum="0"` on `<p:presentation>`.
- Replace each badge's text with an `<a:fld type="slidenum">` field.

That way, reordering slides (see §3) can't break the numbers again.

### 1.2 Speaker notes duplicated: confirmed, with one correction to the brief

- **Slides 2 and 3** have identical notes. The brief says slide 3 has the wrong note. It's the other way round: the note (*"The amber box is the part that has to land. Slide 4 depends on it."*) belongs to **slide 3**. That's where the only amber (`#E0A73E`) element in the deck is. **Slide 2 is the one that got the copy.**
- **Slides 6 and 7** have identical notes. This note belongs to **slide 6**, the `$EFAE` listing. **Slide 7 got the copy.**
- **Also wrong in that note:** *"Twenty-six instructions."* The listing on slide 6 runs from `$EFAE` to `$EFE7`. That's **28** instructions, and all 28 run on the `RND(1)` path.

Corrected notes:

**Slide 2 (replace):**
> This is the number they just watched three times. Don't explain it yet. "Hold onto that number. By slide 5 you'll know exactly where it lives."
> If anyone says their machine gives a different number: one seed byte is never initialized (AAL, May 1984), so the exact value varies by machine. It's still the same every power-on.
> Aldridge, 1987: "exactly the same sequence each time the machine is powered on."

**Slide 3 (keep, trim):**
> Thirty seconds. This room knows what a PRNG is. The only line that matters is the amber one: same starting number, same numbers. The Integer BASIC slide depends on it.

**Slide 6 (keep, fix count):**
> This is the whole thing. **Twenty-eight** instructions.
> Point at the top: the seed comes from `$C9`, which got a fixed value out of ROM at boot. Point at the bottom: the answer goes back to `$C9`. Nothing else feeds it.
> Read McFadden's own comments aloud: "very poor RND algorithm", "this does nothing, due to small exponent". The disassembler editorializes for you.
> Source: McFadden's disassembly, 6502disassembly.com.

**Slide 7 (new):**
> Read the RND(n) line aloud: "generates a new random number each time it is used." True. It just never tells you that sequence starts in the same place every power-on.
> RND(-n): Apple *documents* repeatability as a feature, for debugging.
> The manual tells you how to get the same sequence on purpose. It never tells you you're getting it by accident. Aldridge's word for this, in 1987: "undocumented."
> When his lab called Apple, the fix Apple gave them was `X = RND(-1*(PEEK(78)+256*PEEK(79)))`. Hold that for the fix slide.

### 1.3 Slide 8 note: "The 202 figure" has nothing on screen to point at. Confirmed.

The figure comes from Kaner and Vokey **[DOC]**:

> "between the 10,000th and the 20,000th number generated, RND fell into an endless loop, repeating itself every 202 numbers … the application of the name RND to a generator of period 202."

**Fix:** under the Kaner and Vokey entry, replace

> "First published account. Dr. Kaner sent me the paper directly."

with

> "RND fell into a loop of 202 numbers."

Say the personal line out loud; don't spend screen space on it.

Also fix the note, which leans on Commodore for no reason:

> "The 202 figure is measured, from the paper, on real Applesoft. Better than any secondhand claim about Commodore."

→

> "202 is measured, on real Applesoft, by two psychologists who needed randomized experiments. Sander-Cederlof got 37,758 on his machine two years later. Same generator, different uncopied byte."

### 1.4 Slide 8 citation errors (found while checking 1.3)

- **"Kaner & Vokey, 1982 / First published account."** The paper's own header reads *"Copyright © 1982 … Published in MICRO, June 1984."* Call-A.P.P.L.E.'s "RND is Fatally Flawed" appeared in January 1983, so on the evidence in hand, Kaner and Vokey was **not** the first *published* account. → **"Kaner & Vokey: written 1982, MICRO June 1984"**, and drop "first published". Keep "first" only if you have a publication from 1982.
- **"Aldridge 1987, Gleason 1988 / Behavior Research Methods. ERIC EJ372427."** This merges two papers into one citation. EJ372427 is **Gleason, *Collegiate Microcomputer* 6(2), May 1988**. Aldridge is **BRMIC 19(4), 1987**. → Split into two lines: "Aldridge, *Behavior Research Methods*, 1987" and "Gleason, *Collegiate Microcomputer*, 1988".
- **"Found the startup bug. The seed copy is off by one."** Accurate, but vague for this room. → **"Seed init copies 4 of 5 bytes. Fix: `$F151` `$1C`→`$1D`."** [DOC, AAL May 1984]

### 1.5 Slide 10 has no link and no QR code

The notes say *"Link and QR. Nothing else."* The slide XML has only three elements: "Try it yourself", a thin green rule, and the byline. The slide's relationship file points only to the notes and the layout, and neither the layout nor the master has images.

**Fix:**
- Add the QR image.
- Also add the URL **as text**. The back rows can't scan a QR from 40 m, and the PDF version of the slides needs a link people can click.

### 1.6 Slide 7 is not "three bare tokens," but it still fails

The brief's item (d) needs a correction. The text extraction shows only `RND(n)`, `RND(-n)`, `RND(0)`, but the slide also carries **four scanned excerpts from the manual** (image7–10) and the **.973136996 screenshot** (image11), placed to the right of `RND(n)`. The pieces are there; the slide just doesn't tell anyone what to look at. The RND(-n) scan is seven lines of typewriter text that no one past row 3 can read.

**What slide 7 must say:**
1. **Highlight** "generates a new random number each time it is used" in the RND(n) scan. Put the .973136996 screenshot next to it with the label **"…starting here, every power-on."**
2. **Crop** the RND(-n) scan to the two sentences that matter: "generates the same random number each time it is used with the same \aexpr\" and "initialize (or 'seed') a repeatable sequence."
3. **Add a caption line at the bottom** (this is the slide's whole point):
   > **Repeatable on purpose: documented. Repeatable by accident: not.**
4. RND(0) can stay as a scan with no highlight. It's context, not argument.

### 1.7 Slide 5: one crop hides the evidence

`image4` (IIc ROM, `$CC71 inc RNDL`) is cropped through the middle of the rows above and below. The line that shows the high byte being bumped is cut off, which is the proof that this is a 16-bit counter. **Re-crop to show `$CC70`–`$CC79` whole.**

### 1.8 Slide 9: "may impact HFIND, supposedly unused by AppleSoft"

The disassembly settles this **[DOC]**: `* HFIND - calculates current position of hi-res cursor` / `* (not called by any Applesoft routine)`, at `$F5CB`.

"Supposedly" invites the exact heckle you don't want. → **"Overwrites HFIND (`$F5CB`), which Applesoft never calls (McFadden disassembly)."** Keep one sentence in the notes about the remaining risk: a third-party program that does `CALL 62923` directly **[INF]**.

### 1.9 Slide 9: list numbered "1." with no "2."

The only numbered item, *"1. Preserves negative and zero RND() functionality…"*, sits under the `Patch_lc.bin` label with no second item. "Two Part Solution" means two binaries, but the numbering suggests two properties. Either add a "2." (see §2.4) or remove the number.

---

## 2. Missing content, ranked by importance

### 2.1 The stakes. Rank 1: the problem statement is missing its "so what"

The audience sees the symptom, not the damage. The deck already holds the best consequence story available, buried as a citation on slide 8. Aldridge 1987 **[DOC]**:

> "In a memory experiment, each subject was supposed to have been presented an individually randomized list of words… one particular ordering of the list seemed to be reappearing… the subjects receiving the repeated lists were those tested **at the beginning of each day, immediately after the computer had been turned on**."

Why this matters more than a game example:
- It's documented and specific.
- It's a *published scientific result* contaminated by the bug.
- Kaner and Vokey were also writing because experiments needed randomization ("Randomization of the order of events in experiments is a necessary part of the design of every experiment that we have run").
- "Which games were affected" would be **[INF]** at best unless you have a specific title with evidence. Don't ad-lib one.

**Where to put it:** lead slide 8 with it (see §4 for the retitle). Thirty seconds of speaking, and it turns the list of sources into a story about harm.

### 2.2 Why nobody noticed. Rank 2

This is the most counterintuitive fact in the talk, and it isn't in the deck. Rerunning a program, or even rebooting DOS, gives *different* numbers. Only power-on repeats **[DOC, Aldridge]**. That's why the bug survived: a programmer at their desk never sees it; the first user of the day does. It also explains the slide 9 note "the failure is silent" and gives it evidence.

**Where:** one spoken sentence on slide 2 (after the demo) or slide 7. Optional on screen: "Rerun: looks random. Power-cycle: repeats."

### 2.3 The regression, said out loud. Rank 3

The slide 4 note says *"Don't make the regression argument yet."* No slide ever makes it explicitly. Slide 6 comes closest with *"However, the seed for Integer BASIC remains."* That is the thesis, and it's phrased as an aside.

It's also stronger than the deck states. In Integer BASIC, `$4E/$4F` isn't just read as a seed; it **is** the generator's state (`rol MON_RNDL`, `rol MON_RNDH`, `sta MON_RNDH` at `$EF5E–$EF6F`). So every wait for a keypress stirs the generator itself. Applesoft's state at `$C9` is touched by nothing except RND. **[DOC, disassembly on slide 5's own image]**

**Where:** slide 6's headline (wording in §4).

### 2.4 What the patch actually does, and what it doesn't. Rank 4: the resolution is under-specified

Slide 9 describes how the loader *installs* the patch (five steps) but not what the patch *does* once it runs. The audience needs one line of behavior and one line of limits.

- **Behavior (presenter to confirm):** does positive `RND` reseed from `$4E/$4F` on every call, only on the first call, or when the counter has changed? The answer decides several Q&A questions below.
- **Limits the room will raise:**
  - **It fixes the seed, not the generator.** If §1.3 puts "202" on slide 8, someone will ask whether the patch fixes the loop. Kaner and Vokey, Call-A.P.P.L.E., Sander-Cederlof, and Empson all *replaced the generator*; this patch doesn't. Say that plainly. It's the difference between their approach and yours, not a weakness.
  - **Seeding doesn't escape the loop either [EMU].** In a 16-seed sample, some `RND(-n)` seeds fall into the 202-number cycle: `RND(-52894)` after 6,594 calls, `RND(-22258)` after 20,326. Anything seeded from the counter, including the patch and Apple's own PEEK(78) advice, can land there. This is also why Gleason (1988) published a list of recommended seeds.
  - **It needs a keypress first.** Aldridge flags this for the Apple-advised fix: fine "as long as there has been keyboard input of any kind between power-on and" the first RND. A turnkey program that calls RND before any keypress gets a much less arbitrary counter **[DOC for Apple's workaround; INF for the patch]**.
  - **It needs a language card.** That means a II+ with a 16K card; the IIe and IIc have one built in. Possible conflicts with anything else living in the language card (ProDOS itself; Integer BASIC loaded into the card on a II+) **[INF, verify]**.

**Where:** add a "2." line to slide 9 (wording in §4) and put the Q&A answers in the notes.

### 2.5 A closing demo that proves the fix. Rank 5

The talk opens with proof of the problem and closes with a QR code. The resolution has no proof. **Symmetry is the cheapest persuasion available:** power on, run `LC_Loader`, `PRINT RND(1)`, power-cycle, run it again, get a different number. That's about 90 seconds. If power-cycling on stage is risky, show a pre-recorded clip.

### 2.6 The takeaways. Rank 6: the goals are never stated

Slide 10 is "Try it yourself" plus a byline (and, per §1.5, not even the QR). The talk doesn't need a separate takeaways slide at this length, but it needs **three lines on slide 10, above the link**:

> **1977: the Apple II seeded RND from you. 1978: from ROM.**
> **It hid for years: rerun looked random; only power-on repeated.**
> **The fix puts the counter back, without changing a single program.**

(The third line assumes the patch needs no changes to programs, which is true by construction since it lives in the language card. Confirm against §2.4.)

### 2.7 "Now": the subtitle promises something the deck doesn't deliver. Rank 7

The deck has no modern beat. Nothing on the slides or in the notes connects to after 1999, except implicitly the 2026 patch. Pick one:

- **(a) Recommended: one line plus 30 seconds of speaking.** Define "now" as two things:
  1. The patch you're releasing today.
  2. The same bug shape recurring: a change silently removes the entropy input, and the output still *looks* random. The textbook modern case is the **Debian OpenSSL RNG bug, CVE-2008-0166**: a 2006 code change removed nearly all entropy mixing, and predictable keys were generated for about two years before anyone noticed **[DOC]**. Present it as a *parallel*, not a lineage. Don't claim anyone learned from, or ignored, the Apple II.
- **(b)** A lighter "now": C's `rand()` without `srand()` is specified to behave as if seeded with 1, so it produces the same sequence every run in 2026 **[DOC, ISO C]**. Fine, but less dramatic.
- **(c)** If neither fits, change the subtitle to *"…on the Apple II, Then and Today's Fix"*, or drop "Then and Now."

**Where:** the notes for slide 9 or 10, plus the takeaway lines in §2.6.

### 2.8 Microsoft attribution. Rank 8, cheap and credibility-protecting

No slide says Applesoft is Microsoft's 6502 BASIC. It shows up only in the slide 10 Q&A notes ("same Microsoft code"). In front of this crowd, a title that reads as "Woz's regression" will get corrected from the floor. The slide 4 → slide 6 arc ("Woz wrote a generator…" → "Applesoft, 1978") invites exactly that reading.

→ Slide 6 subtitle: **"Applesoft, 1978 (Microsoft's 6502 BASIC, licensed)"**

---

## 3. Ordering and pacing

### 3.1 Estimated timing as the deck stands

Assumes the notes are followed.

| Slide | Content | Est. min | Verdict |
|---|---|---|---|
| — | Cold-boot demo (×3 power cycles) | 3–4 | Right. Each power cycle takes time; plan around it. |
| 1 | Title | 0.25 | — |
| 2 | The Problem | 1 | Too thin: no source, no stakes (§0.2, §2.2) |
| 3 | What an RNG is | 1.5 | **Over-explained** for this room. Cut to 30 s. |
| 4 | Integer BASIC 1977 | 2–3 | Vague bullets (§4) |
| 5 | KEYIN counter, 4 ROMs | **5–6** | **Drags.** Five images and four URLs. Walking four ROM variants loses the thread. |
| 6 | Applesoft `$EFAE` listing | 4–5 | Right weight, weak headline |
| 7 | Manual | 3 | Dense scans; the point is never made (§1.6) |
| 8 | Sources | 3–4 | A list; should be the stakes and history beat |
| 9 | The fix | 3 | **Too compressed** for the payoff; no demo |
| 10 | Close | 0.5 | Missing QR/link and takeaways |
| | **Total** | **~27–31** | Leaves 10–15 min of Q&A in a 45-min slot. Right-sized. |

### 3.2 Recommendations

1. **Swap slides 6 and 7: the promise before the reality.** The manual says "a new random number each time" (7); then the code shows nothing feeds `$C9` (6). The code slide becomes the reveal where the regression lands. It then leads straight into "and people found this, repeatedly" (8). Once numbering uses fields (§1.1), the swap costs nothing.
2. **Compress slide 3 to 30 seconds.** Keep it only as a stage for the amber line (reworded in §4). Its notes already concede the room knows this.
3. **Slide 5: walk the left side only; say the right side in one line.** Show the original F8 KEYIN loop and the Integer BASIC RND. Summarize the right column as "same counter in the Autostart ROM, the IIe, and the IIc; links on the slide." Don't point at each image. Saves about 2 minutes, which should go to slide 9.
4. **Slide 8: stakes first, then the timeline.** Aldridge's memory experiment, then 1982→1999: "found, reported, worked around one program at a time, never fixed at the source."
5. **Slide 9: open with the rebuttal on screen, then the patch, then the demo.** Right now the rebuttal lives only in the notes. Put it on screen as the transition:
   > **New code:** `X = RND(-PEEK(78)-256*PEEK(79))`: Apple's own advice, 1987.
   > **Existing code:** you can't edit it, and it fails silently.
   >
   > The rebuttal is strong; it's just invisible. Citing that *Apple itself* gave this one-liner to a research lab (Aldridge) turns "just seed it first" from a heckle into your setup: "Right, and that's what Apple told people to do, one program at a time, if they happened to find out."
6. **For a 25-minute slot:** cut slide 5's right column entirely and drop the RND(0) scan from slide 7. Do not cut the closing demo.

### 3.3 Final running order (still 10 slides)

0 Title *(after demo)* · 1 The Problem · 2 Same seed, same dice · 3 Integer BASIC 1977 · 4 The counter · **5 Applesoft manual** · **6 Applesoft code** · 7 Found and worked around · 8 The fix *(plus live proof)* · 9 Takeaways, "now", link/QR

---

## 4. Wording rewrites

| Slide | Current | Replacement |
|---|---|---|
| 3 | "Entropy is the key to sufficient randomness and unpatterned results." | **"Same starting number → same 'random' numbers. Every time."** This is the idea slides 4–6 actually depend on. "Sufficient" and "unpatterned" are undefined; the room needs the determinism point, not a definition of entropy. |
| 3 | "What a random number generator is" | **"Pseudo-random means repeatable"** |
| 4 | "Sufficiently random" | **"Different every run"**. That's the property that matters to the thesis. If you want a quality claim, use a measured one instead of "sufficiently". |
| 4 | "Known period with limited range" | **"15-bit shift register: repeats every 32,767 calls"** [EMU: `woz/intbasic_rnd_emu.py`; feedback = bit 14 XOR bit 13; period 32,767 from every start state tested] |
| 4 | "No Floating point" | **"Integers only: RND(n) returns 0 to n−1"** [the routine ends in `jmp MOD`; confirm the range against the Integer BASIC manual] |
| 4 | "Built-in Seed" | **"Seeded by you: how long you took to press a key"** |
| 4 | "There's a counter at $4E and $4F that goes up while the monitor sits waiting for a keypress. Integer BASIC reads it." | "…waiting for a keypress. **Integer BASIC's generator *is* that counter.**" (see §2.3) |
| 5 | "Present in some form in all Apple II ROMs" | **"Same counter in the II, II+, IIe and IIc ROMs"**. Name the ROMs you actually show. "All" invites "what about the IIgs?" |
| 5 (note) | "Sit there two seconds and it's gone round tens of thousands of times." | "It counts about **68,000 times a second**. The 16-bit counter wraps roughly **once a second**." [calculation: 1,020,484 Hz ÷ 15 cycles per loop; `woz/intbasic_rnd_emu.py`] |
| 6 | "Applesoft relies on different seed" | **"Seed: `$C9`, filled from ROM at power-on"** |
| 6 | "However, the seed for Integer BASIC remains." | **"`$4E/$4F` still counts. Applesoft never reads it."** Make this the headline. It's the thesis. |
| 6 | "Takes the seed at $C9, multiplies, adds, swaps two bytes around, forces the result under 1, writes it back to $C9." | Keep, and add **"Nothing outside RND ever touches `$C9`."** |
| 7 | *(caption missing)* | **"Repeatable on purpose: documented. Repeatable by accident: not."** |
| 8 | "Sources" | **"Found in 1982. Worked around until 1999. Never fixed."** |
| 8 | "Kaner & Vokey, 1982 / First published account. Dr. Kaner sent me the paper directly." | **"Kaner & Vokey (written 1982, MICRO 1984): RND fell into a loop of 202 numbers."** |
| 8 | "Aldridge 1987, Gleason 1988 / Behavior Research Methods. ERIC EJ372427." | **"Aldridge 1987: a memory experiment gave the same 'random' word list to every day's first subject."** Then separately: **"Gleason 1988 (Collegiate Microcomputer): published a list of seeds that pass."** |
| 8 | "Found the startup bug. The seed copy is off by one." | **"Seed init copies 4 of 5 bytes (`$F151`: `$1C`→`$1D`)."** |
| 9 | "Two Part Solution" | **"The Fix: Put the Counter Back"**. "Solution" reads as *the* fix; the scope in §2.4 makes it *a* fix, and more honest. |
| 9 | "(may impact HFIND, supposedly unused by AppleSoft.)" | **"Overwrites HFIND (`$F5CB`), which Applesoft never calls."** |
| 9 | "1. Preserves negative and zero RND() functionality while relying on the KEYIN counter present in the ROM." | **"1. RND(1) seeds from `$4E/$4F`. RND(−n) and RND(0) behave exactly as documented."** *(confirm the reseed semantics)* and **"2. Fixes the seed, not the generator. Needs a language card."** |
| 10 | "Try it yourself" *(alone)* | Keep, and put the three takeaway lines from §2.6 above it, plus **URL text** and the **QR** below it. |

---

## 5. If you change only three things

**Prerequisite, about 10 minutes:** the mechanical sweep in §1.1–1.5. That covers badge numbers, notes on slides 2 and 7, the 26→28 count, the orphaned "202", the slide 8 citations, and the missing QR. These are errors, not choices.

1. **Make the opening claim bulletproof and give it stakes.**
   - Power-cycle during the demo; don't reboot (§0.1).
   - Put Aldridge's "exactly the same sequence each time the machine is powered on" on slide 2 (§0.2).
   - Lead slide 8 with the memory experiment (§2.1).

   The problem statement is currently one number with no source and no victim.

2. **Say what the fix does, what it doesn't, and prove it.**
   - Slide 9: one behavior line and one scope line ("fixes the seed, not the generator; needs a language card").
   - Put the `RND(-PEEK(78)-256*PEEK(79))` rebuttal on screen as the lead-in.
   - Close with a 90-second power-cycle demo showing different numbers (§2.4, §2.5, §3.2.5).

3. **Close with the goals and deliver the "Now."**
   - Slide 10 gets the three takeaway lines, plus the URL and QR, which are currently absent.
   - One sentence and one line for the modern parallel (Debian OpenSSL 2008, as a parallel, not a lineage), or retitle the subtitle (§2.6, §2.7).

---

### Appendix: Q&A to prepare for, created by the fixes above

- *"I rebooted and got a different number."* → Only power-on repeats; the fifth seed byte is never copied (Aldridge 1987; AAL May 1984).
- *"My IIe gives a different number than yours."* → Same reason. The byte at `$CD` depends on the machine's power-on RAM **[INF]**; it's still the same on every power-on of *that* machine.
- *"Does the patch fix the 202 loop?"* → No. It fixes the seed. Replacing the generator breaks programs that depend on `RND(-n)` being repeatable, and there's no room in ROM for it.
- *"What if a turnkey game calls RND before any keypress?"* → Aldridge's caveat applies. Answer based on the patch's actual reseed behavior.
- *"ProDOS lives in the language card."* → **[INF, verify before the show]**
- *"Is `$F5CB` safe?"* → HFIND; "not called by any Applesoft routine" (McFadden). Only a direct `CALL 62923` would break.
