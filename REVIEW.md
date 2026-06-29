# Adversarial review

An attempt to refute each headline claim before publishing. Every objection I could construct
is listed with how the data answers it. Claims that survived are the ones reported.

## Claim A: the direct depth limit is a tracking failure, not arithmetic

- **"The sums get large, so it is arithmetic after all."** The sum of sixteen single-digit
  numbers is at most 144 - a three-digit number the models add fluently in the sibling study
  (three-digit addition is near 0.9). And the running-total CoT condition, which does the exact
  same additions one at a time, reaches 0.70 at sixteen terms on the 1.5B. So the additions are
  not the problem; holding the partial sum across many of them is.
- **"Your parser drops the answer on long direct outputs."** The direct condition is capped at
  16 tokens and the answer is a short integer; the parser is unit-tested on single-number and
  trailing-line outputs. If parsing failed at length, the CoT condition (longer, multi-line)
  would suffer more, not less - instead CoT is far more accurate.

## Claim B: CoT rescues the capable model but not the weak one

- **"CoT just has more tokens."** That is the mechanism, not a confound: the extra tokens are
  spent writing the running total, which is exactly what removes the working-memory bottleneck.
  The point is that the same extra tokens help the 1.5B enormously (frontier 4 to 16) and the
  0.5B barely (3 to 4), so it is not tokens alone - it is whether the model can sustain the
  bookkeeping.
- **"171 vs 2 is too lopsided to be real."** It is lopsided because the direct condition fails
  almost everything past 4 terms while CoT succeeds almost everything up to 16; the discordant
  pairs are overwhelmingly rescues. The exact McNemar p is 2.5e-48, and verify.py recomputes the
  counts independently.

## Claim C: the rescue scales with capability

- **"You are inferring a scaling law from two models."** The claim is a described contrast, not a
  law: CoT extends the 1.5B frontier by 12 terms and the 0.5B by 1, and the 0.5B's CoT accuracy
  itself decays with length (0.25 at 8, 0 by 12). Both facts are shown, not extrapolated.

## Confounds checked

- Deterministic chains per length: every model and condition sees identical problems, so
  CoT-vs-direct and model-vs-model are paired.
- Single-digit terms: per-step arithmetic is trivial, isolating tracking depth.
- Ground truth is the Python sum; exact integer match; no judge.
- Greedy decoding, temperature 0, fixed seed: outputs are deterministic.

## What this does NOT claim

- Not that CoT is always good - a companion study shows it hurts on retrieval multiple choice.
  It helps here because the task decomposes into a running total.
- Not that the depth limit is fundamental - it is a working-memory limit that externalizing the
  count (CoT, or a scratchpad, or a tool) relaxes.
- Not a claim about larger models, other operations, or other prompt formats.
