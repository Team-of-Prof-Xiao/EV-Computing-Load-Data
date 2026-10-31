# License and attribution

The 30 workbooks in this folder are redistributed unchanged from:

Davies, K. (2024). *Scottish Public Electric Vehicle Charging – ChargePlace Scotland October 2022 to March 2024* [Data set]. University of Strathclyde. https://doi.org/10.15129/1f431af7-5caa-4840-a9ab-c1f3b521e033

The session data are sourced from ChargePlace Scotland; the Urban Rural Classification, Scottish Index of Multiple Deprivation and Geographical Accessibility Index come from the Scottish Government. The dataset accompanies the paper "Plugging-In Caledonia: Location and utilisation of public electric vehicle chargers in Scotland".

**License:** Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/.

**Files.**
- `Sessions_from_CPS/`: 18 monthly workbooks, October 2022 to March 2024, one row per session. Columns: `CPID` (charge point), `Consumed(kWh)`, `Duration` (stored as a fraction of a day), `Start` (date), `Time` (start time of day, UK local time) and `Amount` (paid, GBP). Departure is start plus duration. File names are inconsistent (for example `October22.xlsx`, `DEC-22.xlsx`, `FEB-2023.xlsx`), and the November 2023 sheet has a different column order.
- `CPID_information/`: charger speed (AC, Rapid, Ultra-Rapid), local authority, postcode, urban–rural class, deprivation rank and accessibility rank of each charge point.
- `Chargers_10km_from_borders/` and `Population_data/`: tables used in the paper's regional comparison.

No changes were made. The original deposit (ScotPublicCharging.zip, 144 MB) also contains the author's analysis script, `code_KD_Dec24.py`, which is not copied here. Known issues and cleaning steps are listed in the repository README; SHA-256 checksums are in `../../SHA256SUMS`.
