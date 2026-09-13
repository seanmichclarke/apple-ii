# APPLEii: Applesoft's Loaded Dice, deliverables

Materials for **Jeff Robison's VCF Midwest 21 (2026) talk**, *"Applesoft's Loaded Dice: The Truth About Randomness on the Apple II, Then and Now."* Everything here is a recommendation for the presenter. Audience-facing decisions are Jeff's.

**Thesis (unchanged, sharpened):** Integer BASIC (1977) seeded its RND from the monitor's live keyboard-wait counter at `$4E/$4F`. Applesoft II, which is Microsoft's 6502 BASIC, seeds from ROM, and its seed copy is off by one. So every *power-on* of a given machine repeats the same sequence, and the counter goes unread. It's a regression of the default, not of what was possible.

## Start here
| If you want… | Open |
|---|---|
| Jeff's deck with the fixes applied | `01_Edited_Deck/Applesoft_Loaded_Dice_Deck_1_EDITED.pptx` |
| What was changed and why, slide by slide | `01_Edited_Deck/CHANGES.md` |
| The expanded companion deck (19 slides + 5 backup) | `02_New_Deck/Applesoft_Loaded_Dice_Expanded.pptx` |
| The same deck in a browser (← → keys, **N** for notes) | `02_New_Deck/Applesoft_Loaded_Dice_Expanded.html` |
| What to test on real hardware before the show | `03_Collateral/HARDWARE_TEST_PLAN.md` |
| Answers to the hard questions | `03_Collateral/QA_PREP.md` |

## Folder map
```
APPLEii/
├── README.md                          this file
├── 00_Original_Deck/                  Jeff's deck exactly as received (untouched)
├── 01_Edited_Deck/
│   ├── Applesoft_Loaded_Dice_Deck_1_EDITED.pptx   same 10 slides, same look, errors fixed
│   └── CHANGES.md                     every edit (before/after, reason, source) + open items
├── 02_New_Deck/
│   ├── Applesoft_Loaded_Dice_Expanded.pptx        native PowerPoint; imports into Keynote
│   ├── Applesoft_Loaded_Dice_Expanded.html        self-contained, images embedded
│   ├── Applesoft_Loaded_Dice_Expanded.marp.md     Marp source (images from ../assets)
│   └── KEYNOTE_OUTLINE.md             per-slide content, notes, assets
├── 03_Collateral/
│   ├── HANDOUT.md                     one-page audience handout
│   ├── QA_PREP.md                     expected questions with labelled answers
│   ├── FACT_SHEET.md                  every on-slide number → label → source
│   ├── HARDWARE_TEST_PLAN.md          BASIC test programs + compatibility matrix
│   └── SOURCES.md                     bibliography
├── 04_Research_and_Evidence/
│   ├── VERIFY_LOG.md                  independent re-run of the headline numbers
│   ├── REVIEW_A_TECHNICAL.md          adversarial technical review
│   ├── REVIEW_B_NARRATIVE.md          narrative/completeness review
│   ├── DECK_REVIEW_PASS1.md           mechanical review of the original
│   ├── LITERATURE.md                  annotated literature record
│   ├── DESIGN_INTENT.md               Woz/Microsoft attribution and design constraints
│   ├── applesoft-rnd.md               annotated, byte-verified RND listing
│   ├── BRIEF.md                       original research brief
│   ├── emulator_evidence/             raw emulator runs
│   └── tools/                         py65 harnesses (need an Apple ][+ ROM image)
├── assets/deck_images/                images extracted from Jeff's deck
└── _build/                            scripts that regenerate both decks
```

## Biggest corrections to the original deck
1. **The opening demo has to be a power-cycle.** The notes said "reboot". Ctrl-RESET and PR#6 keep the uncopied seed byte, so the number changes.
2. **`.973136996` depends on one uninitialized byte (`$CD`).** The 256 possible values give 181 different first numbers. Someone's own machine may print a different one, but it will still repeat on every power-on.
3. **The duplicated speaker notes are replaced.** Slides 2 and 3 had identical notes, and so did slides 6 and 7. "Twenty-six instructions" is corrected to twenty-eight.
4. **The badges are fixed** (0,1,2,3,4,5,**6**,7,**8**,**9**). The citations on slide 8 are corrected: 202 is on screen, the Aldridge and Gleason entries are split, and the "first published" claim is gone.
5. **Slide 9 no longer hedges.** HFIND is not called by Applesoft, and the ][+ ROM has no `JSR`/`JMP $F5CB`. The patch budget is 53 bytes.

## Needs Jeff before the show
- What the patch does on positive `RND`, and its byte length. `Patch_lc.bin` and `LC_Loader.bin` weren't supplied, so nothing about their behavior is verified here.
- Power-cycle the demo machine and confirm the number repeats (test T1).
- The link and QR code for the closing slide. Both decks show an amber placeholder.
- The manual edition for the slide 7 scans.

## How to rebuild
```
python3 -m venv .venv && .venv/bin/pip install python-pptx pillow
.venv/bin/python _build/edit_original_deck.py
.venv/bin/python _build/build_new_deck.py
```

Evidence labels used throughout: **DOC** primary source · **EMU** measured by running the real ROM code in an emulator · **INF** inference · **OPEN/TEST** needs real hardware.
