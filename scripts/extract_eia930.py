"""Extract the ERCOT rows of EIA-930 six-month balance files into one hourly CSV.

Usage: python3 -I scripts/extract_eia930.py OUT.csv RAW.csv [RAW.csv ...]
The raw files are downloads, so run in isolated mode (-I) and read them as data only.

Output columns are listed in data/eia930/README.md and include the day-ahead
demand forecast; values are copied as published. Generation comes from the "(Adjusted)" columns.
Files up to June 2024 use EIA's older layout: hydro includes pumped storage, solar and wind are
single columns, and storage has no columns, so those outputs stay empty.
"""
import csv
import sys
from datetime import datetime

BA = 'ERCO'
TIME_FMT = '%m/%d/%Y %I:%M:%S %p'
G = 'Net Generation (MW) from '
COLUMNS = {  # output column: raw headers, newer layout first
    'time_local': ['Local Time at End of Hour'],
    'time_utc': ['UTC Time at End of Hour'],
    'demand': ['Demand (MW) (Adjusted)'],
    'netgen': ['Net Generation (MW) (Adjusted)'],
    'coal': [G + 'Coal (Adjusted)'],
    'gas': [G + 'Natural Gas (Adjusted)'],
    'nuclear': [G + 'Nuclear (Adjusted)'],
    'oil': [G + 'All Petroleum Products (Adjusted)'],
    'hydro': [G + 'Hydropower Excluding Pumped Storage (Adjusted)', G + 'Hydropower and Pumped Storage (Adjusted)'],
    'pumped': [G + 'Pumped Storage  (Adjusted)'],                        # two spaces, as published
    'solar': [G + 'Solar without Integrated Battery Storage (Adjusted)', G + 'Solar (Adjusted)'],
    'solar_bat': [G + 'Solar witho Integrated Battery Storage (Adjusted)'],  # "witho", as published
    'wind': [G + 'Wind without Integrated Battery Storage (Adjusted)', G + 'Wind (Adjusted)'],
    'wind_bat': [G + 'Wind with Integrated Battery Storage (Adjusted)'],
    'battery': [G + 'Battery Storage (Adjusted)'],
    'other_storage': [G + 'Other Energy Storage (Adjusted)'],
    'unknown_storage': [G + 'Unknown Energy Storage (Adjusted)'],
    'geothermal': [G + 'Geothermal (Adjusted)'],
    'other': [G + 'Other Fuel Sources (Adjusted)'],
    'unknown': [G + 'Unknown Fuel Sources (Adjusted)'],
    'demand_forecast': ['Demand Forecast (MW)'],
}


def main(out, raws):
    rows = []
    for raw in raws:
        with open(raw, newline='') as f:
            reader = csv.DictReader(f)
            source = {col: next((h for h in heads if h in reader.fieldnames), None) for col, heads in COLUMNS.items()}
            missing = [col for col, h in source.items() if h is None]
            n = len(rows)
            for r in reader:
                if r['Balancing Authority'] == BA:
                    rows.append({col: r[h].replace(',', '').strip() if h else '' for col, h in source.items()})
            print(f'{raw}: {len(rows) - n} {BA} rows; no column for {", ".join(missing) or "-"}')
    rows.sort(key=lambda r: datetime.strptime(r['time_utc'], TIME_FMT))
    with open(out, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(COLUMNS))
        w.writeheader()
        w.writerows(rows)
    print(f'{out}: {len(rows)} rows, {rows[0]["time_local"]} to {rows[-1]["time_local"]}')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:])
