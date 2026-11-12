import pathlib,json,os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
root=pathlib.Path(__file__).resolve().parents[1]; font=pathlib.Path('C:/Windows/Fonts/simhei.ttf')
if font.exists(): font_manager.fontManager.addfont(str(font)); plt.rcParams['font.family']=font_manager.FontProperties(fname=str(font)).get_name()
else: plt.rcParams['font.sans-serif']=['Noto Sans CJK SC','WenQuanYi Zen Hei','DejaVu Sans']
plt.rcParams['axes.unicode_minus']=False
out=pathlib.Path(os.environ.get('FIGURE_OUTPUT',root/'figures')); out.mkdir(parents=True,exist_ok=True)
old=json.loads((root/'data/sqlite-results.json').read_text(encoding='utf-8'))['summary']; fac=json.loads((root/'data/factorial-results.json').read_text(encoding='utf-8'))['summary']; mixed=json.loads(pathlib.Path(os.environ.get('MIXED_OUTPUT',root/'data/mixed-affinity-results.json')).read_text(encoding='utf-8'))
def bars(name,title,labels,means,errors,log=False):
 fig,ax=plt.subplots(figsize=(8,4.8)); ax.bar(labels,means,yerr=errors,capsize=5,color='#4484b5',label='均值及样本标准差'); ax.set_title(title); ax.set_ylabel('墙钟时间（秒）'+('，对数坐标' if log else '')); ax.set_xlabel('实验方案'); ax.legend()
 if log: ax.set_yscale('log')
 fig.tight_layout(); fig.savefig(out/name,dpi=170); plt.close(fig)
for w,title,name in [('query','订单查询：全表扫描与索引','query-cn.png'),('write','事件写入：逐条提交与批量事务','write-cn.png')]:
 g=[x for x in old if x['workload']==w]; bars(name,title,['基线','优化'],[x['mean_seconds'] for x in g],[x['stdev_seconds'] for x in g],True)
bars('journal-cn.png','事务与日志模式对照',['逐条\nDELETE','批量\nDELETE','逐条\nWAL','批量\nWAL'],[x['mean_seconds'] for x in fac],[x['stdev_seconds'] for x in fac],True)
s=mixed['summary']; g=[x for x in s if x['n']==100000 and x['read_pct']==90]; bars('affinity-cn.png','混合负载：索引与 CPU 亲和性（10 万行、90% 读）',['基线','绑核','索引','索引+绑核'],[x['mean'] for x in g],[x['stdev'] for x in g],True)
fig,ax=plt.subplots(figsize=(8,5))
for i,a,label in [(0,0,'基线'),(0,1,'绑核'),(1,0,'索引'),(1,1,'索引+绑核')]:
 g=[x for x in s if x['read_pct']==90 and x['index']==i and x['affinity']==a];ax.errorbar([x['n'] for x in g],[x['mean'] for x in g],yerr=[x['stdev'] for x in g],marker='o',capsize=4,label=label)
ax.set(title='不同数据规模下的混合负载（90% 读）',xlabel='初始订单数（行）',ylabel='墙钟时间（秒，对数坐标）',yscale='log'); ax.legend(); fig.tight_layout(); fig.savefig(out/'scale-cn.png',dpi=170)
