"""Extract ERCOT day-ahead wind/solar forecasts and revised actual generation (2024-2025 by default).

Usage: python3 -I scripts/extract_ercot_forecasts.py INPUT_DIRECTORY
           [--start YYYY-MM-DD] [--end YYYY-MM-DD] [--out CSV] [--summary TXT]
Read nested monthly ZIPs in memory, select the last previous-day release by 10:00,
and check coverage, DST hour-ending alignment, and agreement with local EIA-930 CSVs.
Partial boundary days in the rolling reports use ranks in the complete delivery day.
--start/--end are operating days; --out and --summary are relative to the project root.
"""
import csv
import io
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
START, END = date(2024, 1, 1), date(2025, 12, 31)
COVER_START = date(2023, 12, 31)
TIME_FMT = '%Y-%m-%d %H:%M:%S'
EIA_FMT = '%m/%d/%Y %I:%M:%S %p'
MAX_MEMBER = 50 * 1024 * 1024
HOUR = timedelta(hours=1)
DAY = timedelta(days=1)
PRODUCTS = {'wind': ('NP4-732-CD', 'STWPF', 'WGRPP'),
            'solar': ('NP4-737-CD', 'STPPF', 'PVGRPP')}
CSV_OUT = ROOT / 'data/ercot/ercot_dayahead_wind_solar_2024_2025.csv'
SUMMARY_OUT = ROOT / 'results/ercot_forecasts/summary.txt'
COLUMNS = ['time_utc_hour_ending', 'time_local_hour_ending', 'dst_flag',
           'wind_post_time_local', 'wind_stwpf_MW', 'wind_wgrpp_MW', 'wind_cop_hsl_MW',
           'solar_post_time_local', 'solar_stppf_MW', 'solar_pvgrpp_MW', 'solar_cop_hsl_MW',
           'wind_actual_MW', 'solar_actual_MW']
try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
except ImportError:
    CHICAGO = None
else:
    try:
        CHICAGO = ZoneInfo('America/Chicago')
    except ZoneInfoNotFoundError:
        CHICAGO = None


def dates(first, last):
    while first <= last:
        yield first
        first += DAY


@lru_cache(None)
def transitions(year):
    march, november = date(year, 3, 1), date(year, 11, 1)
    return (march + timedelta(days=(6 - march.weekday()) % 7 + 7),
            november + timedelta(days=(6 - november.weekday()) % 7))


@lru_cache(None)
def day_grid(d):
    spring, fall = transitions(d.year)
    keys = [(h, 'N') for h in range(1, 25) if not (d == spring and h == 3)]
    if d == fall:
        keys.append((2, 'Y'))
    keys.sort()
    midnight = datetime.combine(d, datetime.min.time())
    if CHICAGO is not None:
        utc = midnight.replace(tzinfo=CHICAGO).astimezone(timezone.utc).replace(tzinfo=None)
    else:
        utc = midnight + timedelta(hours=5 if spring < d <= fall else 6)
    return {key: (utc + k * HOUR, midnight + key[0] * HOUR)
            for k, key in enumerate(keys, 1)}


def read_member(z, member):
    if member.file_size > MAX_MEMBER:
        raise ValueError(f'ZIP member exceeds 50 MiB: {member.filename} ({member.file_size} bytes)')
    return z.read(member)


def headers(kind, new):
    _, short, regional = PRODUCTS[kind]
    fields = ['DELIVERY_DATE', 'HOUR_ENDING', 'SYSTEM_WIDE_GEN' if new else 'ACTUAL_SYSTEM_WIDE',
              'COP_HSL_SYSTEM_WIDE', short + '_SYSTEM_WIDE', regional + '_SYSTEM_WIDE']
    if kind == 'wind':
        for zone in ('SOUTH_HOUSTON', 'WEST', 'NORTH'):
            fields += [prefix + '_LZ_' + zone
                       for prefix in ('GEN' if new else 'ACTUAL', 'COP_HSL', short, regional)]
    return fields + (['SYSTEM_WIDE_HSL'] if new else []) + ['DSTFlag']


def number(value):
    value = value.strip()
    if not value:
        return None
    result = float(value)
    if not np.isfinite(result):
        raise ValueError(f'Non-finite value: {value!r}')
    return result


def inventory(folder, kind):
    releases = {}
    duplicates = 0
    for path in sorted((folder / kind).glob(PRODUCTS[kind][0] + '_*.zip')):
        with zipfile.ZipFile(path) as z:
            for m in z.infolist():
                if m.is_dir():
                    continue
                if m.file_size > MAX_MEMBER:
                    raise ValueError(f'ZIP member exceeds 50 MiB: {path}: {m.filename}')
                parts = Path(m.filename).name.split('.')
                if len(parts) != 8 or parts[-1] != 'zip':
                    raise ValueError(f'Unexpected release filename: {m.filename}')
                doc = int(parts[0])
                post = datetime.strptime(parts[4] + parts[5], '%Y%m%d%H%M%S')
                if doc in releases:
                    old = releases[doc]
                    if old[0] != post or old[3:] != (m.CRC, m.file_size):
                        raise ValueError(f'Conflicting duplicate docId: {doc}')
                    duplicates += 1
                else:
                    releases[doc] = (post, path, m.filename, m.CRC, m.file_size)
    if not releases:
        raise ValueError(f'No {kind} reports in {folder}')
    return releases, duplicates


def parse_report(payload, kind, label):
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        members = [m for m in z.infolist() if not m.is_dir()]
        if len(members) != 1 or not members[0].filename.lower().endswith('.csv'):
            raise ValueError(f'{label}: expected exactly one CSV')
        reader = csv.DictReader(io.StringIO(read_member(z, members[0]).decode('utf-8-sig')))
        fields = reader.fieldnames
        if fields is None or len(fields) != len(set(fields)) or not any(
                set(fields) == set(headers(kind, new)) for new in (False, True)):
            raise ValueError(f'{label}: unknown header {fields}')
        groups = defaultdict(dict)
        issues = []
        for r in reader:
            if None in r or any(v is None for v in r.values()):
                raise ValueError(f'{label}: malformed CSV row')
            d = parse_date(r['DELIVERY_DATE'])
            key = (int(r['HOUR_ENDING']), r['DSTFlag'].strip())
            allowed = key in day_grid(d) or (d == transitions(d.year)[0] and key == (3, 'N'))
            if not allowed or key in groups[d]:
                raise ValueError(f'{label}: invalid/duplicate hour {d} {key}')
            groups[d][key] = r
    if not groups:
        raise ValueError(f'{label}: empty CSV')
    first, last = min(groups), max(groups)
    issues += [f'missing delivery day {d}' for d in dates(first, last) if d not in groups]
    for d, rows in groups.items():
        if d == transitions(d.year)[0] and (3, 'N') in rows:
            if (2, 'N') in rows:
                raise ValueError(f'{label}: spring day contains both HE02 and HE03: {d}')
            rows[(2, 'N')] = rows.pop((3, 'N'))
            issues.append(f'{d}: spring HE03 label used instead of HE02; preserved sorted hour rank')
        expected = list(day_grid(d))
        actual = sorted(rows)
        if first < d < last:
            valid = actual == expected
        elif d == first and first != last:
            valid = actual == expected[-len(actual):]
        elif d == last and first != last:
            valid = actual == expected[:len(actual)]
        else:
            valid = actual == expected
        if not valid:
            issues.append(f'incomplete day {d}: {len(rows)}/{len(expected)} hours')
    return groups, 'SYSTEM_WIDE_GEN' if 'SYSTEM_WIDE_GEN' in fields else 'ACTUAL_SYSTEM_WIDE', issues


@lru_cache(None)
def parse_date(value):
    return datetime.strptime(value, '%m/%d/%Y').date()


def describe(items):
    return ', '.join(str(x) for x in items) or 'none'


def extract(folder, kind, manifest, lines):
    releases, duplicates = inventory(folder, kind)
    ordered = sorted(releases, key=lambda doc: (releases[doc][0], doc))
    daily, hourly = Counter(), defaultdict(list)
    selected = {}
    for doc in ordered:
        post = releases[doc][0]
        daily[post.date()] += 1
        hourly[post.replace(minute=0, second=0)].append(doc)
        d = post.date() + DAY
        if START <= d <= END and post.time() <= datetime.min.replace(hour=10).time():
            selected[d] = doc
    lines += [f'{kind}:', f'  Releases: {len(releases)} unique docIds; {duplicates} duplicate ZIP entries',
              f'  First / last: {releases[ordered[0]][0]:{TIME_FMT}} / {releases[ordered[-1]][0]:{TIME_FMT}}',
              '  Dates with no releases: ' + describe(d for d in dates(COVER_START, END) if not daily[d]),
              '  Non-24 release dates excluding DST transitions: ' + describe(
                  f'{d}={daily[d]}' for d in dates(COVER_START, END)
                  if daily[d] != 24 and d not in transitions(d.year)),
              '  DST release counts: ' + describe(f'{d}={daily[d]}' for y in range(START.year, END.year + 1)
                                                  for d in transitions(y) if START <= d <= END),
              '  Multiple releases in a local clock hour: ' + describe(
                  f'{t:{TIME_FMT}} [{" ".join(str(doc) for doc in docs)}]'
                  for t, docs in sorted(hourly.items()) if len(docs) > 1)]
    missing, extra = sorted(set(manifest) - set(releases)), sorted(set(releases) - set(manifest))
    mismatch = [doc for doc in ordered if doc in manifest and releases[doc][0] != manifest[doc]]
    lines += [f'  Manifest docIds match: {not missing and not extra}; manifest={len(manifest)}',
              '    Missing from ZIPs: ' + describe(missing), '    Absent from manifest: ' + describe(extra),
              '    Filename/manifest post-time mismatches: ' + describe(mismatch)]
    forecasts, actuals = {}, {}
    schema_counts = Counter()
    report_issues = []
    spring_labels = Counter()
    chosen = set(selected.values())
    open_path, outer = None, None
    try:
        for doc in ordered:
            post, path, name, _, _ = releases[doc]
            if path != open_path:
                if outer is not None:
                    outer.close()
                outer, open_path = zipfile.ZipFile(path), path
            groups, actual_col, issues = parse_report(read_member(outer, outer.getinfo(name)), kind, str(doc))
            schema_counts[actual_col] += 1
            for issue in issues:
                if 'spring HE03 label' in issue:
                    spring_labels[issue] += 1
                else:
                    report_issues.append(f'{doc} ({post:{TIME_FMT}}): {issue}')
            for d, rows in groups.items():
                if not START <= d <= END:
                    continue
                for key, r in rows.items():
                    value = number(r[actual_col])
                    if value is not None:
                        actuals[day_grid(d)[key][0]] = value
            if doc in chosen:
                d = post.date() + DAY
                if d not in groups or set(groups[d]) != set(day_grid(d)):
                    report_issues.append(f'{doc}: incomplete selected day-ahead day {d}; missing hours left empty')
                _, short, regional = PRODUCTS[kind]
                for key, r in groups.get(d, {}).items():
                    forecasts[day_grid(d)[key][0]] = (post, number(r[short + '_SYSTEM_WIDE']),
                                                     number(r[regional + '_SYSTEM_WIDE']),
                                                     number(r['COP_HSL_SYSTEM_WIDE']))
    finally:
        if outer is not None:
            outer.close()
    distribution = Counter(releases[doc][0].strftime('%H:%M') for doc in selected.values())
    lines += ['  Spring label variants: ' + describe(f'{issue} ({n} reports)'
                                                    for issue, n in sorted(spring_labels.items())),
              '  Report coverage anomalies:']
    lines += ['    ' + issue for issue in report_issues] or ['    none']
    lines += ['  Recognized schemas: ' + describe(f'{k}={v}' for k, v in sorted(schema_counts.items())),
              f'  Day-ahead days: {len(selected)} / {(END - START).days + 1}; selected hours: {len(forecasts)}',
              '  Selected release HH:MM distribution: ' + describe(f'{k}={v}' for k, v in sorted(distribution.items())),
              '  Missing day-ahead dates: ' + describe(d for d in dates(START, END) if d not in selected),
              f'  Nonempty actual hours: {len(actuals)} / {sum(len(day_grid(d)) for d in dates(START, END))}',
              '  Missing actual dates (hour counts): ' + describe(
                  f'{d}={sum(t not in actuals for t, _ in day_grid(d).values())}'
                  for d in dates(START, END) if any(t not in actuals for t, _ in day_grid(d).values())), '']
    return forecasts, actuals


def load_eia():
    result = {}
    for year in range(START.year, END.year + 1):
        with (ROOT / f'data/eia930/eia930_erco_{year}.csv').open(newline='') as f:
            for row in csv.DictReader(f):
                t = datetime.strptime(row['time_utc'].strip(), EIA_FMT)
                if t in result:
                    raise ValueError(f'Duplicate EIA UTC hour: {t}')
                result[t] = {kind: (number(row[kind]) or 0.0) + (number(row[kind + '_bat']) or 0.0)
                             for kind in PRODUCTS}
    return result


def compare(data, grid, lines):
    eia = load_eia()
    lines += ['EIA-930 alignment (MW; EIA blanks=0; generation includes integrated batteries).',
              'Years refer to local delivery dates, including HE24. Shift s compares ERCOT(t) with EIA(t+s).',
              'Shift MAEs use the same hours available at all seven shifts. Bias = forecast - actual.']
    for year in range(START.year, END.year + 1):
        for kind, (forecasts, actuals) in data.items():
            times = [t for t, (_, _, d) in grid.items() if d.year == year and t in actuals and t in eia]
            lines.append(f'{year} {kind}: matched hours={len(times)}')
            if times:
                a = np.array([actuals[t] for t in times])
                b = np.array([eia[t][kind] for t in times])
                delta = np.abs(a - b)
                corr = np.corrcoef(a, b)[0, 1] if len(a) > 1 and a.std() and b.std() else float('nan')
                lines.append(f'  MAE={delta.mean():.6f}; max absolute difference={delta.max():.6f}; correlation={corr:.9f}')
                common = [t for t in times if all(t + s * HOUR in eia for s in range(-3, 4))]
                if common:
                    scores = {s: np.mean([abs(actuals[t] - eia[t + s * HOUR][kind]) for t in common])
                              for s in range(-3, 4)}
                    best = min(scores, key=lambda s: (scores[s], abs(s), s))
                    lines += [f'  Shift common hours={len(common)}; best shift={best:+d} h',
                              '  Shift MAEs: ' + ', '.join(f'{s:+d}h={v:.6f}' for s, v in scores.items())]
                else:
                    lines.append('  Shift comparison unavailable: no common hours')
                lines.append('  Largest 10 differences: UTC hour ending | ERCOT | EIA | absolute difference')
                for i in sorted(range(len(times)), key=lambda i: (-delta[i], times[i]))[:10]:
                    lines.append(f'    {times[i]:{TIME_FMT}} | {a[i]:.6f} | {b[i]:.6f} | {delta[i]:.6f}')
            errors = [forecasts[t][1] - actuals[t] for t, (_, _, d) in grid.items()
                      if d.year == year and t in actuals and t in forecasts and forecasts[t][1] is not None]
            name = PRODUCTS[kind][1]
            if errors:
                values = np.array(errors)
                lines.append(f'  Day-ahead {name}: hours={len(errors)}; MAE={np.abs(values).mean():.6f}; bias={values.mean():.6f}')
            else:
                lines.append(f'  Day-ahead {name}: hours=0; MAE/bias unavailable')
            lines.append('')


def output_value(value):
    if value is None:
        return ''
    if isinstance(value, datetime):
        return value.strftime(TIME_FMT)
    return format(value, '.15g')


def main():
    global START, END, COVER_START, CSV_OUT, SUMMARY_OUT
    args = sys.argv[1:]
    opts = dict(zip(args[1::2], args[2::2]))
    if len(args) % 2 != 1 or set(opts) - {'--start', '--end', '--out', '--summary'}:
        raise SystemExit(__doc__)
    folder = Path(args[0]).resolve()
    START = date.fromisoformat(opts.get('--start', START.isoformat()))
    END = date.fromisoformat(opts.get('--end', END.isoformat()))
    COVER_START = START - DAY
    CSV_OUT = ROOT / opts['--out'] if '--out' in opts else CSV_OUT
    SUMMARY_OUT = ROOT / opts['--summary'] if '--summary' in opts else SUMMARY_OUT
    manifest = {kind: {} for kind in PRODUCTS}
    for path in sorted(folder.glob('archive_manifest*.csv')):     # the main manifest plus any supplements
        with path.open(encoding='utf-8-sig', newline='') as f:
            for r in csv.DictReader(f):
                kind, doc = r['label'], int(r['docId'])
                post = datetime.fromisoformat(r['postDatetime'])
                if kind not in manifest:
                    raise ValueError(f'Unknown manifest label: {kind}')
                if doc in manifest[kind] and manifest[kind][doc] != post:
                    raise ValueError(f'Conflicting manifest docId: {doc}')
                manifest[kind][doc] = post
    grid = {}
    for d in dates(START, END):
        for (_, flag), (utc, local) in day_grid(d).items():
            if utc in grid:
                raise ValueError(f'Duplicate UTC hour: {utc}')
            grid[utc] = (local, flag, d)
    times = sorted(grid)
    if any(b - a != HOUR for a, b in zip(times, times[1:])):
        raise ValueError('Output grid is not consecutive UTC hours')
    lines = [f'ERCOT day-ahead wind/solar forecasts: {START} to {END}',
             f'Time conversion: {"zoneinfo America/Chicago" if CHICAGO else "US DST rule fallback"}',
             f'Output: {len(times)} hourly rows; UTC {times[0]:{TIME_FMT}} through {times[-1]:{TIME_FMT}}',
             'Rolling-report interior days and selected forecast days checked for exact 23/24/25-hour structure.',
             'Coverage anomalies are reported; valid hours retained, missing hours left empty.',
             'Spring HE03-without-HE02 variants use sorted ranks and canonical HE02 output labels.',
             'Partial first/last report days checked against complete-day hour ranks.',
             'Latest actual = latest local publication timestamp, then largest docId, with a nonempty value.', '']
    data = {kind: extract(folder, kind, manifest[kind], lines) for kind in PRODUCTS}
    compare(data, grid, lines)
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_OUT.parent.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(COLUMNS)
        for t in times:
            local, flag, _ = grid[t]
            row = [t.strftime(TIME_FMT), local.strftime(TIME_FMT), flag]
            for kind in PRODUCTS:
                row += [output_value(v) for v in data[kind][0].get(t, (None,) * 4)]
            row += [output_value(data[kind][1].get(t)) for kind in PRODUCTS]
            writer.writerow(row)
    text = '\n'.join(lines) + '\n'
    SUMMARY_OUT.write_text(text, encoding='utf-8')
    print(text, end='')


if __name__ == '__main__':
    main()
