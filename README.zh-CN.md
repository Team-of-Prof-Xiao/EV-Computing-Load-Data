# 电动汽车充电与 AI 算力负荷数据集

[English](README.md) | 中文

这里收集了一组公开数据集，用来研究可调度的电动汽车（EV）充电、AI 算力负荷，以及美国得克萨斯州的风电和光伏预测。每个数据集都核对过，并写了说明。

六个数据集都放在仓库里，每个都注明了出处和许可情况。文件都是原样复制的，只有 EIA-930 和 ERCOT 是从发布的数据里提取的逐小时数据；所有数据文件的 SHA-256 校验码在 `SHA256SUMS` 里。使用前请先看[数据来源与声明](#数据来源与声明)。

## 总览

| 文件夹 | 数据 | 时间 | 规模 | 许可 | 是否放在仓库里 |
|---|---|---|---|---|---|
| [`data/utrecht_office_ev`](data/utrecht_office_ev) | 荷兰乌特勒支一个大型办公楼停车场的 EV 充电记录 | 2020-08-25 至 2024-10-02 | 55,379 次充电，约 300 个充电桩 | CC BY-NC-SA 4.0 | 是 |
| [乌特勒支新传入原始文件夹](data/Electric%20Vehicle%20Charging%20Session%20Data%20of%20Large%20Office%20Parking%20Lot%20_1_all) | 乌特勒支办公停车场充电数据的副本，附展开的问卷资料 | 2020-08-25 至 2024-10-02 | 55,379 次充电（与上一行 CSV 相同）；5 份问卷资料 | 充电数据：CC BY-NC-SA 4.0；问卷资料未注明许可 | 是 |
| [`data/chargeplace_scotland`](data/chargeplace_scotland) | 苏格兰 ChargePlace Scotland 公共充电网的充电记录 | 2022-10-01 至 2024-03-31 | 约 312 万次充电，3,518 个充电桩 | CC BY 4.0 | 是 |
| [`data/eia930`](data/eia930) | 德州电网（ERCOT）逐小时的负荷、分电源发电量和日前负荷预测，来自 EIA-930 | 2024-01-01 至 2026-10-27 | 24,743 个小时 | 公有领域 | 是 |
| [`data/ercot`](data/ercot) | ERCOT 逐小时的风电、光伏日前预测和实际出力 | 2024-01-01 至 2026-10-27 | 24,719 个小时 | 未说明，适用 ERCOT 使用条款 | 是 |
| [`data/alibaba_spot_gpu_v2026`](data/alibaba_spot_gpu_v2026) | 阿里巴巴 GPU 集群的作业，分高优先级和 Spot 两类 | 184 天，相对时间 | 466,867 个作业，10,412 张 GPU | 未说明，要求引用论文 | 是 |
| [`data/alibaba_maas_v2026`](data/alibaba_maas_v2026) | 阿里巴巴大模型推理应用的逐小时指标 | 一周，相对时间 | 7,401 行，4 个应用 | 未说明，要求引用论文 | 是 |

## 各数据集说明

### 1. 乌特勒支办公楼停车场（EV 充电）

- **是什么：** 荷兰乌特勒支一栋办公楼（a.s.r.）的员工和访客停车场，2020 年 8 月到 2024 年 10 月记录的每一次 EV 充电。数据来自 SmoothEMS met GridShield 项目，由特温特大学和合作方发布在 4TU.ResearchData 上。
- **一行是什么：** 一次充电，包括化名的车辆编号、插枪和拔枪时间、充电量（kWh）和所用的充电桩。约 4,000 次充电还附有车主的问卷回答（电池容量、通勤距离范围、车型）。
- **有什么用：** 这是一个真实的上班停车场。车早上到、停大半个工作日，停的时间比充满所需的时间长得多，所以充电时间可以挪动。场地约有 300 个充电桩，都是 22 kW 双枪桩，两辆车同时充时每枪 11 kW。
- **主要数字：** 55,379 次充电；2024 年每个工作日约 97 次；停留时间中位数 7.1 小时；充电量中位数 17.6 kWh；工作日四分之三的车在 7:00–10:00 到达；离开时间中位数 16:17。按 11 kW 充电，充满后中位数还能多停 4.7 小时。
- **注意：** 这期间停车场一直在扩建，用到的充电桩从 2020 年的 9 个增加到 2024 年的 309 个；2020–2021 年还有疫情封控。所以 2023 年以后的数据最能代表建成后的停车场。周末几乎没有充电。发布方已经去掉了充电不到 1 kWh、停留不到 10 分钟或超过 24 小时的记录。
- **新增副本与问卷资料：** 新传入的[原始文件夹](data/Electric%20Vehicle%20Charging%20Session%20Data%20of%20Large%20Office%20Parking%20Lot%20_1_all)包含与 `data/utrecht_office_ev` 完全相同的充电记录 CSV（SHA-256 一致）、较早版本的来源说明，以及展开的 `Survey_supplementary` 文件夹。该文件夹中的五个文件与已有的问卷 ZIP 内文件逐字节一致，包括荷兰语问卷、邮件联系同意表、研究说明和同意表、邮件正文与问卷说明。它们是调查过程资料，不包含个人问卷答复；这个副本不是第七个独立数据集。
- **使用时注意：** 时间采用荷兰当地时间，包含夏令时切换；部分充电 ID 为多人共用，不能视作单一车主。来源说明还指出充电设施及问卷字段存在缺失，并介绍了从 2023 年 3 月起在员工停车区大部分线路实施的模型预测充电控制。控制策略的后续调整和再分发提示请查阅来源说明。

### 2. 苏格兰 ChargePlace Scotland（EV 充电）

- **是什么：** 苏格兰全国公共充电网 2022 年 10 月到 2024 年 3 月的充电记录，由斯特拉斯克莱德大学根据 ChargePlace Scotland 的数据整理，另附每个充电桩的属性表。
- **一行是什么：** 一次充电，包括充电桩编号、充电量（kWh）、时长、开始日期和时刻、付费金额。另外几张表给出每个充电桩的类型（交流慢充、快充、超快充）、所属地方政府、邮编和地区指数。
- **有什么用：** 数据量大、时间新，还能看出公共充电和上班停车场的区别：一半的充电发生在快充桩上，停留时间中位数只有 0.68 小时；交流慢充的停留时间中位数是 2.9 小时。
- **主要数字：** 约 312 万行充电记录，3,518 个充电桩；清洗后剩 2,857,836 次，平均每天约 5,400 次。
- **注意：** 表格需要清洗，见[已知问题](#已知问题)。

### 3. EIA-930 德州电网逐小时数据（ERCOT）

- **是什么：** 美国能源信息署（EIA）发布的 ERCOT 逐小时数据。ERCOT 负责德州大部分地区的电网。数据包括负荷、日前负荷预测和分电源的净发电量，时间是 2024 年 1 月到 2026 年 10 月。
- **一行是什么：** 一个小时，单位 MW，带当地时间（美国中部时间）和 UTC 时间，时间戳标在每小时的结束时刻。
- **有什么用：** 可以得到逐小时的风电和光伏出力、发电结构（可以用来估算碳排放强度）和负荷。ERCOT 是一个可再生能源占比很高的大电网。
- **注意：** 2024 年 7 月以前的文件用的是 EIA 的旧格式：水电里包含抽水蓄能，也没有储能的列。2026 年的最后一行只有负荷预测。

### 4. ERCOT 风电和光伏日前预测

- **是什么：** ERCOT 自己对全网风电、光伏总出力的逐小时预测，取前一天 9:55 发布的那一版，并配上实际出力，时间是 2024 年 1 月到 2026 年 10 月。
- **一行是什么：** 一个小时，包括预测值（STWPF、STPPF 和发电潜力预测）、各电站运行计划里的出力上限，以及实际出力，单位 MW。
- **有什么用：** 预测值减去实际出力，就是调度员提前一天做计划时面对的预测误差。
- **来源：** 用 `scripts/extract_ercot_forecasts.py` 从 ERCOT 的 NP4-732-CD 和 NP4-737-CD 两份报告里提取，报告是通过 ERCOT 公共 API 下载的。ERCOT 没有说明报告能否再发布，所以适用它的使用条款。[`data/ercot/README.md`](data/ercot/README.md) 说明了怎样重建这些文件。

### 5. 阿里巴巴 GPU 集群作业：高优先级和 Spot

- **是什么：** 阿里巴巴 GPU 集群半年内提交的作业（cluster-trace-v2026-spot-gpu），随 ASPLOS 2026 的论文公开。高优先级作业（包括长期运行的服务）提交后马上运行；Spot 作业用空闲的 GPU，可以被抢占，也可以等。
- **一行是什么：** 一个作业，包括所属组织、GPU 型号、CPU、GPU 和工作进程的数量、提交时间、运行时长和作业类型。另一张表列出了 4,278 个节点和上面的 10,412 张 GPU。
- **有什么用：** 它把不能等的算力负荷和可以推迟的算力负荷分开了，这正是给可调度的 AI 算力需求建模的基础。
- **主要数字：** 184 天里共 466,867 个作业。高优先级作业平均占着约 8,700 张 GPU；Spot 作业只占 GPU 时的 2.4%，运行时长中位数 0.58 小时。
- **注意：** 时间是相对时间，见[已知问题](#已知问题)。
- **来源：** 官方发布文件的原样副本，包括它的说明文件（`README.upstream.md`）。阿里巴巴没有给出许可，要求引用论文。

### 6. 阿里巴巴大模型推理指标

- **是什么：** 阿里巴巴"模型即服务"（MaaS）平台上 4 个在线大模型应用一周的逐小时指标，是 cluster-trace-v2026-maas 里的 `app_metrics` 文件，随 ATC '26 的论文公开。
- **一行是什么：** 某条序列某个指标在某个小时的值。指标包括归一化的每秒请求数、GPU 数、token 数、响应延迟和 KV 缓存利用率，并分成预填充（prefill）和解码（decode）两个阶段。
- **有什么用：** 能看出在线推理需求在一天里的变化：几个应用加起来的归一化请求量，夜里约 0.2，下午到晚上约 2.3。
- **注意：** 只有一周、4 个应用；时间是相对时间。
- **来源：** 官方文件的原样副本。阿里巴巴没有给出许可，要求引用论文。

## 已知问题

**苏格兰数据需要清洗。** `scripts/inspect_scotland.py` 会报告并执行下面这些步骤：
- 有 16 天完全没有记录，是导出时漏掉的，不是没人充电：2022-10-31、2022-12-04、2022-12-26 至 31 日、2023-03-01 至 05 日、2024-02-05 至 07 日；
- 有 27,026 行完全重复；
- 2023 年 10 月的表里，993 个超过 24 小时的时长存成了文字（如 "1 day, 8:37:17"），其他月份还有 99 个时长是乱码或空白；
- 2023 年 11 月的表列顺序不同，所以按列名读取；
- 去掉停留不到 1 分钟、充电量不到 0.1 kWh、停留超过 72 小时、平均功率超过 350 kW 的记录后，剩 2,857,836 次充电。

**阿里巴巴的数据没有日期。** 两份数据都做了匿名化。时间都是以秒计的相对偏移，不是日期：`submit_time` 从第一个作业提交时算起，`time_s` 是在半年推理数据里的偏移。真实日期和时区都没有公布。数据的昼夜和每周规律很明显，所以钟点和星期几只能靠对齐这些规律来推断；这种推断是假设，使用时应当说明。

**数据来自不同地区和年份。** EV 数据来自荷兰和苏格兰，算力数据来自阿里巴巴，风电和光伏来自德州；除了德州的数据，时间段也不一样。把它们放在一起研究时，要按日历位置（月份、工作日或周末、小时）对齐，并且说明这样做了。

**时区。** 乌特勒支：荷兰当地时间。苏格兰：英国当地时间。EIA-930 和 ERCOT：美国中部时间和 UTC，时间戳标在每小时的结束时刻。

## 快速开始

需要 Python 3.9 或更新的版本和 NumPy，下载要用 `curl`。

```bash
shasum -a 256 -c SHA256SUMS      # 核对仓库里的文件
bash scripts/fetch_alibaba.sh    # 可选：和阿里巴巴官方发布的文件核对
python3 -I scripts/inspect_utrecht.py data/utrecht_office_ev/202410DatasetEVOfficeParking_v0.csv
python3 -I scripts/inspect_scotland.py data/chargeplace_scotland
python3 -I scripts/inspect_spot_gpu.py data/alibaba_spot_gpu_v2026
python3 -I scripts/inspect_alibaba_app_metrics.py data/alibaba_maas_v2026/app_metrics.csv.zip
```

这些检查脚本只读数据、打印汇总。`inspect_scotland.py` 用标准库直接读 Excel 表，不需要装表格软件包。`extract_eia930.py` 和 `extract_ercot_forecasts.py` 是生成德州数据文件的脚本。

## 数据来源与声明

| 数据集 | 发布方 | 原始出处 | 许可 | 获取时间 | 仓库里放了什么 |
|---|---|---|---|---|---|
| 乌特勒支办公楼停车场 | SmoothEMS met GridShield 项目组（特温特大学及合作方），发布在 4TU.ResearchData | https://doi.org/10.4121/80ef3824-3f5d-4e45-8794-3b8791efbd13.v2 | CC BY-NC-SA 4.0 | 2026-10-31，取自互联网档案馆保存的官方下载链接；MD5 和 4TU 一致 | 原样副本 |
| 苏格兰 ChargePlace Scotland | K. Davies，斯特拉斯克莱德大学；数据来自 ChargePlace Scotland 和苏格兰政府 | https://doi.org/10.15129/1f431af7-5caa-4840-a9ab-c1f3b521e033 | CC BY 4.0 | 2026-10-30 | 原样副本，不含作者的分析脚本 |
| EIA-930 | 美国能源信息署 | https://www.eia.gov/electricity/gridmonitor/ | 公有领域 | 2026-10-27 | 提取了 ERCOT 的行，数值未改动 |
| ERCOT 风电和光伏预测 | 得克萨斯州电力可靠性委员会（ERCOT） | NP4-732-CD 和 NP4-737-CD 两份报告，https://www.ercot.com/ | 未说明，适用 ERCOT 使用条款 | 2026-10，通过 ERCOT 公共 API | 日前发布版的逐小时提取 |
| 阿里巴巴 Spot GPU 数据 | 阿里巴巴集团 | https://github.com/alibaba/clusterdata/tree/master/cluster-trace-v2026-spot-gpu | 未说明，要求引用 | 2026-10-30 | 原样副本 |
| 阿里巴巴 MaaS 数据（app_metrics） | 阿里巴巴集团 | https://github.com/alibaba/clusterdata/tree/master/cluster-trace-v2026-maas | 未说明，要求引用 | 2026-10-30 | app_metrics.csv.zip 的原样副本 |

**声明**

1. **权利归属：** 所有数据都属于原发布方。这里转发它们用于科研和教学，并注明出处：都是原样复制，EIA-930 和 ERCOT 是数值不变的逐小时提取。
2. **各文件夹许可不同：** 乌特勒支的数据只能用于非商业用途，改编后的作品必须同样以 CC BY-NC-SA 4.0 许可发布。ERCOT 和阿里巴巴没有给出数据许可，本仓库也不授予任何许可，适用它们自己的条款。本仓库的 MIT 许可只适用于 `scripts/` 里的代码，不适用于任何数据。
3. **没有隶属或背书关系：** 本仓库和各数据发布方没有隶属关系，也没有得到它们的认可。本说明里的数字来自我们自己的核对，不是官方统计。
4. **不作担保：** 数据和脚本按"原样"提供，不作任何形式的担保。使用前请对照原始出处。
5. **隐私：** EV 数据已经由发布方匿名化或化名处理。请勿尝试识别个人，也不要为此把数据和其他来源关联起来。
6. **删除请求：** 如果您对这里的某个文件享有权利、不同意转发，请提交 issue，我们会尽快删除。

## 许可

- `scripts/` 里的代码：MIT 许可，见 [LICENSE](LICENSE)。
- 数据保留原来的许可，写在每个数据文件夹的 LICENSE 或 README 文件里：乌特勒支 CC BY-NC-SA 4.0，苏格兰 CC BY 4.0，EIA-930 公有领域。ERCOT 和阿里巴巴没有给出许可，适用它们自己的条款，使用时必须注明出处。

## 引用

使用这些数据时，请引用原始出处（文献信息保持英文原文）：

1. de Bont, K., Hoogsteen, G., Hurink, J., Kokhuis, R., Kusche, F., Nijenhuis, B., Ozceylan, B., de Ruijter, J., Schubbel, A., and van der Velden, J. (2025). *Electric Vehicle Charging Session Data of Large Office Parking Lot* (Version 2). 4TU.ResearchData. https://doi.org/10.4121/80ef3824-3f5d-4e45-8794-3b8791efbd13.v2
2. Davies, K. (2024). *Scottish Public Electric Vehicle Charging – ChargePlace Scotland October 2022 to March 2024*. University of Strathclyde. https://doi.org/10.15129/1f431af7-5caa-4840-a9ab-c1f3b521e033
3. U.S. Energy Information Administration. *Hourly Electric Grid Monitor* (Form EIA-930). https://www.eia.gov/electricity/gridmonitor/
4. Electric Reliability Council of Texas. Reports NP4-732-CD and NP4-737-CD. https://www.ercot.com/
5. Duan, J., et al. (2026). GFS: A Preemptive Scheduling Framework for GPU Clusters with Predictive Spot Management. In *Proc. ASPLOS 2026*.
6. Zheng, Y., Yang, L., Yu, Y., Yang, G., Zhang, L., and Yu, M. (2026). Model-as-a-Service in the Wild: Characterizing Production LLM Inference Clusters at Scale. In *Proc. ATC '26*.
