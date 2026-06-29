#!/usr/bin/env bash
# Regenerate the chained-addition depth sweep for both models.
# Usage: ./reproduce.sh PORT_15B PORT_05B
set -euo pipefail
cd "$(dirname "$0")"
P15="${1:-8081}"; P05="${2:-8082}"
. .venv/bin/activate
python tools/run_sweep.py --port "$P15" --model qwen-dp   --n 40 --ks 2,3,4,6,8,10,12,16 --out results/dp_15b.jsonl
python tools/run_sweep.py --port "$P05" --model qwen-dp05 --n 40 --ks 2,3,4,6,8,10,12,16 --out results/dp_05b.jsonl
python tools/analyze.py
python tools/verify.py
echo "regenerated results; see bench_results/frontier.md"
