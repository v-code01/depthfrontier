"""Sweep exact accuracy on chained single-digit additions over chain length k and condition
(direct answer vs chain-of-thought), for one model. Chains are generated deterministically per
k, so every model and condition sees identical problems and CoT-vs-direct is paired. Ground
truth is the Python sum; the model output is parsed to its final integer. Because the terms are
single digits, a wrong answer is a tracking failure, not an arithmetic one. No judge. Writes
results/<model>.jsonl.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from depth import chain_sum, correct, gen_chain, parse_int  # noqa: E402

_SYS = {
    "direct": "Compute the exact result and reply with only the final integer, nothing else.",
    "cot": ("You are a calculator. Think step by step, then write the final result on the "
            "last line as just the number."),
}
_MAXTOK = {"direct": 16, "cot": 384}


def ask(url: str, model: str, cond: str, terms: list[int]) -> int | None:
    question = " + ".join(str(t) for t in terms) + " = ?"
    payload = json.dumps({"model": model,
                          "messages": [{"role": "system", "content": _SYS[cond]},
                                       {"role": "user", "content": question}],
                          "temperature": 0.0, "max_tokens": _MAXTOK[cond], "seed": 1}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            j = json.loads(r.read())
        return parse_int(str(j["choices"][0]["message"]["content"]))
    except Exception:  # noqa: BLE001
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", default="8081")
    ap.add_argument("--model", default="qwen-dp")
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--ks", default="2,3,4,6,8,10,12,16")
    ap.add_argument("--seed", type=int, default=20260708)
    ap.add_argument("--concurrency", type=int, default=6)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    url = f"http://127.0.0.1:{args.port}/v1/chat/completions"
    ks = [int(x) for x in args.ks.split(",")]
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    jobs = []
    for k in ks:
        for i, terms in enumerate(gen_chain(k, args.n, args.seed)):
            for cond in ("direct", "cot"):
                jobs.append((k, cond, i, terms))

    def run(job: tuple[int, str, int, list[int]]) -> dict[str, object]:
        k, cond, i, terms = job
        gold = chain_sum(terms)
        pred = ask(url, args.model, cond, terms)
        return {"model": args.model, "k": k, "cond": cond, "idx": i,
                "terms": terms, "gold": gold, "pred": pred, "correct": correct(pred, gold)}

    with ThreadPoolExecutor(max_workers=args.concurrency) as pool, \
            open(args.out, "w", buffering=1) as out:
        for c, row in enumerate(pool.map(run, jobs)):
            out.write(json.dumps(row) + "\n")
            if (c + 1) % 100 == 0:
                print(f"  {args.model} {c + 1}/{len(jobs)}", flush=True)
    print(f"# SWEEP_DONE {args.model}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
