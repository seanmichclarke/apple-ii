# Deliverables: *Applesoft's Loaded Dice* (Jeff Robison, VCF Midwest 21, 2026)

Prepared 2026-09-12 for Jeff's talk.

- Jeff's original deck is untouched at `../deck/Applesoft_Loaded_Dice_Deck_1.pptx`.
- Every change here is a proposal. Jeff has the final say.
- The Codeberg site was not looked at or used.

## Start here

1. **`03_collateral/OPEN_ITEMS_FOR_JEFF.md`**: five things only Jeff can settle before going on stage:
   - what `$CD` holds on the demo machine
   - what the patch does
   - the patch's byte count
   - which setups the patch works on
   - the URL and QR code
2. **`01_edited_deck/`**: Jeff's own 10 slides, corrected.
3. **`02_new_deck/`**: an expanded, restructured edition: 20 main slides and 7 backup slides.

## Contents

```
01_edited_deck/
  Applesoft_Loaded_Dice_Deck_1_EDITED.pptx   Jeff's deck with fixes applied
  Applesoft_Loaded_Dice_Deck_1_EDITED.pdf    PDF export (rendered by PowerPoint)
  EDIT_LOG.md                                every change: before/after, reason, source

02_new_deck/
  Applesoft_Loaded_Dice_EXPANDED.pptx        PowerPoint; opens in Keynote
  Applesoft_Loaded_Dice_EXPANDED.pdf         PDF export (rendered by PowerPoint)
  Applesoft_Loaded_Dice_EXPANDED.html        self-contained HTML deck
  Applesoft_Loaded_Dice_EXPANDED_marp.md     Marp / Markdown source
  KEYNOTE_OUTLINE.md                         per slide: on-screen text, assets, source, notes
  assets/                                    the 11 listings, manual scans and screenshots from Jeff's deck

03_collateral/
  OPEN_ITEMS_FOR_JEFF.md   blocking and should-settle items
  FACT_SHEET.md            every on-screen number with its source; "don't say / say instead"
  QA_PREP.md               likely questions with short answers
  DEMO_PROGRAMS.md         opening demo, pre-show patch tests, how to measure $CD
  HANDOUT.md               one-page audience handout (URL placeholder)
  SOURCES.md               bibliography, marked by how much of each source was read
  listings/applesoft-rnd.md  annotated RND listing, verified byte for byte
  tools/                   emulator harness and verification scripts
  evidence/                raw emulator output and verification logs
  research/                full literature record and design-intent analysis
  reviews/                 the three reviews of Jeff's original deck

_build/
  edit_jeff_deck.py        rebuilds 01_edited_deck from the original
  build_new_deck.py        rebuilds all four formats of 02_new_deck from one slide definition
```

## What the two decks do differently

| | Edited deck | Expanded deck |
|---|---|---|
| Structure | Jeff's order, 10 slides | Reordered: manual before code; new slides for "why nobody noticed", "one byte short", the loops, the side-by-side comparison, Microsoft's two RNDs, "just seed it first", the fix's scope, the proof demo, and "Now" |
| Changes | Mechanical, factual and minimal wording fixes only | Applies all review recommendations |
| Backup slides | None | Byte-level listing, constants, $CD hardware table (to fill in), compatibility matrix (to fill in), HFIND, Commodore, sources |

## How it was checked

- **Headline numbers:** re-run on the genuine Apple II Plus ROM bytes. The ROM image is AppleWin's, SHA-1 `33a24f54…`. The log is `03_collateral/evidence/verify_headline_numbers.log`.
- **Checked this way:**
  - `.973136996`, `.270011996`, `.512199496`
  - 181 distinct first values
  - the 202-number loop from `$CD=$58`
  - Integer BASIC's period of 32,767
  - that no `JSR` or `JMP` targets `$F5CB`
  - that `$F600` is a shared `RTS`
- **Visual check:** both decks were exported to PDF by Microsoft PowerPoint, and every page was inspected.
- **Not verified, and flagged wherever it appears:**
  - what real DRAM holds in `$CD` at power-on
  - anything about `LC_Loader.bin` and `Patch_lc.bin`, which are not in the workspace
  - the //c and IIgs ROMs
  - who wrote the Call-A.P.P.L.E. article
  - the body of Gleason's 1988 paper (only the abstract was read)

## Correction to earlier team output

`research/DESIGN_INTENT.md` gives the space available at `$F5CB` as 54 bytes. The correct limit is **53**: `$F600` is an `RTS` that HLIN branches to from `$F59C`. Both decks and all collateral use 53.

## HTML deck controls

| Key | Action |
|---|---|
| ← → / Space | move between slides |
| N | speaker notes |
| P | show all slides |

- Append `#12` to the URL to open slide 12.
- Append `?print` to show all slides for printing.

## Rebuild

From `projects/apple2-rng/`:

```
python3 -m venv .venv && .venv/bin/pip install python-pptx pillow py65
.venv/bin/python deliverables/_build/edit_jeff_deck.py
.venv/bin/python deliverables/_build/build_new_deck.py
.venv/bin/python deliverables/03_collateral/tools/verify_headline_numbers.py <Apple2_Plus.rom>
```
