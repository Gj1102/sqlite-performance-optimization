import pathlib,json,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=pathlib.Path(__file__).resolve().parent
s=json.loads((p/'data/factorial-results.json').read_text())['summary']
fig,ax=plt.subplots(figsize=(8,4)); labels=[x['transaction']+'\n'+x['journal'] for x in s]; ax.bar(labels,[x['mean_seconds'] for x in s],yerr=[x['stdev_seconds'] for x in s],capsize=4); ax.set_yscale('log'); ax.set_ylabel('Wall time in seconds (log scale)'); ax.set_title('300 SQLite event inserts: mean and standard deviation'); fig.tight_layout(); fig.savefig(p/'figures/factorial-performance.png',dpi=160)
