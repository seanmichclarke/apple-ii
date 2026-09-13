# Demo programs and pre-show tests

Type these at the Applesoft `]` prompt unless a section says otherwise. Section 2 is
typed at the Integer BASIC `>` prompt.

Wherever a step says **power-cycle**, it means: flip the power switch off, wait a few
seconds, switch back on.

Ctrl-Reset, `PR#6`, and `3D0G` are **not** power-cycles, and they won't reproduce the
problem.

---

## 1. Opening demo: the loaded dice

Do this three times before the title slide:

1. Power-cycle.
2. At the `]` prompt, type:
   ```
   ]PRINT RND(1)
   ```

The same number comes up every time. On the machine that took the deck's screenshot, it
was `.973136996`.

If the number differs from the slide, show that number anyway. The argument doesn't
depend on the exact value (see Section 5).

## 2. Integer BASIC: seeded by you

On a machine or card with Integer BASIC:

```
>10 PRINT "PRESS A KEY": INPUT A$
>20 FOR I = 1 TO 5: PRINT RND(100): NEXT I
>RUN
```

Press Return at a different moment each run, and the numbers change. The wait at
`INPUT` spins `$4E/$4F`, and Integer BASIC's `RND` state *is* that counter.

## 3. Why nobody noticed: only power-on repeats

```
]10 FOR I = 1 TO 5 : PRINT RND(1) : NEXT
]RUN
]RUN
```

- The two `RUN`s print different numbers, so it looks fine.
- Power-cycle, retype or reload the program, then `RUN`. The first run's numbers come
  back.

## 4. Pre-show test battery for the patch

Run each test twice: once on stock ROM, once patched. Record the results in the new
deck's backup slide B4 and in `OPEN_ITEMS_FOR_JEFF.md` A2–A4.

**4a. `RND(-n)` still repeats, even with keyboard input in between**
```
]10 X = RND(-1) : FOR I = 1 TO 5 : PRINT RND(1) : NEXT
]20 PRINT "PRESS A KEY" : GET A$
]30 X = RND(-1) : FOR I = 1 TO 5 : PRINT RND(1) : NEXT
]RUN
```
Pass: lines 10 and 30 print identical columns.

**4b. `RND(0)` returns the last value**
```
]PRINT RND(1) : PRINT RND(0)
```
Pass: both numbers are the same.

**4c. Tight loop with no keypress**
```
]10 FOR I = 1 TO 52 : C(I) = RND(1) : NEXT
]20 FOR I = 1 TO 52 : PRINT C(I) : NEXT
]RUN
```
Pass: no runs of identical or near-identical values. (Arrays up to index 10 don't need
`DIM`; this loop needs `DIM C(52)` first.)

**4d. Turnkey program calls `RND` before any key**

Save as `HELLO` on a DOS 3.3 disk:
```
10 PRINT RND(1)
```
Power-cycle and boot it three times. Record what prints each time.

**4e. Hi-res regression (HFIND overwritten, `$F600` intact)**
```
]HGR : HCOLOR = 3
]HPLOT 0,0 TO 279,159
]HPLOT 279,0 TO 0,159
```
Then load any shape table and run `DRAW 1 AT 140,80`, `XDRAW 1 AT 140,80`, `SCALE = 2`,
`ROT = 16`, and `DRAW` again.

Pass: lines draw fully, and the shape draws and erases.

**4f. RESET**

Press Ctrl-Reset, then run test 1's `PRINT RND(1)` twice across a power-cycle.

Record whether the patch is still active on the ][+ language card, the IIe, and the IIc.

**4g. DOS 3.3 `FP` / `INT`**

After loading the patch, type `FP`, then `PRINT RND(1)` across a power-cycle. Repeat with
`INT`, then `FP`.

**4h. ProDOS**

Under BASIC.SYSTEM, `BRUN` the loader, then `CAT`.

Record: does it hang? Does it refuse to load?

## 5. Measure `$CD` (resolves the "your number is different" question)

1. Power-cycle.
2. **Before calling `RND`**, type:
   ```
   ]FOR I = 201 TO 205 : PRINT PEEK(I);" "; : NEXT
   ```
   Expect `128 79 199 82 ?`, where the fifth value is `$CD`.
3. Type `]PRINT RND(1)`.

Repeat on every machine, and for each boot path: no disk, DOS 3.3, ProDOS.

Look up the result:

| `PEEK(205)` | First `RND(1)` |
|---|---|
| 254 or 255 | .973136996 |
| 0 | .270011996 |
| 88 | .512199496 |

The other values are listed in `tools/cd_sweep_results.jsonl`. You can also compute them
by running `tools/rnd_experiments.py`.

## 6. Apple's own advice (1987): seed from the counter

```
]10 PRINT "PRESS A KEY" : GET A$
]20 X = RND(-(PEEK(78) + 256 * PEEK(79)))
]30 FOR I = 1 TO 5 : PRINT RND(1) : NEXT
]RUN
```

Edge case to mention if asked: if `PEEK(78)` and `PEEK(79)` are both 0, line 20 is
`RND(0)` and does not reseed. This happens about once in 65,536 runs.

## 7. The one-byte ROM bug, shown live (optional, language card required)

This copies ROM to language-card RAM and patches `$F151` from `$1C` to `$1D`. The seed
copy then includes the fifth byte, and every power-on prints `.512199496`: Microsoft's
intended number, which leads into the 202-number loop.

Only do this on a machine with a known-good LC setup, and never under ProDOS. The team
does not supply a loader for this. It's a suggestion for Jeff's existing `LC_Loader`
code path.
