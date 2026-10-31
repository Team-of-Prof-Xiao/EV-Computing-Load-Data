"""Summarize app_metrics.csv from the Alibaba cluster-trace-v2026-maas archive, read directly from the zip.

Usage: python3 -I scripts/inspect_alibaba_app_metrics.py data/alibaba_maas_v2026/app_metrics.csv.zip
"""
import csv
import io
import sys
import zipfile
from collections import Counter, defaultdict

path = sys.argv[1]
with zipfile.ZipFile(path) as z:
    names = z.namelist()
    print('members:', names)
    with z.open('app_metrics.csv') as f:
        rows = list(csv.DictReader(io.TextIOWrapper(f, encoding='utf-8')))

print('rows:', len(rows), '| columns:', list(rows[0].keys()))
times = sorted({float(r['time_s']) for r in rows if r['time_s']})
print(f'time_s: {len(times)} distinct, from {times[0]:.0f} to {times[-1]:.0f} s '
      f'({(times[-1] - times[0]) / 3600:.1f} h); step {times[1] - times[0]:.0f} s')
print('apps:', len({r['app_id'] for r in rows}), '| series:', len({r['series_id'] for r in rows}))
print('metrics:', Counter(r['metric'] for r in rows).most_common())
print('pd_role:', Counter(r['pd_role'] for r in rows).most_common())
print('gpu_type:', Counter(r['gpu_type'] for r in rows).most_common(8))

# total normalized QPS per hour across apps, to see the daily cycle
qps = defaultdict(float)
for r in rows:
    if r['metric'] == 'qps_norm' and r['value'] not in ('', 'NULL'):
        qps[float(r['time_s'])] += float(r['value'])
hours = sorted(qps)
print('qps_norm summed over apps, first 30 hours:')
print('  ' + ' '.join(f'{qps[h]:.2f}' for h in hours[:30]))
