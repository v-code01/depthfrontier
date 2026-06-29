"""Derive the depth frontier for each (model, condition): accuracy by chain length k, the
frontier (longest chain summed at >=0.5, contiguous from the shortest up), how much
chain-of-thought extends the frontier over direct answering, and an exact paired McNemar test
of CoT vs direct on identical chains. Writes bench_results/frontier.md and curve.json. Pure
derivation from results/*.jsonl; no model calls.
"""
from __future__ import annotations

import json
import math
import os
import sys
from typing import TypedDict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from depth import frontier  # noqa: E402

MODELS = [("1.5B", "results/dp_15b.jsonl"), ("0.5B", "results/dp_05b.jsonl")]
CONDS = ["direct", "cot"]
THRESH = 0.5


class Row(TypedDict):
    model: str
    k: int
    cond: str
    idx: int
    correct: bool


def load(path: str) -> list[Row]:
    return [json.loads(x) for x in open(path) if x.strip()]


def mcnemar_p(rescue: int, sabotage: int) -> float:
    n = rescue + sabotage
    if n == 0:
        return 1.0
    j = min(rescue, sabotage)
    return float(min(1.0, 2 * sum(math.comb(n, i) for i in range(j + 1)) / 2 ** n))


def acc_by_k(rows: list[Row], cond: str) -> dict[int, float]:
    out: dict[int, float] = {}
    for k in sorted({r["k"] for r in rows}):
        sub = [r for r in rows if r["cond"] == cond and r["k"] == k]
        if sub:
            out[k] = sum(1 for r in sub if r["correct"]) / len(sub)
    return out


def analyze_model(label: str, rows: list[Row]) -> dict[str, object]:
    accs = {cond: acc_by_k(rows, cond) for cond in CONDS}
    fronts = {cond: frontier(accs[cond], THRESH) for cond in CONDS}
    key = {(r["k"], r["idx"], r["cond"]): r["correct"] for r in rows}
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
    return {
        "label": label,
        "acc": {cond: {str(k): accs[cond][k] for k in accs[cond]} for cond in CONDS},
        "frontier": fronts, "cot_extends": fronts["cot"] - fronts["direct"],
        "cot_rescue": rescue, "cot_sabotage": sabotage,
        "mcnemar_cot_vs_direct": mcnemar_p(rescue, sabotage),
    }


def render(r: dict[str, object]) -> list[str]:
    acc = r["acc"]
    fr = r["frontier"]
    assert isinstance(acc, dict) and isinstance(fr, dict)
    ks = sorted({int(k) for cell in acc.values() for k in cell})
    lines = [f"## {r['label']}", "", "  cond     " + "".join(f"k={k:<4}" for k in ks) + " frontier"]
    for cond in CONDS:
        cell = acc[cond]
        row = f"  {cond:<7}  " + "".join(f"{cell.get(str(k), float('nan')):.2f}  " for k in ks)
        lines.append(row + f"  {fr[cond]}")
    lines += ["",
              f"- CoT extends the depth frontier by {r['cot_extends']} term(s) "
              f"({fr['direct']} -> {fr['cot']})",
              f"- CoT vs direct (paired): rescue {r['cot_rescue']} vs sabotage "
              f"{r['cot_sabotage']}, McNemar p={r['mcnemar_cot_vs_direct']:.4g}", ""]
    return lines


def main() -> int:
    results = []
    for label, path in MODELS:
        if not os.path.exists(path):
            print(f"MISSING {path}", file=sys.stderr)
            return 1
        results.append(analyze_model(label, load(path)))
    os.makedirs("bench_results", exist_ok=True)
    with open("bench_results/curve.json", "w") as f:
        json.dump(results, f, indent=2)
    lines = ["# depthfrontier: how long a chain of trivial additions can a model track?", "",
             "Chains of single-digit addends (deterministic per length, identical across models",
             "and conditions). Per-step arithmetic is trivial, so a wrong sum is a tracking",
             "failure, not a computation one. Frontier = longest chain summed at >=0.5 accuracy,",
             "contiguous from the shortest up. direct vs chain-of-thought.", ""]
    for r in results:
        lines += render(r)
    with open("bench_results/frontier.md", "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
