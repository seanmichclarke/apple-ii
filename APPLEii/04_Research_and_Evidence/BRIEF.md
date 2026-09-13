# The Problem of the Apple II RNG — Presentation Project

## Deliverable
A complete presentation: **problem statement → resolution → goals**, on why Apple II random
number generation was fundamentally flawed.

## Audience
Strong vintage-computing knowledge. Comfortable with basic programming, AppleSoft BASIC,
and vintage Apple/Mac hardware. Assume they know what a PEEK, a soft switch, and a
6502 zero page are. Do NOT explain what BASIC is. Do explain LCG spectral structure.

## Central thesis (locked 2026-09-12)
The flaw is **systemic, not a single bug**. Treat these as one family:
1. AppleSoft `RND`'s floating-point LCG — multiplier/period/constants, bit-level
   correlation, low-order-bit weakness, lattice/spectral structure.
2. The `$4E/$4F` keyboard-scan counter as a pseudo-entropy source, seeded by
   human keypress timing.
3. Cold-start / post-reset determinism — every machine reproducing the same
   "random" sequence.
4. `RND(0)` and negative-argument reseeding semantics, and how they were
   misunderstood and misused by programmers.

Framing: *the Apple II had no entropy source, only the appearance of one.*

## Output formats (all three)
1. Hosted self-contained HTML deck (embedded in the Control UI dashboard).
2. Marp/Markdown slide source.
3. Keynote-ready per-slide outline plus standalone code-listing/diagram assets.

## Source-code requirement
Slides must be able to analyze actual source:
- Apple II ROM monitor / Integer BASIC 6502 disassembly.
- AppleSoft BASIC `RND` implementation and its floating-point routines.
Cite addresses and label names. Show real bytes, not paraphrase.

## Directory layout
- `research/` — scientific literature agent output
- `woz/`      — design-intent agent output
- `review/`   — adversarial reviewer output
- `slides/`   — deck source (HTML, Marp, outline)
- `source/`   — disassembly and code listings
- `assets/`   — diagrams and figures

## Standard of evidence
Every factual claim gets a citation or a code reference. Where the historical record
is ambiguous or contested, say so explicitly rather than resolving it silently.
Distinguish firmly between (a) documented fact, (b) strong community consensus,
(c) plausible inference. Label which is which.
