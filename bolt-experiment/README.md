# LLVM BOLT 与 SQLite 跨层优化实验

本目录是独立实验，不修改原始项目。当前工作区没有 LLVM BOLT 源码；需自行提供 LLVM BOLT 工具与 SQLite amalgamation 源码。实验运行 SQLite CLI：生成 10 万订单、创建索引并执行 1 万次聚合查询。数据为合成数据，应用为真实开源 SQLite，非真实业务轨迹。

Linux 环境需安装 clang、llvm-bolt、perf2bolt、perf、Python 3、taskset，以及支持分支记录的 CPU 和允许 perf 采样的系统配置。构建 llvm-bolt 时需启用 LLVM BOLT 项目；SQLite amalgamation 需含 sqlite3.c、shell.c 和 sqlite3.h。设置 `SQLITE_SOURCE` 为其绝对路径，运行：

```bash
cd bolt-experiment
export SQLITE_SOURCE=/path/to/sqlite-amalgamation
bash run.sh
```

脚本对无优化、BOLT、CPU 亲和性及两者组合各运行 5 次，比较完整输出；`results/raw.json` 保存逐次数据，`results/summary.json` 保存均值、标准差、吞吐、加速比和 CPU 使用率。CPU 使用率为子进程 CPU 时间除墙钟时间。工作负载包含数据库初始化，因此吞吐量按 10000 条查询除以整体时间计算。perf 分支采样、BOLT 构建或 CPU 亲和性不被支持时脚本会失败，需先解决环境问题，不会生成虚假结果。

实验限制：采样负载和测试负载相同，存在训练偏差；应增加独立测试负载。固定运行顺序可能受到热缓存及系统漂移影响；应随机化并增加轮次。尚未实现 cache miss、IPC 的采集及绘图，也尚未完成 perf 瓶颈报告。BOLT 使用现有 hfsort+ 和 ext-tsp，非原创算法。实际分析需先检查 perf 热点和调度迁移，不能预设 BOLT 或绑核一定有效。
