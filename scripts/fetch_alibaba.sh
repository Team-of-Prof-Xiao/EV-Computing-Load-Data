#!/usr/bin/env bash
# Check the Alibaba trace files in this repository against the SHA-256 values of the official release
# (recorded on 2026-10-30), downloading any missing file from its official location.
# Run from the repository root: bash scripts/fetch_alibaba.sh
set -euo pipefail

if command -v sha256sum >/dev/null 2>&1; then check() { sha256sum -c -; }; else check() { shasum -a 256 -c -; }; fi

fetch() {  # URL, destination, expected SHA-256
  mkdir -p "$(dirname "$2")"
  if [ ! -f "$2" ]; then curl -fL --retry 3 -o "$2" "$1"; fi
  echo "$3  $2" | check || { echo "checksum mismatch: the upstream file may have changed since 2026-10-30" >&2; exit 1; }
}

base=https://raw.githubusercontent.com/alibaba/clusterdata/master/cluster-trace-v2026-spot-gpu
fetch "$base/job_info_df.csv" data/alibaba_spot_gpu_v2026/job_info_df.csv \
  113ccee4c28f5c3bbaaca974cd164b9280b7d4c39e53b745443b28eea05e03dd
fetch "$base/node_info_df.csv" data/alibaba_spot_gpu_v2026/node_info_df.csv \
  1aba161961a5a4a1a61aa581383c5e5abe3400b59f8597ba8c4eef7597bc9d18
fetch "$base/README.md" data/alibaba_spot_gpu_v2026/README.upstream.md \
  11eb33818d3b40ba430c1bc1e0fd42786af214db334152141e29bccb3d26db2b
fetch https://tre-clusterdata.oss-cn-hangzhou.aliyuncs.com/cluster-trace-v2026-maas/data/app_metrics.csv.zip \
  data/alibaba_maas_v2026/app_metrics.csv.zip \
  c03d3a0cd81d1bd1060eee5035022ea071879817b794cc0c7bf2ad6659cfe927
