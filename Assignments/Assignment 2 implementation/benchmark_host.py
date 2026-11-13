#!/usr/bin/env python3
import argparse, json, platform, statistics, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description="Host-only CPU loop timing; not a hypervisor comparison.")
parser.add_argument("--iterations", type=int, default=2000000)
parser.add_argument("--repeats", type=int, default=3)
args = parser.parse_args()
if args.iterations < 1 or args.repeats < 1:
    parser.error("iterations and repeats must be positive")
times, checksum = [], 0
for _ in range(args.repeats):
    start = time.perf_counter()
    value = 0
    for i in range(args.iterations):
        value = (value + (i % 97) * (i % 89)) % 1000003
    times.append(time.perf_counter() - start)
    checksum = value
result = {
    "test": "Python integer-loop timing",
    "purpose": "Host-level timing only; not a KVM/Docker/Kata comparison",
    "platform": platform.platform(), "iterations": args.iterations,
    "repeats": args.repeats, "durations_seconds": times,
    "median_seconds": statistics.median(times), "checksum": checksum,
    "warning": "Do not use this result to claim virtualization overhead."
}
out = ROOT / "results"
out.mkdir(exist_ok=True)
(out / "host_microbenchmark.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
