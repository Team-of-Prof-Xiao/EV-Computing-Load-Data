"""Summarize the Utrecht office parking-lot EV sessions (4TU, DOI 10.4121/80ef3824-3f5d-4e45-8794-3b8791efbd13, v2).

Usage: python3 -I scripts/inspect_utrecht.py data/utrecht_office_ev/202410DatasetEVOfficeParking_v0.csv
The file is semicolon-separated UTF-8 with a byte-order mark; times are local (Europe/Amsterdam).
Prints coverage, sessions per year and per weekday, dwell, energy, laxity and the arrival-hour profile.
"""
import csv
import sys
import datetime as dt
from collections import Counter

import numpy as np

TOP_KW = 11.0  # a double-plug 22 kW charger gives 11 kW per plug when both are in use (dataset README)


def q(x, ps=(5, 25, 50, 75, 95)):
    return ' '.join(f'p{p}={v:.2f}' for p, v in zip(ps, np.percentile(x, ps))) if len(x) else 'empty'


def profile(hours):
    h = np.bincount(hours, minlength=24)[:24]
    return ' '.join(f'{v:.1f}' for v in 100 * h / max(h.sum(), 1))


with open(sys.argv[1], encoding='utf-8-sig', newline='') as f:
    rows = list(csv.DictReader(f, delimiter=';'))
print('columns:', list(rows[0]))
print('rows:', len(rows))
empty = {k: sum(1 for r in rows if not r[k].strip()) for k in rows[0]}
print('empty cells per column:', empty)

fmt = '%Y-%m-%d %H:%M:%S'
start = [dt.datetime.strptime(r['start_datetime'], fmt) for r in rows]
end = [dt.datetime.strptime(r['end_datetime'], fmt) for r in rows]
kwh = np.array([float(r['total_energy']) for r in rows])
dwell = np.array([(e - s).total_seconds() / 3600 for s, e in zip(start, end)])
hour = np.array([s.hour for s in start])
weekday = np.array([s.weekday() for s in start])
year = np.array([s.year for s in start])
days = sorted({s.date() for s in start})
print(f'coverage {min(start)} .. {max(end)}; days with sessions {len(days)} of '
      f'{(days[-1] - days[0]).days + 1}; distinct EV ids {len({r["EV_id_x"] for r in rows})}')
print('sessions per year:', dict(sorted(Counter(year.tolist()).items())))
for y in sorted(set(year.tolist())):
    m = year == y
    wd = sorted({s.date() for s, k in zip(start, m) if k and s.weekday() < 5})
    print(f'  {y}: {int(m.sum())} sessions, {np.sum(m & (weekday < 5)) / max(len(wd), 1):.1f} per working weekday '
          f'with sessions, weekend share {100 * np.mean(weekday[m] >= 5):.1f}%, '
          f'charge points used {len({rows[i]["evse_uid"] + rows[i]["channel"] for i in np.flatnonzero(m)})}')
print('sessions by weekday Mon..Sun:', np.bincount(weekday, minlength=7).tolist())
print('dwell h:', q(dwell), '| energy kWh:', q(kwh), '| mean kW:', q(kwh / dwell))
lax = dwell - kwh / np.maximum(TOP_KW, kwh / dwell)
print(f'laxity at max({TOP_KW:.0f} kW, mean) h:', q(lax, (25, 50, 75, 95)),
      f'| >= 1 h {100 * np.mean(lax >= 1):.1f}%, >= 3 h {100 * np.mean(lax >= 3):.1f}%')
print('weekday arrivals by hour %:', profile(hour[weekday < 5]))
print('departure clock h (weekday):', q((hour + np.array([s.minute / 60 for s in start]) + dwell)[weekday < 5], (10, 50, 90)))
recent = year >= 2022
print(f'2022 onwards: {int(recent.sum())} sessions; dwell h', q(dwell[recent], (5, 50, 95)),
      '| energy kWh', q(kwh[recent], (5, 50, 95)), '| laxity h', q(lax[recent], (25, 50, 75)))
print('rails:', Counter(r['rail'] for r in rows).most_common(12))
