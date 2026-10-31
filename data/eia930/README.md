# EIA-930 hourly data for ERCOT (Texas)

**Source:** U.S. Energy Information Administration, Hourly Electric Grid Monitor (Form EIA-930), six-month balance files, downloaded on 2026-10-27. The rows of balancing authority ERCO were extracted with `scripts/extract_eia930.py`; values are copied as published, and generation comes from the "(Adjusted)" columns.

**License:** public domain. EIA states that its data may be used and distributed and asks for an acknowledgment such as "Source: U.S. Energy Information Administration (Oct 2026)". See https://www.eia.gov/about/copyrights_reuse.php.

**Files:** `eia930_erco_2024.csv` (8,784 hours), `eia930_erco_2025.csv` (8,760 hours) and `eia930_erco_2026.csv` (7,199 rows, to 2026-10-28 00:00 local time; the final row holds only the demand forecast).

**Columns** (MW, hourly; timestamps mark the end of the hour):
- `time_local` (US Central, as published, for example `01/01/2024 1:00:00 AM`) and `time_utc`;
- `demand`, `netgen` and `demand_forecast` (day-ahead demand forecast);
- net generation by source: `coal`, `gas`, `nuclear`, `oil`, `hydro`, `pumped`, `solar`, `solar_bat`, `wind`, `wind_bat`, `battery`, `other_storage`, `unknown_storage`, `geothermal`, `other`, `unknown`.

Files up to June 2024 use EIA's older layout: hydro includes pumped storage, solar and wind are single columns, and there are no storage columns, so those fields are empty.
