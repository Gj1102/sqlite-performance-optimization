import json, pathlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=pathlib.Path(__file__).resolve().parent
s=json.loads((p/'data/sqlite-results.json').read_text(encoding='utf-8'))['summary']
fig,axes=plt.subplots(1,2,figsize=(9,4))
for ax,w in zip(axes,['query','write']):
 g=[x for x in s if x['workload']==w]; ax.bar([x['variant'] for x in g],[x['mean_seconds'] for x in g],yerr=[x['stdev_seconds'] for x in g],capsize=4); ax.set_title(w); ax.set_ylabel('Mean wall time (seconds)')
fig.tight_layout(); (p/'figures').mkdir(exist_ok=True); fig.savefig(p/'figures/sqlite-performance.png',dpi=160)
