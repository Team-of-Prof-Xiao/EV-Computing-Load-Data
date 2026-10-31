# Alibaba cluster-trace-v2026-spot-gpu (not included)

**Source:** https://github.com/alibaba/clusterdata/tree/master/cluster-trace-v2026-spot-gpu

The upstream repository has no license file, and its README asks users to cite the paper below, so the files are not stored here. Download them and check their SHA-256 with `bash scripts/fetch_alibaba.sh`, run from the repository root:

| File | Bytes | Contents |
|---|---|---|
| `job_info_df.csv` | 23,055,929 | 466,867 jobs: `job_name`, `organization`, `gpu_model`, `cpu_request`, `gpu_request`, `worker_num`, `submit_time`, `duration` (s), `job_type` |
| `node_info_df.csv` | 78,330 | 4,278 nodes with 10,412 GPUs (A10, A100-80GB, A800, H800 and anonymized models) |
| `README.upstream.md` | 5,608 | the upstream README |

**Job types.** High-priority jobs (415,713; about 8,700 GPUs in use on average) include long-running services. Spot jobs (51,154; median duration 0.58 h) can be preempted and account for 2.4% of GPU-hours.

**Time is relative.** The trace is anonymized: `submit_time` counts seconds from the first submitted job, and absolute dates and the time zone are not released. The trace spans 184 days. Its daily and weekly cycles are clear: the autocorrelation of hourly GPUs in use is 0.75 (high-priority) and 0.63 (Spot) at a lag of 24 h, and 0.52 and 0.43 at 168 h. Spot submissions are fewest in relative hours 3–9 and most frequent at 10–11 and 14–17, which suggests that relative hour 0 is near local midnight, but this is an inference.

**Citation:** Duan, J., Xu, S., Qian, S., Yang, D., Wang, K., Liao, C., Yu, Y., Hua, Q., Hu, H., Wang, Q., Wu, W., Bao, D., Lu, T., Cao, J., Xue, G., Yang, G., Zhang, L., and Chen, G. (2026). GFS: A Preemptive Scheduling Framework for GPU Clusters with Predictive Spot Management. In *Proceedings of the 31st ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS 2026)*.
