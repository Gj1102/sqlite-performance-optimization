# SQLite 业务负载跨层优化实验

使用真实 SQLite 引擎与合成订单、事件负载，比较索引、事务、日志与 Windows CPU 亲和性。报告及完整结果见 [报告.md](报告.md)。绑核是实际测量的系统层尝试，当前机器上变慢。

安装 Python 依赖后运行：

```bash
python -m pip install -r requirements.txt
python reproduce.py
```

该入口检查依赖，随机顺序运行 80 次混合负载并验证结果，计算统计和绘图，写到时间戳 `runs/`，不覆盖历史数据。需要操作系统支持 psutil CPU 亲和性；不支持则退出并保留已有结果。图表优先使用 Windows 黑体，Linux 需安装 Noto Sans CJK。独立历史实验脚本 `sqlite_experiment.py`、`factorial_experiment.py` 会覆盖其对应历史结果，若需重复应先备份。旧脚本 `benchmark.py` 会删除同目录的 experiment.db，避免在存在重要同名文件时使用。

- `data/`：历史实验的逐次真实测量；`figures/`：中文图和保留的旧图。
- `scripts/`：混合负载实验和绘图；`requirements.txt`：Python 依赖。
- `bolt-experiment/`：仅供扩展，尚未验证或运行，不属于已实测结果。
- `runs/`：重新运行的输出，不上传大型临时数据。

合成负载不代表真实生产流量；混合实验是每组五次，固定种子随机化次序，计时范围和限制见报告。无自动 git push。

正式报告：[Markdown](报告.md) 和 [PDF](报告.pdf)；课程逐项自查见 [提交清单](提交清单.md)。可用 `python scripts/verify_data.py` 重新核对原始记录与汇总统计。`python reproduce.py` 的复现运行已验证返回码为 0。PDF 使用 Microsoft Edge 打印生成，HTML 预览已检查中文和表格；当前环境缺少 PDF 页面渲染工具，未逐页检查 PDF 输出。重新生成 PDF 需安装 Markdown 包，执行 `python scripts/export_report.py` 生成 HTML 后使用浏览器打印为 PDF。
