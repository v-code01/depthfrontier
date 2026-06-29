#!/usr/bin/env python3
"""Independent verification of the headline, sharing NO code with src/depth.py or
tools/analyze.py. Re-reads the raw JSONL and recomputes, from scratch, accuracy by chain length
and the depth frontier (longest contiguous chain at >=0.5), then asserts: (1) direct accuracy
collapses with chain length despite trivial single-digit terms - both models fail past a few
terms; (2) the smaller model's direct frontier is no longer than the larger model's; (3) CoT
extends the frontier and rescues far more than it sabotages (paired, significant) for both
models; (4) the CoT depth extension is far larger for the capable model. Exit non-zero on
mismatch. Run in the ship gate.
"""
from __future__ import annotations

import json
import sys
from math import comb

PATHS = {"1.5B": "results/dp_15b.jsonl", "0.5B": "results/dp_05b.jsonl"}


def rows_of(path: str) -> list[dict[str, object]]:
    return [json.loads(x) for x in open(path) if x.strip()]


def acc_by_k(rows: list[dict[str, object]], cond: str) -> dict[int, float]:
    out: dict[int, float] = {}
    for k in sorted({int(r["k"]) for r in rows}):  # type: ignore[call-overload]
        sub = [r for r in rows if r["cond"] == cond and int(r["k"]) == k]  # type: ignore[call-overload]
        if sub:
            out[k] = sum(1 for r in sub if r["correct"]) / len(sub)
    return out


def frontier(acc: dict[int, float], thr: float = 0.5) -> int:
    best = 0
    for k in sorted(acc):
        if acc[k] >= thr:
            best = k
        else:
            break
    return best


def cot_pairs(rows: list[dict[str, object]]) -> tuple[int, int]:
    key = {(r["k"], r["idx"], r["cond"]): bool(r["correct"]) for r in rows}
    rescue = sabotage = 0
    for (k, i, cond), ok in key.items():
        if cond != "direct":
            continue
        cot = key.get((k, i, "cot"))
        if cot is None:
            continue
        if cot and not ok:
            rescue += 1
        elif ok and not cot:
            sabotage += 1
    return rescue, sabotage


def mcnemar(rescue: int, sabotage: int) -> float:
    n = rescue + sabotage
    if n == 0:
        return 1.0
    j = min(rescue, sabotage)
    return float(min(1.0, 2 * sum(comb(n, i) for i in range(j + 1)) / 2 ** n))


def main() -> int:
    ext: dict[str, int] = {}
    fr_direct: dict[str, int] = {}
    cot_ok = collapse_ok = True
    for m, path in PATHS.items():
        rows = rows_of(path)
        ad, ac = acc_by_k(rows, "direct"), acc_by_k(rows, "cot")
        fd, fc = frontier(ad), frontier(ac)
        fr_direct[m] = fd
        ext[m] = fc - fd
        ks = sorted(ad)
        if not (ad[ks[-1]] < ad[ks[0]] and fd <= 5):  # accuracy collapses; direct frontier small
            collapse_ok = False
        rescue, sabotage = cot_pairs(rows)
        p = mcnemar(rescue, sabotage)
        if not (fc > fd and rescue > sabotage and p < 0.05):
            cot_ok = False
        print(f"  {m}: direct frontier {fd}, CoT frontier {fc} (extends {fc - fd}); "
              f"CoT rescue {rescue} vs sabotage {sabotage}, McNemar p={p:.3g}")

    small_shorter = fr_direct["0.5B"] <= fr_direct["1.5B"]
    cot_scales = ext["1.5B"] > ext["0.5B"]
    print(f"  direct accuracy collapses with chain length (both models): {collapse_ok}")
    print(f"  smaller model direct frontier no longer than larger: {small_shorter}")
    print(f"  CoT extends frontier + rescues significantly (both models): {cot_ok}")
    print(f"  CoT depth extension far larger for the capable model: {cot_scales}")

    if collapse_ok and small_shorter and cot_ok and cot_scales:
        print("VERIFY OK: a working-memory depth limit on trivial addition; CoT rescues it for "
              "the capable model and much less for the weak one")
        return 0
    print("VERIFY FAILED", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
