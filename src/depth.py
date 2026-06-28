"""depth core: deterministic chains of single-digit addends (so every model and condition sees
identical problems), their exact sum, robust parsing of the model's final integer, and the
depth-frontier reduction - the longest chain a model still sums at a threshold. Single-digit
terms keep the per-step arithmetic trivial, so a failure is losing track of the sequence, not a
computation error. Deterministic and exact; no judge.
"""
from __future__ import annotations

import random
import re
from typing import Mapping, Optional, Sequence

_INT = re.compile(r"-?\d+")


def gen_chain(k: int, n: int, seed: int) -> list[list[int]]:
    """n chains of exactly k single-digit terms (1-9). The RNG is seeded from (seed, k) so each
    chain length has its own reproducible stream, and a fixed seed reproduces identical problems
    across every model and condition.
    """
    rng = random.Random(f"{seed}:{k}")
    return [[rng.randint(1, 9) for _ in range(k)] for _ in range(n)]


def chain_sum(terms: Sequence[int]) -> int:
    return sum(terms)


def parse_int(text: str) -> Optional[int]:
    """The model's final integer: the last integer on the last line that contains one, reading
    bottom-up (so trailing blank lines and a final answer line are handled). Commas stripped.
    None if the reply contains no integer.
    """
    for line in reversed(text.splitlines()):
        nums = _INT.findall(line.replace(",", ""))
        if nums:
            return int(nums[-1])
    nums = _INT.findall(text.replace(",", ""))
    return int(nums[-1]) if nums else None


def correct(pred: Optional[int], gold: int) -> bool:
    return pred == gold


def frontier(acc_by_k: Mapping[int, float], threshold: float) -> int:
    """Longest chain length solved at or above `threshold`, counting only the contiguous run
    from the shortest chain up (so a lucky pass past a failure does not inflate it). 0 if the
    shortest chain already fails.
    """
    best = 0
    for k in sorted(acc_by_k):
        if acc_by_k[k] >= threshold:
            best = k
        else:
            break
    return best
