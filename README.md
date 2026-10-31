# EV Charging and AI Computing Load Data

English | [中文](README.zh-CN.md)

Public datasets for studying flexible electric-vehicle (EV) charging and AI computing loads together with Texas wind and solar forecasts, checked and documented in one place.

All six datasets are included, each with its source and license status. Files are copied unchanged, except that the EIA-930 and ERCOT files are hourly extracts of the published data; SHA-256 checksums of all data files are in `SHA256SUMS`. Please read [Data sources and statement](#data-sources-and-statement) before using the data.

## Overview

| Folder | Data | Period | Size | License | Included |
|---|---|---|---|---|---|
| [`data/utrecht_office_ev`](data/utrecht_office_ev) | EV charging sessions of a large office parking lot in Utrecht, the Netherlands | 2020-08-25 to 2024-10-02 | 55,379 sessions, about 300 charge points | CC BY-NC-SA 4.0 | Yes |
| [`data/chargeplace_scotland`](data/chargeplace_scotland) | Charging sessions on the ChargePlace Scotland public network | 2022-10-01 to 2024-03-31 | about 3.12 million sessions, 3,518 charge points | CC BY 4.0 | Yes |
| [`data/eia930`](data/eia930) | Hourly demand, generation by source and day-ahead demand forecast for ERCOT (Texas), from EIA-930 | 2024-01-01 to 2026-10-27 | 24,743 hours | Public domain | Yes |
| [`data/ercot`](data/ercot) | Hourly day-ahead wind and solar forecasts and actual output for ERCOT | 2024-01-01 to 2026-10-27 | 24,719 hours | Not stated; ERCOT terms of use apply | Yes |
| [`data/alibaba_spot_gpu_v2026`](data/alibaba_spot_gpu_v2026) | GPU jobs in Alibaba clusters, high-priority and Spot | 184 days, relative time | 466,867 jobs, 10,412 GPUs | Not stated; cite the paper | Yes |
| [`data/alibaba_maas_v2026`](data/alibaba_maas_v2026) | Hourly metrics of LLM inference applications at Alibaba | one week, relative time | 7,401 rows, 4 applications | Not stated; cite the paper | Yes |

## The datasets

### 1. Utrecht office parking lot (EV charging)

- **What it is.** Every EV charging session recorded at the employee and visitor parking lot of an office building (a.s.r.) in Utrecht, the Netherlands, from August 2020 to October 2024. The data were collected in the SmoothEMS met GridShield project and published by the University of Twente and its partners on 4TU.ResearchData.
- **One row** is one charging session: a pseudonymous vehicle ID, plug-in and plug-out times, energy delivered (kWh) and the charge point used. About 4,000 sessions also carry the drivers' survey answers (battery capacity, commute distance range, car model).
- **Why it is useful.** It is a real workplace site. Cars arrive in the morning and stay most of the working day, far longer than they need to charge, so their charging can be shifted. The site has about 300 charge points: 22 kW chargers with two plugs, giving 11 kW per plug when both are in use.
- **Key figures.** 55,379 sessions; about 97 per working day in 2024; median stay 7.1 h; median energy 17.6 kWh; three quarters of weekday arrivals between 07:00 and 10:00; median departure 16:17. Charging at 11 kW, the median session would still have 4.7 h to spare.
- **Caveats.** The site grew over the period (9 charge points in use in 2020, 309 in 2024), and COVID-19 lockdowns depress 2020–2021, so data from 2023 onward best represent the full site. There is almost no charging at weekends. The publishers removed sessions under 1 kWh, under 10 minutes or over 24 hours.

### 2. ChargePlace Scotland (EV charging)

- **What it is.** Charging sessions on Scotland's national public charging network from October 2022 to March 2024, compiled by the University of Strathclyde from ChargePlace Scotland data, with descriptive tables for each charge point.
- **One row** is one session: charge point ID, energy (kWh), duration, start date and time, and amount paid. Separate tables give each charge point's speed (AC, Rapid or Ultra-Rapid), local authority, postcode and area indices.
- **Why it is useful.** It is large and recent, and it shows how public charging differs from workplace charging: half of the sessions are at rapid chargers with a median stay of 0.68 h, while sessions at AC chargers have a median stay of 2.9 h.
- **Key figures.** About 3.12 million session rows from 3,518 charge points; 2,857,836 sessions remain after cleaning, about 5,400 a day.
- **Caveats.** The workbooks need cleaning; see [Known issues](#known-issues).

### 3. EIA-930 hourly grid data for Texas (ERCOT)

- **What it is.** Hourly data of the U.S. Energy Information Administration for the ERCOT balancing authority, which serves most of Texas: demand, the day-ahead demand forecast and net generation by energy source, from January 2024 to October 2026.
- **One row** is one hour, in MW, with local (US Central) and UTC timestamps at the end of the hour.
- **Why it is useful.** It gives hourly wind and solar output, the generation mix (from which carbon intensity can be estimated) and the demand of a large grid with a high share of renewables.
- **Caveats.** Files before July 2024 use EIA's older layout: hydro includes pumped storage and there are no storage columns. The last row of 2026 holds only the demand forecast.

### 4. ERCOT day-ahead wind and solar forecasts

- **What it is.** ERCOT's own hourly forecasts of total wind and solar output, as published the day before (the 09:55 release), paired with the actual output, from January 2024 to October 2026.
- **One row** is one hour: the forecasts (STWPF, STPPF and the resource power potential forecasts), the limits in the resources' operating plans, and the actual output, in MW.
- **Why it is useful.** Forecast minus actual output gives the day-ahead forecast errors that an operator faces when planning the next day.
- **Source.** Extracted with `scripts/extract_ercot_forecasts.py` from ERCOT reports NP4-732-CD and NP4-737-CD, downloaded through the ERCOT Public API. ERCOT states no license for republishing its reports, so its terms of use apply. [`data/ercot/README.md`](data/ercot/README.md) explains how to rebuild the files.

### 5. Alibaba GPU cluster jobs, high-priority and Spot

- **What it is.** Six months of jobs submitted to Alibaba's GPU clusters (cluster-trace-v2026-spot-gpu), released with an ASPLOS 2026 paper. High-priority jobs, including long-running services, run when submitted; Spot jobs use spare GPUs, can be preempted and can wait.
- **One row** is one job: organization, GPU model, numbers of CPUs, GPUs and workers, submission time, duration and job type. A second table lists the 4,278 nodes and their 10,412 GPUs.
- **Why it is useful.** It separates computing load that cannot wait from load that can be shifted, which is the basis for modeling flexible AI computing demand.
- **Key figures.** 466,867 jobs over 184 days. High-priority jobs keep about 8,700 GPUs busy on average; Spot jobs account for 2.4% of GPU-hours, with a median duration of 0.58 h.
- **Caveats.** Times are relative; see [Known issues](#known-issues).
- **Source.** Unchanged copy of the official release, including its README (`README.upstream.md`). Alibaba states no license and asks users to cite the paper.

### 6. Alibaba LLM inference metrics

- **What it is.** One week of hourly metrics for four online large-language-model applications on Alibaba's Model-as-a-Service platform (the `app_metrics` file of cluster-trace-v2026-maas), released with an ATC '26 paper.
- **One row** is one hourly value of one metric for one series: normalized requests per second, GPU count, token counts, response latencies and KV-cache utilization, split into the prefill and decode stages.
- **Why it is useful.** It shows the daily shape of online inference demand: the summed normalized request rate rises from about 0.2 at night to about 2.3 in the afternoon and evening.
- **Caveats.** Only one week and four applications; times are relative.
- **Source.** Unchanged copy of the official file. Alibaba states no license and asks users to cite the paper.

## Known issues

**ChargePlace Scotland needs cleaning.** `scripts/inspect_scotland.py` reports and applies these steps:
- 16 days have no records at all, which are export gaps rather than idle days: 2022-10-31, 2022-12-04, 2022-12-26 to 31, 2023-03-01 to 05 and 2024-02-05 to 07;
- 27,026 rows are exact duplicates;
- the October 2023 sheet stores 993 durations over 24 h as text such as "1 day, 8:37:17", and 99 durations elsewhere are garbled or empty;
- the November 2023 sheet has a different column order, so columns are read by name;
- after dropping stays under 1 minute, energy under 0.1 kWh, stays over 72 h and mean power over 350 kW, 2,857,836 sessions remain.

**The Alibaba traces have no dates.** Both traces are anonymized. Every time is an offset in seconds, not a date: `submit_time` counts from the first submitted job, and `time_s` is an offset within the six-month inference trace. Absolute dates and the time zone are not released. The daily and weekly cycles are clear, so clock time and weekday can only be inferred by aligning these cycles; any such alignment is an assumption and should be reported.

**The datasets come from different places and years.** EVs are from the Netherlands and Scotland, computing from Alibaba, and wind and solar from Texas; apart from the Texas data, the periods also differ. A study that combines them has to align them by calendar position, such as month, type of day and hour, and should say so.

**Time zones.** Utrecht: Europe/Amsterdam local time. Scotland: UK local time. EIA-930 and ERCOT: hour-ending timestamps in US Central time and in UTC.

## Quick start

Requirements: Python 3.9 or later with NumPy, and `curl` for fetching.

```bash
shasum -a 256 -c SHA256SUMS      # check the included files
bash scripts/fetch_alibaba.sh    # optional: check the Alibaba files against the official release
python3 -I scripts/inspect_utrecht.py data/utrecht_office_ev/202410DatasetEVOfficeParking_v0.csv
python3 -I scripts/inspect_scotland.py data/chargeplace_scotland
python3 -I scripts/inspect_spot_gpu.py data/alibaba_spot_gpu_v2026
python3 -I scripts/inspect_alibaba_app_metrics.py data/alibaba_maas_v2026/app_metrics.csv.zip
```

The inspection scripts only read the data and print summaries. `inspect_scotland.py` reads the Excel workbooks with the standard library, so no spreadsheet package is needed. `extract_eia930.py` and `extract_ercot_forecasts.py` show how the Texas files were built.

## Data sources and statement

| Dataset | Publisher | Original source | License | Retrieved | In this repository |
|---|---|---|---|---|---|
| Utrecht office parking lot | SmoothEMS met GridShield consortium (University of Twente and partners), via 4TU.ResearchData | https://doi.org/10.4121/80ef3824-3f5d-4e45-8794-3b8791efbd13.v2 | CC BY-NC-SA 4.0 | 2026-10-31, from the Internet Archive copy of the official download; MD5 checksums match 4TU | Unchanged copy |
| ChargePlace Scotland | K. Davies, University of Strathclyde; data from ChargePlace Scotland and the Scottish Government | https://doi.org/10.15129/1f431af7-5caa-4840-a9ab-c1f3b521e033 | CC BY 4.0 | 2026-10-30 | Unchanged copy, without the author's analysis script |
| EIA-930 | U.S. Energy Information Administration | https://www.eia.gov/electricity/gridmonitor/ | Public domain | 2026-10-27 | ERCOT rows extracted; values unchanged |
| ERCOT wind and solar forecasts | Electric Reliability Council of Texas | Reports NP4-732-CD and NP4-737-CD, https://www.ercot.com/ | Not stated; ERCOT terms of use apply | 2026-10, through the ERCOT Public API | Hourly extract of the day-ahead release |
| Alibaba Spot GPU trace | Alibaba Group | https://github.com/alibaba/clusterdata/tree/master/cluster-trace-v2026-spot-gpu | Not stated; citation requested | 2026-10-30 | Unchanged copy |
| Alibaba MaaS trace (app_metrics) | Alibaba Group | https://github.com/alibaba/clusterdata/tree/master/cluster-trace-v2026-maas | Not stated; citation requested | 2026-10-30 | Unchanged copy of app_metrics.csv.zip |

**Statement**

1. **Ownership.** All data belong to their original publishers. They are redistributed here for research and teaching, with their sources stated: copied unchanged, or for EIA-930 and ERCOT as hourly extracts with values unchanged.
2. **Licenses differ by folder.** The Utrecht data may be used for non-commercial purposes only, and adaptations must be shared under CC BY-NC-SA 4.0. ERCOT and Alibaba state no license for their data, and this repository grants none; their own terms apply. The MIT License of this repository covers only the code in `scripts/`, not the data.
3. **No affiliation or endorsement.** This repository is not affiliated with or endorsed by any of the data publishers. The figures in this README come from our own checks and are not official statistics.
4. **No warranty.** The data and scripts are provided "as is", without warranty of any kind. Check the original sources before relying on them.
5. **Privacy.** The EV data were anonymized or pseudonymized by their publishers. Do not try to identify individuals, or link the data with other sources for that purpose.
6. **Removal requests.** If you hold rights in any file here and object to its redistribution, please open an issue, and we will remove the file promptly.

## Licenses

- Code in `scripts/`: MIT License, see [LICENSE](LICENSE).
- Data keep their original licenses, stated in the LICENSE or README file of each data folder: Utrecht CC BY-NC-SA 4.0, ChargePlace Scotland CC BY 4.0 and EIA-930 public domain. ERCOT and Alibaba state no license; their terms apply, and their sources must be cited.

## Citation

If you use these data, cite the original sources:

1. de Bont, K., Hoogsteen, G., Hurink, J., Kokhuis, R., Kusche, F., Nijenhuis, B., Ozceylan, B., de Ruijter, J., Schubbel, A., and van der Velden, J. (2025). *Electric Vehicle Charging Session Data of Large Office Parking Lot* (Version 2). 4TU.ResearchData. https://doi.org/10.4121/80ef3824-3f5d-4e45-8794-3b8791efbd13.v2
2. Davies, K. (2024). *Scottish Public Electric Vehicle Charging – ChargePlace Scotland October 2022 to March 2024*. University of Strathclyde. https://doi.org/10.15129/1f431af7-5caa-4840-a9ab-c1f3b521e033
3. U.S. Energy Information Administration. *Hourly Electric Grid Monitor* (Form EIA-930). https://www.eia.gov/electricity/gridmonitor/
4. Electric Reliability Council of Texas. Reports NP4-732-CD and NP4-737-CD. https://www.ercot.com/
5. Duan, J., et al. (2026). GFS: A Preemptive Scheduling Framework for GPU Clusters with Predictive Spot Management. In *Proc. ASPLOS 2026*.
6. Zheng, Y., Yang, L., Yu, Y., Yang, G., Zhang, L., and Yu, M. (2026). Model-as-a-Service in the Wild: Characterizing Production LLM Inference Clusters at Scale. In *Proc. ATC '26*.
