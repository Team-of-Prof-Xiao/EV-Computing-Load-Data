# Alibaba cluster-trace-v2026-maas, app_metrics only

**Source:** Alibaba Group, https://github.com/alibaba/clusterdata/tree/master/cluster-trace-v2026-maas. The file `app_metrics.csv.zip` (99,947 bytes) is an unchanged copy of https://tre-clusterdata.oss-cn-hangzhou.aliyuncs.com/cluster-trace-v2026-maas/data/app_metrics.csv.zip, downloaded on 2026-10-30.

**License:** Alibaba states no license; its README asks users to cite the paper below. `bash scripts/fetch_alibaba.sh`, run from the repository root, checks the file against the official release (SHA-256).

**Contents.** `app_metrics.csv` has 7,401 rows: one week (168 hours) of hourly values for 4 applications in 27 series. Columns: `time_s`, `app_id`, `gpu_type`, `series_id`, `pd_role` (prefill or decode), `metric` and `value`. Metrics include normalized queries per second (`qps_norm`), GPU count, token counts, time to first token, time per output token and KV-cache utilization. Summed over applications, `qps_norm` shows a clear daily cycle, from about 0.2 at night to about 2.3 in the afternoon and evening.

**Time is relative.** The trace is anonymized: `time_s` is an offset in seconds (this file starts at 12,096,000 s, which is day 140 if the offset counts from the start of the six-month trace), and absolute dates are not released.

The larger files of this release, `instance_daily.zip` (9.8 GiB) and `instance_week_5min.zip` (4.5 GiB), are not included.

**Citation:** Zheng, Y., Yang, L., Yu, Y., Yang, G., Zhang, L., and Yu, M. (2026). Model-as-a-Service in the Wild: Characterizing Production LLM Inference Clusters at Scale. In *2026 ACM SIGOPS Annual Technical Conference (ATC '26)*.
