# Open items only Jeff can settle

For Jeff Robison. *Applesoft's Loaded Dice*, VCF Midwest 21 (2026).

The research team settled everything it could settle from ROM images, disassemblies,
Microsoft's source, and the papers. The items below need Jeff's machine, Jeff's patch
files, or Jeff's decision.

Both decks mark every place that depends on one of these items. The mark is either
`[Jeff: …]` in the speaker notes, or an amber placeholder on the slide.

---

## A. Blocking. Settle before going on stage.

### A1. What does `$CD` hold at power-on on the demo machine?

**Why it matters.** Cold start copies only 4 of the 5 seed bytes, so the fifth byte
(`$CD`) is whatever RAM held. `.973136996` appears only when `$CD` is `$FE` or `$FF`.
Of the 256 possible values, 181 give different first numbers. A room full of Apple II
owners will try this on their own machines.

**Test.** Run it on each machine you might demo on. Do a true power-on each time, and
do not call `RND` first.
```
]PRINT PEEK(205)
]FOR I = 201 TO 205 : PRINT PEEK(I);" "; : NEXT
]PRINT RND(1)
```
Repeat for each boot path you'll use:
- no disk, Ctrl-Reset to the `]` prompt
- DOS 3.3 boot
- ProDOS / BASIC.SYSTEM boot, if you'll claim it

Record the results in the table on backup slide B3 of the new deck.

**Decide.** If the demo machine prints `.973136996`, say "on this machine, every
power-on." If it doesn't, the slide should show the number your machine prints. The
argument doesn't change.

### A2. What does the patch do to `RND(1)`?

**Status.** `LC_Loader.bin` and `Patch_lc.bin` are not in the project workspace, so
nobody has seen the code. Slide 9 describes how the patch is installed but not what it
does. Each possible behavior fails in a different way:

| If positive `RND`… | Then… |
|---|---|
| reseeds from `$4E/$4F` on every call | A tight loop with no keypress reads the same counter every time, so it returns near-identical values. That is worse than stock. |
| mixes the counter into the state on every call | It breaks the documented promise that `RND(-n)` followed by `RND(1)` repeats, as soon as there's any `INPUT` or `GET` in between. |
| seeds once, on the first call | Where is the "already seeded" flag kept? Do `RUN`, `NEW`, `CLEAR` or `RND(-n)` reset it? |
| builds a negative seed from the counter | When the counter reads `$0000`, `SIGN` returns 0, the call takes the `RND(0)` path, and nothing is reseeded. |

**Need from Jeff:**
- The binaries or the source listing, so the team can annotate them.
- A one-sentence statement of the behavior.

### A3. Patch size: 53 bytes or fewer

HFIND runs from `$F5CB` to `$F5FF`, which is **53 bytes**. `$F600` is an `RTS` that
HLIN branches to (`BEQ` at `$F59C`). A patch longer than 53 bytes breaks `HPLOT … TO`,
and a longer one also breaks `DRAW`/`XDRAW`, which start at `$F601`. This was verified
against the II Plus ROM bytes.

> `woz/DESIGN_INTENT.md` says 54 bytes. That figure is wrong because `$F600` is shared.

**Need from Jeff:**
- The byte count.
- A hi-res regression test after patching. See `DEMO_PROGRAMS.md` §4e.

### A4. Where does the patch work, and where does it break?

Slide 10 says "Try it yourself." These configurations are likely to fail. None has been
tested.

| Configuration | Risk |
|---|---|
| ProDOS 8 / BASIC.SYSTEM | The ProDOS kernel lives in language-card RAM, so the loader overwrites the OS. |
| DOS 3.3 with the other BASIC in the LC | `FP`/`INT` flip the LC switches, which may silently unpatch. |
| Original Apple II (Integer BASIC in ROM) | The loader copies Integer BASIC into the LC and writes `JMP` into the middle of it. |
| IIe / IIc, Ctrl-Reset | RESET forces ROM read, so the patch is silently off. |
| ][+ with third-party 16K/32K/128K cards | RESET behavior and banking vary by card. |
| Programs that use the LC (Pascal, CP/M, RAM disks, `/RAM`) | These destroy the patch, or the patch destroys them. |
| //c ROM revisions, IIc Plus, IIgs | Applesoft bytes at `$EFAE`, `$F150` and `$F5CB` were not checked. |

**Decide one:**
1. The loader checks and refuses unsafe configurations, and the slide says so.
2. The slide names what's supported, for example: "II Plus / IIe, DOS 3.3 or no DOS; not
   ProDOS."
3. Offer a `USR`/`&` hook in main RAM as an alternative, which avoids the LC entirely.
   This is the approach AAL 1984 and Call-A.P.P.L.E. 1983 took.

Backup slide B4 in the new deck is an empty matrix for recording results.

### A5. URL and QR for the closing slide

The closing slide has no link and no QR code. The notes say "Link and QR. Nothing
else." Both decks carry an amber placeholder.

The team did not look at or use the Codeberg site. Jeff supplies the link.

---

## B. Should settle. A pedant will ask.

| # | Item | Current handling |
|---|---|---|
| B1 | Which printing of the Applesoft manual the slide 7 scans come from | No edition on screen; flagged in notes |
| B2 | Author of Call-A.P.P.L.E. "RND is Fatally Flawed" (Jan 1983). "D. Sparks" comes only from a search snippet | Author not named |
| B3 | Gleason (1988): only the abstract was read | Slide says only what the abstract says |
| B4 | Whether HFIND/`$F5CB` was a published entry point (Apple II Reference Manual, *What's Where in the Apple*, Nibble). The ROM itself never calls it | Notes say "no Applesoft routine calls it" and name `CALL 62923` as the residual risk |
| B5 | How widely `RND(-(PEEK(78)+256*PEEK(79)))` was published before 1984 | Deck cites Aldridge 1987 for Apple's own advice, and nothing earlier |
| B6 | Whether the RAM-loaded 1978 Applesoft releases share the seed bug and the same seed bytes | Slide 6 now says "Applesoft II", not "1978" |
| B7 | Subtitle "Then and Now" | The new deck adds a "Now" slide (Debian OpenSSL 2008, as a parallel). The edited deck keeps the subtitle; cut it if the "Now" slide isn't used |
| B8 | Apple's license fee ($21K vs $31K in secondary sources) | Not used anywhere. Keep it that way |

---

## C. Structure (recommendations Jeff may reject)

The **edited deck** keeps Jeff's structure. It makes only mechanical fixes, factual
corrections, and minimal wording changes. The **new deck** applies these structural
recommendations:

1. Swap the manual and code slides: show the promise, then the reality.
2. Add "why nobody noticed" (only power-on repeats).
3. Put the off-by-one on its own slide instead of burying it in the sources.
4. Add a side-by-side comparison: "a regression of the default, not the capability."
5. Show the "just seed it first" rebuttal on screen.
6. Add a closing proof demo: power-cycle → different number.
7. Add takeaways and a "Now" beat.
