# depthfrontier

How many *trivial* operations can a small language model chain before it loses track? This sums
lists of single-digit numbers - where each addition is easy - and measures accuracy as the list
gets longer, for two instruction-tuned models (Qwen2.5 1.5B and 0.5B), direct answer versus
step-by-step, with ground truth computed in Python and no judge.

The headline: **there is a severe reasoning-depth limit that has nothing to do with
arithmetic.** Neither model can reliably add more than three or four single-digit numbers in
one shot. Chain-of-thought rescues it almost completely for the capable model (its frontier
jumps from 4 to 16 terms) but barely for the weak one (3 to 4), because keeping a running total
across many steps is itself a capacity that scales with model size.

## Method

- Each problem is a chain of k single-digit addends (1-9), generated deterministically per
  length k, so every model and both conditions see the **identical** problems and CoT-vs-direct
  is a paired comparison.
- Chain lengths k in {2, 3, 4, 6, 8, 10, 12, 16}, two conditions (direct: "reply with only the
  final integer"; CoT: "think step by step, final result on the last line"), both models, n=40
  per cell.
- The sum is computed exactly in Python; the model's final integer is parsed and matched. Since
  the terms are single digits, a wrong sum is a **tracking** failure, not an arithmetic one.
- The **depth frontier** is the longest chain summed at >=0.5 accuracy, counting the contiguous
  run from the shortest chain up.

## Pre-registered prediction

Written down before the full run (a small pilot probe showed a sharp collapse and a CoT rescue):

> (1) Accuracy falls with chain length despite trivial per-step arithmetic - a depth limit, not
> an arithmetic limit. (2) The smaller model's depth frontier is shorter. (3) CoT substantially
> extends the frontier, because a running total is exactly the bookkeeping it supplies -
> consistent with the arithmetic-magnitude result and opposite of the multiple-choice one.

All three held; the size of the CoT rescue turned out to scale sharply with the model.

## Results (n=40 per cell)

Accuracy by chain length k, and the depth frontier (>=0.5, contiguous):

```
1.5B      k=2   k=3   k=4   k=6   k=8   k=10  k=12  k=16   frontier
direct    1.00  0.90  0.68  0.40  0.07  0.07  0.00  0.00      4
cot       1.00  0.97  1.00  0.97  0.97  0.88  0.85  0.70     16

0.5B      k=2   k=3   k=4   k=6   k=8   k=10  k=12  k=16   frontier
direct    1.00  0.78  0.35  0.03  0.05  0.00  0.05  0.00      3
cot       1.00  1.00  0.82  0.40  0.25  0.03  0.00  0.00      4
```

CoT vs direct, paired over identical chains (pooled across all lengths):

| model | rescue (direct wrong, CoT right) | sabotage (direct right, CoT wrong) | McNemar p |
|-------|---------------------------------:|-----------------------------------:|----------:|
| 1.5B  | 171                              | 2                                  | 2.5e-48   |
| 0.5B  | 57                               | 7                                  | 7.6e-11   |

Full numbers in `bench_results/frontier.md`.

## What this shows

1. **The direct depth limit is tiny and is not about arithmetic.** Every single addition here is
   single-digit and trivial (both models add one digit at ~1.0), yet the 1.5B cannot reliably
   sum 8 of them in one shot (0.07) and the 0.5B fails at 6 (0.03). What breaks is keeping the
   running total in mind, not the addition.
2. **The frontier shrinks with model size.** The 0.5B's direct frontier is 3 terms versus the
   1.5B's 4.
3. **CoT rescues the capable model almost completely.** Writing the running total moves the
   1.5B's frontier from 4 to 16 terms, still 0.70 at 16, with a near-total rescue asymmetry (171
   fixed versus 2 broken, p=2.5e-48). Externalizing the count removes the working-memory
   bottleneck.
4. **The rescue itself scales with capability.** CoT barely helps the 0.5B (frontier 3 to 4):
   even with running totals it drifts (0.25 at 8 terms, 0 by 12). Sustaining the bookkeeping over
   many steps is a capacity the small model lacks, so the same intervention that nearly solves
   the task for the 1.5B only nudges the 0.5B.
5. **Same direction as arithmetic magnitude, opposite of retrieval multiple choice.** CoT helps
   where the task genuinely decomposes into steps (long sums, big additions) and hurts where it
   does not (retrieval multiple choice). Here the decomposition is a running total, and it helps
   in proportion to how well the model can carry it.

## Limitations and falsifiers

- Two model sizes, one operation (addition), one prompt pair per condition, greedy decoding,
  n=40 per cell. Not a claim about larger models or other operations.
- Single-digit terms are a deliberate design choice to remove arithmetic difficulty and isolate
  tracking depth; larger terms would confound the two (that is the sibling study).
- **Falsifier:** if direct accuracy had stayed high as chains grew, there would be no depth
  limit. It collapses to near zero by 8 terms.
- **Falsifier:** if CoT had not extended the frontier or had sabotaged more than it rescued, the
  rescue claim would fail. It rescues 171 vs 2 on the 1.5B.
- The adversarial pass that tried to refute each claim is in `REVIEW.md`.

## Reproduce

```bash
./scripts/gate.sh                 # ruff + mypy --strict + pytest + ASCII + independent verify
./reproduce.sh 8081 8082          # rerun both models against two OpenAI-compatible endpoints
```

`tools/verify.py` recomputes the frontiers and the paired CoT-vs-direct McNemar straight from
the raw JSONL, sharing no code with the analysis, and the ship gate runs it.

## Layout

```
src/depth.py         deterministic single-digit chains + exact sum + robust parse + frontier
tests/test_depth.py  6 unit tests, including the frontier and the last-line integer parse
tools/run_sweep.py   chain-length x condition sweep, identical chains per cell
tools/analyze.py     accuracy by length, frontiers, CoT extension, paired McNemar
tools/verify.py      independent recompute of the headline claims (in the gate)
bench_results/       frontier.md + curve.json
claims.toml          every claim tied to its evidence
REVIEW.md            adversarial refutation attempt
```

MIT licensed.
