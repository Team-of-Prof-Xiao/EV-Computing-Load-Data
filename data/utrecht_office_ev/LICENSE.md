# License and attribution

The three files in this folder are redistributed unchanged from:

de Bont, K., Hoogsteen, G., Hurink, J., Kokhuis, R., Kusche, F., Nijenhuis, B., Ozceylan, B., de Ruijter, J., Schubbel, A., and van der Velden, J. (2025). *Electric Vehicle Charging Session Data of Large Office Parking Lot* (Version 2) [Data set]. 4TU.ResearchData. https://doi.org/10.4121/80ef3824-3f5d-4e45-8794-3b8791efbd13.v2

**License:** Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0), https://creativecommons.org/licenses/by-nc-sa/4.0/. You may share and adapt these files for non-commercial purposes if you give attribution, and adaptations must use the same license.

**Files.** `README.txt` is the publishers' description (data collection, charging equipment, disclaimers). `202410DatasetEVOfficeParking_v0.csv` holds one row per charging session; it is semicolon-separated UTF-8 with a byte-order mark, and times are local (Europe/Amsterdam). Columns: `EV_id_x` (pseudonym), `start_datetime`, `end_datetime`, `total_energy` (kWh), `rail`, `evse_uid`, `channel`, `capacity_kwh`, and survey fields (`commute_km_range_min`, `commute_km_range_max`, `EV_brand_selfreported`, `EV_model_selfreported`, `capacity_kwh_selfreported`, `ownership`) that are filled for 4,053 sessions. `Survey_supplementary.zip` holds the survey questions and procedure, without responses.

**Provenance.** The files come from the dataset's "download all" package for version 2 (4,745,309 bytes), retrieved on 2026-10-31 from the Internet Archive copy of the official 4TU download link (captured 2026-02-23). The MD5 of every file matches the checksum listed on the 4TU dataset page:

| File | Bytes | MD5 |
|---|---|---|
| README.txt | 13,271 | 382fab9d855e7a3e29c55c6b0e8ce3e8 |
| 202410DatasetEVOfficeParking_v0.csv | 4,270,702 | 1c3eef11775c274c239c77714ad0705a |
| Survey_supplementary.zip | 460,900 | 25d1947d8ed3801e81a717d0978ece88 |
