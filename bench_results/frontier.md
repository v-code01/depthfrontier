# depthfrontier: how long a chain of trivial additions can a model track?

Chains of single-digit addends (deterministic per length, identical across models
and conditions). Per-step arithmetic is trivial, so a wrong sum is a tracking
failure, not a computation one. Frontier = longest chain summed at >=0.5 accuracy,
contiguous from the shortest up. direct vs chain-of-thought.

## 1.5B

  cond     k=2   k=3   k=4   k=6   k=8   k=10  k=12  k=16   frontier
  direct   1.00  0.90  0.68  0.40  0.07  0.07  0.00  0.00    4
  cot      1.00  0.97  1.00  0.97  0.97  0.88  0.85  0.70    16

- CoT extends the depth frontier by 12 term(s) (4 -> 16)
- CoT vs direct (paired): rescue 171 vs sabotage 2, McNemar p=2.514e-48

## 0.5B

  cond     k=2   k=3   k=4   k=6   k=8   k=10  k=12  k=16   frontier
  direct   1.00  0.78  0.35  0.03  0.05  0.00  0.05  0.00    3
  cot      1.00  1.00  0.82  0.40  0.25  0.03  0.00  0.00    4

- CoT extends the depth frontier by 1 term(s) (3 -> 4)
- CoT vs direct (paired): rescue 57 vs sabotage 7, McNemar p=7.638e-11

