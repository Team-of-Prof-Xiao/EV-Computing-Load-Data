"""Inspect the ChargePlace Scotland workbooks (Strathclyde, CC BY 4.0) with the standard library and numpy.

Usage:
  python3 -I scripts/inspect_scotland.py DATA_DIR --peek   # sheets, size, header and first rows of every workbook
  python3 -I scripts/inspect_scotland.py DATA_DIR          # sessions: coverage, cleaning, charger types, dwell, flexibility
DATA_DIR is data/chargeplace_scotland. An .xlsx file is zipped XML, so it is read
directly; no spreadsheet package and none of the authors' code (code_KD_Dec24.py) is used.
Session columns: CPID, Consumed(kWh), Duration (fraction of a day), Start (date serial), Time (start time of day), Amount.
"""
import re
import sys
import zipfile
import datetime as dt
import xml.etree.ElementTree as ET
from array import array
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
RNS = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
BUILTIN_FMT = {14: 'm/d/yyyy', 15: 'd-mmm-yy', 16: 'd-mmm', 17: 'mmm-yy', 18: 'h:mm AM/PM', 19: 'h:mm:ss AM/PM',
               20: 'h:mm', 21: 'h:mm:ss', 22: 'm/d/yyyy h:mm', 45: 'mm:ss', 46: '[h]:mm:ss', 47: 'mmss.0'}
MONTHS = {m: i + 1 for i, m in enumerate(('jan', 'feb', 'mar', 'apr', 'may', 'jun',
                                          'jul', 'aug', 'sep', 'oct', 'nov', 'dec'))}
REQUIRED = ('CPID', 'Consumed(kWh)', 'Duration', 'Start', 'Time')
AC_TOP_KW = (7.4, 11.0, 22.0)  # candidate top rates of an AC session (car-side limit); set the shortest charge and laxity
TIMEDELTA = re.compile(r'(?:(\d+) days?, )?(\d+):(\d{2}):(\d{2})')


def col_index(ref):
    n = 0
    for ch in ref:
        if not ch.isalpha():
            break
        n = n * 26 + ord(ch.upper()) - 64
    return n - 1


class Workbook:
    def __init__(self, path):
        self.z = zipfile.ZipFile(path)
        names = set(self.z.namelist())
        wb = ET.fromstring(self.z.read('xl/workbook.xml'))
        rels = ET.fromstring(self.z.read('xl/_rels/workbook.xml.rels'))
        target = {r.get('Id'): r.get('Target') for r in rels}
        self.sheets = []
        for s in wb.iter(NS + 'sheet'):
            t = target[s.get(RNS + 'id')]
            self.sheets.append((s.get('name'), t.lstrip('/') if t.startswith('/') else 'xl/' + t))
        self.epoch = dt.datetime(1904, 1, 1) if any(
            p.get('date1904') in ('1', 'true') for p in wb.iter(NS + 'workbookPr')) else dt.datetime(1899, 12, 30)
        self.sst = []
        if 'xl/sharedStrings.xml' in names:
            for _, el in ET.iterparse(self.z.open('xl/sharedStrings.xml')):
                if el.tag == NS + 'si':
                    self.sst.append(''.join(t.text or '' for t in el.iter(NS + 't')))
                    el.clear()
        # cell style index -> number format code, to tell dates and times from plain numbers
        self.fmt = []
        if 'xl/styles.xml' in names:
            st = ET.fromstring(self.z.read('xl/styles.xml'))
            custom = {int(f.get('numFmtId')): f.get('formatCode') for f in st.iter(NS + 'numFmt')}
            xfs = st.find(NS + 'cellXfs')
            for xf in (xfs if xfs is not None else []):
                i = int(xf.get('numFmtId', 0))
                self.fmt.append(custom.get(i, BUILTIN_FMT.get(i, 'General' if i == 0 else f'builtin {i}')))

    def dimension(self, sheet_path):
        for _, el in ET.iterparse(self.z.open(sheet_path)):
            if el.tag == NS + 'dimension':
                return el.get('ref')
            if el.tag == NS + 'row':
                return None

    def rows(self, sheet_path, with_format=False):
        """Yield each row as a list; numbers stay floats, shared strings become str."""
        for _, el in ET.iterparse(self.z.open(sheet_path)):
            if el.tag != NS + 'row':
                continue
            vals, fmts, k = {}, {}, -1
            for c in el.iter(NS + 'c'):
                r = c.get('r')
                k = col_index(r) if r else k + 1
                t, v = c.get('t'), c.find(NS + 'v')
                if t == 'inlineStr':
                    x = ''.join(tt.text or '' for tt in c.iter(NS + 't'))
                elif v is None:
                    continue
                elif t == 's':
                    x = self.sst[int(v.text)]
                elif t in ('str', 'e', 'd'):
                    x = v.text
                elif t == 'b':
                    x = v.text == '1'
                else:
                    x = float(v.text)
                vals[k] = x
                s = int(c.get('s', 0))
                fmts[k] = self.fmt[s] if s < len(self.fmt) else 'General'
            el.clear()
            width = max(vals) + 1 if vals else 0
            row = [vals.get(i) for i in range(width)]
            yield (row, [fmts.get(i) for i in range(width)]) if with_format else row


def peek(root):
    for path in sorted(p for p in root.rglob('*.xlsx') if not p.name.startswith('~$')):
        wb = Workbook(path)
        print(f'\n=== {path.relative_to(root)}  sheets={[n for n, _ in wb.sheets]}  epoch={wb.epoch.date()}')
        for name, sp in wb.sheets:
            print(f'  [{name}] dimension={wb.dimension(sp)}')
            for i, (row, fmts) in enumerate(wb.rows(sp, with_format=True)):
                if i == 0:
                    print('   header:', row)
                else:
                    print('   row', i, list(zip(row, fmts)))
                if i == 2:
                    break


def file_month(path):
    m = re.fullmatch(r'([A-Za-z]+)-?(\d{2}|\d{4})', path.stem)
    year = int(m.group(2))
    return (year if year > 99 else 2000 + year), MONTHS[m.group(1)[:3].lower()]


def cpid_key(x):
    if isinstance(x, float) and x.is_integer():
        return str(int(x))
    return None if x is None else str(x).strip()


def duration_days(x):
    """Duration cell as a fraction of a day; OCT-23 stores sessions over 24 h as text such as '1 day, 8:37:17'."""
    if isinstance(x, float):
        return x
    m = TIMEDELTA.fullmatch(x.strip()) if isinstance(x, str) else None
    if m is None:
        return None
    d, h, mi, s = (int(g or 0) for g in m.groups())
    return d + (h * 3600 + mi * 60 + s) / 86400


def cpid_table(root, name):
    wb = Workbook(root / 'CPID_information' / name)
    it = wb.rows(wb.sheets[0][1])
    next(it)
    return {cpid_key(r[0]): r[1] for r in it if len(r) > 1 and r[0] is not None}


def q(x, ps=(5, 25, 50, 75, 95, 99)):
    return ' '.join(f'p{p}={v:.2f}' for p, v in zip(ps, np.percentile(x, ps))) if len(x) else 'empty'


def profile(hours):
    """Share of arrivals in each clock hour, in percent."""
    h = np.bincount(hours, minlength=24)[:24]
    return ' '.join(f'{v:.1f}' for v in 100 * h / max(h.sum(), 1))


def load_sessions(root):
    codes = {}
    cp, t0, dur, kwh, amt, src = array('i'), array('d'), array('d'), array('d'), array('d'), array('b')
    keys = array('q')
    files = sorted((root / 'Sessions_from_CPS').glob('*.xlsx'), key=file_month)
    print('file             month    rows    kept  start-has-fraction  text durations parsed  non-numeric cells (example)')
    for fi, path in enumerate(files):
        wb = Workbook(path)
        it = wb.rows(wb.sheets[0][1])
        header = next(it)
        col = [header.index(c) for c in REQUIRED]
        ia = header.index('Amount') if 'Amount' in header else None
        rows = kept = frac = text_dur = 0
        bad, example = Counter(), {}
        for r in it:
            rows += 1
            v = [r[i] if i < len(r) else None for i in col]
            raw_dur, v[2] = v[2], duration_days(v[2])
            text_dur += isinstance(raw_dur, str) and v[2] is not None
            if v[0] is None or not all(isinstance(x, float) for x in v[1:]):
                for name, x in zip(REQUIRED, v):
                    if (name == 'CPID' and x is None) or (name != 'CPID' and not isinstance(x, float)):
                        bad[name] += 1
                        example.setdefault(name, raw_dur if name == 'Duration' else x)
                continue
            a = r[ia] if ia is not None and ia < len(r) and isinstance(r[ia], float) else float('nan')
            k = cpid_key(v[0])
            s = v[3] + v[4]
            frac += v[3] != int(v[3])
            cp.append(codes.setdefault(k, len(codes)))
            t0.append(s)
            dur.append(v[2])
            kwh.append(v[1])
            amt.append(a)
            src.append(fi)
            keys.append(hash((k, round(s * 86400), round(v[2] * 86400), v[1])))
            kept += 1
        y, m = file_month(path)
        print(f'{path.name:16s} {y}-{m:02d} {rows:7d} {kept:7d} {frac:19d} {text_dur:22d}  {dict(bad)} {example}')
    names = [None] * len(codes)
    for k, c in codes.items():
        names[c] = k
    return dict(cp=np.frombuffer(cp, dtype=np.int32), t0=np.frombuffer(t0), dur_h=24 * np.frombuffer(dur),
                kwh=np.frombuffer(kwh), amt=np.frombuffer(amt), src=np.frombuffer(src, dtype=np.int8),
                keys=np.frombuffer(keys, dtype=np.int64), names=names, files=files)


def summarize(root):
    S = load_sessions(root)
    n = len(S['t0'])
    epoch = dt.date(1899, 12, 30)
    day = np.floor(S['t0']).astype(np.int64)
    udays, inv = np.unique(day, return_inverse=True)
    dates = [epoch + dt.timedelta(days=int(d)) for d in udays]
    ym = np.array([d.year * 12 + d.month - 1 for d in dates])[inv]
    file_ym = np.array([y * 12 + m - 1 for y, m in map(file_month, S['files'])])[S['src']]
    _, first = np.unique(S['keys'], return_index=True)
    print(f'\nsessions read {n}; exact duplicates (same CPID, start, duration, energy) {n - len(first)}; '
          f'start outside the file month {int((ym != file_ym).sum())}')
    keep = np.zeros(n, bool)
    keep[first] = True

    dur_h, kwh = S['dur_h'], S['kwh']
    with np.errstate(divide='ignore', invalid='ignore'):
        kw = np.where(dur_h > 0, kwh / dur_h, np.inf)
    rules = {'duration < 1 min': dur_h < 1 / 60, 'energy < 0.1 kWh': kwh < 0.1, 'duration > 72 h': dur_h > 72,
             'mean power > 350 kW': kw > 350}
    for name, m in rules.items():
        print(f'  drop {name}: {int((m & keep).sum())} ({100 * (m & keep).sum() / n:.1f}%)')
        keep &= ~m
    print(f'  duration > 24 h among kept: {int((keep & (dur_h > 24)).sum())}; clean sessions {int(keep.sum())}')

    span = (dates[-1] - dates[0]).days + 1
    per_day = np.bincount(inv[keep], minlength=len(udays))
    print(f'\ncoverage {dates[0]} .. {dates[-1]}: {span} days, {len(udays)} with sessions, '
          f'distinct CPIDs {len(np.unique(S["cp"][keep]))}')
    print('clean sessions per day:', q(per_day, (5, 50, 95)), f'mean={per_day.mean():.0f}')
    missing, gaps = np.setdiff1d(np.arange(udays[0], udays[-1] + 1), np.unique(day[keep])), []
    for d in missing:
        if gaps and d == gaps[-1][1] + 1:
            gaps[-1][1] = d
        else:
            gaps.append([d, d])
    print(f'days without clean sessions ({len(missing)}):', ', '.join(
        str(epoch + dt.timedelta(days=int(a))) + (f'..{epoch + dt.timedelta(days=int(b))}' if b > a else '')
        for a, b in gaps) or 'none')
    by_month = Counter(ym[keep].tolist())
    print('clean sessions per month:', ' '.join(f'{k // 12}-{k % 12 + 1:02d}:{v}' for k, v in sorted(by_month.items())))

    speed = cpid_table(root, 'CPID_and_charger_speed.xlsx')
    la = cpid_table(root, 'CPID_and_local_authority.xlsx')
    pc = cpid_table(root, 'CPID_and_postcode.xlsx')
    types = sorted(set(map(str, speed.values())))
    tcode = np.array([types.index(str(speed[k])) if k in speed else -1 for k in S['names']])[S['cp']]
    weekday = (day + 5) % 7  # serial 0 is a Saturday; Monday = 0
    hour = np.minimum((24 * (S['t0'] - day)).astype(int), 23)
    print(f'\ncharger types in CPID_and_charger_speed: {Counter(map(str, speed.values()))}')
    for code, name in [(i, t) for i, t in enumerate(types)] + [(-1, 'unknown CPID')]:
        m = keep & (tcode == code)
        if not m.any():
            continue
        print(f'\n[{name}] sessions {int(m.sum())} ({100 * m.sum() / keep.sum():.1f}%), '
              f'CPIDs {len(np.unique(S["cp"][m]))}, {m.sum() / span:.0f} sessions/day, '
              f'{kwh[m].sum() / span / 1e3:.1f} MWh/day, free sessions {100 * np.mean(S["amt"][m] == 0):.0f}%')
        print('  dwell h:', q(dur_h[m]))
        print('  energy kWh:', q(kwh[m]))
        print('  mean kW:', q(kw[m]))
        print(f'  dwell >= 4 h {100 * np.mean(dur_h[m] >= 4):.1f}%, >= 8 h {100 * np.mean(dur_h[m] >= 8):.1f}%')
        print('  weekday arrivals by hour %:', profile(hour[m & (weekday < 5)]))
        print('  weekend arrivals by hour %:', profile(hour[m & (weekday >= 5)]))

    ac = keep & (tcode == types.index('AC')) if 'AC' in types else np.zeros(n, bool)
    if ac.any():
        print(f'\nAC flexibility; mean power above 7.4 kW in {100 * np.mean(kw[ac] > 7.4):.1f}% of AC sessions, '
              f'so the top rate is max(candidate, observed mean power):')
        for top in AC_TOP_KW:
            lax = dur_h[ac] - kwh[ac] / np.maximum(top, kw[ac])
            print(f'  top {top:4.1f} kW: laxity h', q(lax, (25, 50, 75, 95)),
                  f'| >= 1 h {100 * np.mean(lax >= 1):.1f}%, >= 3 h {100 * np.mean(lax >= 3):.1f}%')
        work = ac & (weekday < 5) & (hour >= 6) & (hour < 10) & (dur_h >= 4)
        weekdays = int(np.sum((np.unique(day[keep]) + 5) % 7 < 5))
        print(f'  workplace-like AC sessions (weekday arrival 6-10 h, dwell >= 4 h): {int(work.sum())} '
              f'({100 * work.sum() / ac.sum():.1f}% of AC), {work.sum() / weekdays:.0f} per weekday')
        print('    dwell h:', q(dur_h[work], (5, 50, 95)), '| energy kWh:', q(kwh[work], (5, 50, 95)),
              '| departure clock h:', q((24 * (S['t0'] - day) + dur_h)[work], (10, 50, 90)),
              '| laxity at max(11 kW, mean) h:', q(dur_h[work] - kwh[work] / np.maximum(11, kw[work]), (25, 50, 75)))
        long = ac & (dur_h >= 8)
        print('  arrivals of AC sessions with dwell >= 8 h, weekday %:', profile(hour[long & (weekday < 5)]))
        daily = np.bincount(inv[ac], weights=kwh[ac], minlength=len(udays))
        d = daily - daily.mean()
        print(f'  daily AC energy: mean {daily.mean() / 1e3:.1f} MWh, lag-7 autocorrelation '
              f'{np.dot(d[7:], d[:-7]) / np.dot(d, d):.2f}, lag-1 {np.dot(d[1:], d[:-1]) / np.dot(d, d):.2f}')

        for label, table in (('local authority', la), ('postcode (site)', pc)):
            groups = defaultdict(list)
            idx = np.flatnonzero(ac)
            gname = np.array([str(table.get(k, '?')) for k in S['names']], dtype=object)[S['cp'][idx]]
            for g, i in zip(gname, idx):
                groups[g].append(i)
            top = sorted(groups.items(), key=lambda kv: -len(kv[1]))[:10]
            print(f'\n  AC by {label}, top 10: name | CPIDs | sessions/day | median dwell h | dwell >= 8 h % | '
                  f'weekday arrivals 6-10 h %')
            for g, ii in top:
                ii = np.array(ii)
                wk = weekday[ii] < 5
                print(f'    {g:28s} {len(np.unique(S["cp"][ii])):4d} {len(ii) / span:7.1f} '
                      f'{np.median(dur_h[ii]):6.2f} {100 * np.mean(dur_h[ii] >= 8):6.1f} '
                      f'{100 * np.mean(wk & (hour[ii] >= 6) & (hour[ii] < 10)) / max(np.mean(wk), 1e-9):6.1f}')


if __name__ == '__main__':
    root = Path(sys.argv[1])
    if '--peek' in sys.argv:
        peek(root)
    else:
        summarize(root)
