"""Summarize the Alibaba cluster-trace-v2026-spot-gpu job and node tables.

Usage: python3 -I scripts/inspect_spot_gpu.py data/alibaba_spot_gpu_v2026
Prints the span of the trace, high-priority (HP) versus Spot job counts and GPU-hours, duration quantiles,
and the hourly number of GPUs in use by type, with its 24 h and 168 h autocorrelation (submit times are
seconds from the first job, so the phase of the daily cycle is unknown).
"""
import csv
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

root = Path(sys.argv[1])
with open(root / 'job_info_df.csv', newline='') as f:
    jobs = list(csv.DictReader(f))
with open(root / 'node_info_df.csv', newline='') as f:
    nodes = list(csv.DictReader(f))

print('jobs:', len(jobs), '| columns:', list(jobs[0].keys()))
print('nodes:', len(nodes), '| GPUs:', sum(int(float(n['gpu_capacity_num'])) for n in nodes),
      '| models:', Counter(n['gpu_model'] for n in nodes).most_common())


def gpus(j):
    return float(j['gpu_request']) * float(j['worker_num'])


submit = [float(j['submit_time']) for j in jobs]
end = [float(j['submit_time']) + float(j['duration']) for j in jobs]
span_h = max(end) / 3600
print(f'submit_time 0 .. {max(submit) / 86400:.1f} days; last job ends at {span_h / 24:.1f} days')
print('jobs submitted at t=0 (running when the trace starts):', sum(s == 0 for s in submit))

for t in sorted({j['job_type'] for j in jobs}):
    sel = [j for j in jobs if j['job_type'] == t]
    dur = sorted(float(j['duration']) / 3600 for j in sel)
    gh = sum(gpus(j) * float(j['duration']) / 3600 for j in sel)
    q = lambda p: dur[min(len(dur) - 1, int(p * len(dur)))]
    print(f'{t}: {len(sel)} jobs, {gh:,.0f} GPU-hours; duration h p10/p50/p90/p99 = '
          f'{q(.1):.2f}/{q(.5):.2f}/{q(.9):.2f}/{q(.99):.1f}; GPUs per job p50/p90 = '
          f'{sorted(gpus(j) for j in sel)[len(sel) // 2]:.0f}/{sorted(gpus(j) for j in sel)[int(.9 * len(sel))]:.0f}')

# hourly GPUs in use by type, from the start of the trace to the last submission
H = int(math.ceil(max(submit) / 3600)) + 1
use = defaultdict(lambda: [0.0] * H)
for j, s, e in zip(jobs, submit, end):
    g = gpus(j)
    for h in range(int(s // 3600), min(H, int(math.ceil(e / 3600)))):
        lo, hi = max(s, h * 3600), min(e, (h + 1) * 3600)
        if hi > lo:
            use[j['job_type']][h] += g * (hi - lo) / 3600


def acf(x, lag):
    n = len(x) - lag
    if n < 2:
        return float('nan')
    m = sum(x) / len(x)
    v = sum((a - m) ** 2 for a in x)
    return sum((x[i] - m) * (x[i + lag] - m) for i in range(n)) / v if v else float('nan')


for t, x in sorted(use.items()):
    s = sorted(x)
    print(f'GPUs in use, {t}: mean {sum(x) / H:,.0f}, p10 {s[int(.1 * H)]:,.0f}, p90 {s[int(.9 * H)]:,.0f}; '
          f'ACF 24 h {acf(x, 24):.2f}, 168 h {acf(x, 168):.2f}')

# submissions per hour of (relative) day, Spot vs HP
for t in sorted({j['job_type'] for j in jobs}):
    c = Counter(int((float(j['submit_time']) % 86400) // 3600) for j in jobs if j['job_type'] == t
                and float(j['submit_time']) > 0)
    print(f'{t} submissions by relative hour: ' + ' '.join(str(c.get(h, 0)) for h in range(24)))
