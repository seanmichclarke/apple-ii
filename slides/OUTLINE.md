# Deck Skeleton — The Problem of the Apple II RNG

Status: **structure only.** Agents fill content into these slots; reviewers attack the
structure itself for gaps. Slide count target: 28–34 (45–60 min talk with live demos).

Audience reminder: they know 6502, AppleSoft, soft switches, zero page. Do not spend a
slide explaining BASIC. Do spend slides on LCG spectral structure — that is the part
they likely have not seen applied to this machine.

---

## Act I — Problem statement (slides 1–12)

1. **Title** — The Problem of the Apple II RNG
2. **The claim** — Stated bluntly up front: the Apple II had no entropy source, only the
   appearance of one. Promise the four-part proof.
3. **Why this audience should care** — every game's shuffle, every `RND`-driven maze,
   every "random" dungeon on this platform inherited it.
4. **Demo (live)** — cold boot, run a 5-line `RND` program, reset, run again: identical
   output. Set the hook before explaining it. ← `source/demos.md`
5. **Taxonomy of the flaw family** — the four failure modes on one diagram, so the
   audience has the map before the detail. ← `assets/`
6. **Failure mode 1: the AppleSoft LCG** — what the algorithm is. ← `source/applesoft-rnd.md`
7. **The disassembly** — real bytes, real addresses, annotated. ← `source/applesoft-rnd.md`
8. **The constants and the period** — multiplier, addend, FP representation, actual
   period length. ← `research/LITERATURE.md` quantitative section
9. **Spectral structure** — Marsaglia's planes, applied to *these* constants. The
   intellectual centerpiece. ← `research/LITERATURE.md`
10. **Failure mode 2: the `$4E/$4F` seed** — keyboard-scan counter as pseudo-entropy.
    ← `source/keyboard-seed.md`
11. **Failure mode 3: post-reset determinism** — why every machine agreed.
12. **Failure mode 4: `RND(0)` and negative arguments** — opaque semantics, predictable
    misuse. ← `source/demos.md`

## Act II — Why it was built this way (slides 13–20)

13. **Pivot slide** — this is not a story about incompetence. Signals the charitable turn.
14. **1977 constraints, quantified** — ROM bytes, chip count, cost per part, cycles.
    ← `woz/DESIGN_INTENT.md`
15. **What Woz actually built** — Integer BASIC RNG and the keyboard counter.
16. **Attribution slide (load-bearing)** — AppleSoft `RND` is *Microsoft's* 6502 BASIC
    LCG, not Wozniak's code. Sourced explicitly. Getting this wrong in front of this
    audience forfeits the room. ← `woz/DESIGN_INTENT.md`
17. **Integer BASIC vs AppleSoft, side by side** — two designs, two sets of assumptions.
    ← `source/integer-basic-rnd.md`
18. **The entropy sources that existed** — cassette noise, floating bus, paddle ADC
    (`$C064`), VBL — and what each cost in chips and cycles.
19. **The charitable reading** — strongest honest defense of the 1977 choices.
20. **Where the defense runs out** — undocumented determinism, opaque `RND(0)`. The
    failure was as much documentation as algorithm.

## Act III — Resolution (slides 21–28)

21. **What "fixed" means here** — separate the algorithm problem from the seeding problem;
    they need different fixes.
22. **Period solutions** — what contemporaries actually shipped to work around it.
    ← `research/LITERATURE.md` period press
23. **Better seeding on real hardware** — paddle/VBL/cassette harvesting, with code.
24. **Better algorithms within 6502 budget** — LFSR / xorshift-class, cycle and byte cost
    against the original.
25. **Demo (live)** — the same program with a harvested seed and a better generator.
26. **Honest limits** — what you still cannot get on this machine, and why "cryptographic"
    was never on the table.
27. **Contested ground** — where the historical record is thin or sources disagree; say so
    rather than resolving it silently. ← `research/LITERATURE.md` contested section
28. **What modern practice inherited** — the same two mistakes (weak default, unexamined
    seed) recur; name the lineage without overclaiming.

## Act IV — Goals (slides 29–32)

29. **Goals of this talk, restated as takeaways** — three sentences the audience should
    leave repeating.
30. **The transferable lesson** — "no entropy source, only the appearance of one" as a
    design smell that outlived the platform.
31. **Further reading** — curated, not a citation dump. ← `research/LITERATURE.md`
32. **Backup / appendix** — full disassembly, statistical test tables, demo listings for
    the inevitable hard questions from this crowd.

---

## Open structural questions for the reviewers

- Is Act II placed correctly? Defending the design *before* offering the resolution may
  drain momentum — argue for or against moving it after Act III.
- Is the spectral-structure slide (9) too deep for a 45-min slot, or the reason the talk
  exists?
- Does the talk need a slide on *how the flaw was discovered* historically, or is that a
  digression?
- Is four failure modes too many to hold in one talk? If one must be cut, which earns
  its place least?
- Does the modern-lineage slide (28) overclaim? It is the easiest slide to attack.
