# ERCOT day-ahead wind and solar forecasts

**Source:** Electric Reliability Council of Texas (ERCOT), public reports
- NP4-732-CD, Wind Power Production - Hourly Averaged Actual and Forecasted Values;
- NP4-737-CD, Solar Power Production - Hourly Averaged Actual and Forecasted Values.

The monthly report archives were downloaded through the ERCOT Public API in October 2026, and the two files here were extracted with `scripts/extract_ercot_forecasts.py`. For each operating day the script keeps the last forecast posted by 10:00 on the previous day (the 09:55 release), handles daylight-saving hour labels, and checks the actual output against `data/eia930/`. Values are copied as published.

**License:** ERCOT states no license for republishing its reports, so its terms of use apply (https://www.ercot.com/help/terms/data-portal). Cite ERCOT and the report IDs above when you use these files.

**Files:** `ercot_dayahead_wind_solar_2024_2025.csv` (17,544 hours) and `ercot_dayahead_wind_solar_2026.csv` (7,175 hours, to 2026-10-27).

**Columns** (MW, hourly; timestamps mark the end of the hour):
- `time_utc_hour_ending`, `time_local_hour_ending` (US Central) and `dst_flag`;
- `wind_post_time_local` and `solar_post_time_local`: when the forecast used was posted;
- `wind_stwpf_MW` and `solar_stppf_MW`: ERCOT's short-term wind and solar power forecasts;
- `wind_wgrpp_MW` and `solar_pvgrpp_MW`: the wind and solar resource power potential forecasts;
- `wind_cop_hsl_MW` and `solar_cop_hsl_MW`: the summed high sustained limits in the resources' current operating plans;
- `wind_actual_MW` and `solar_actual_MW`: actual hourly averaged output.

**Rebuilding.** With the monthly archive ZIP files in one folder, run from the repository root:

```bash
python3 -I scripts/extract_ercot_forecasts.py ARCHIVE_DIR --start 2024-01-01 --end 2025-12-31 \
    --out data/ercot/ercot_dayahead_wind_solar_2024_2025.csv
```

The ERCOT Public API needs an ERCOT account, and ercot.com may be unreachable from outside the United States.
