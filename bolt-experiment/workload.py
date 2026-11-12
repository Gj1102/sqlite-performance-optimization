import os, sys, subprocess, time, json, statistics, hashlib, pathlib, resource
P=pathlib.Path(__file__).resolve().parent
os.chdir(P)
if sys.argv[1]=='generate':
 p=pathlib.Path(sys.argv[2]); p.write_text('''CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY, customer_id INTEGER, status INTEGER, amount INTEGER);
DELETE FROM orders;
WITH RECURSIVE n(x) AS (VALUES(1) UNION ALL SELECT x+1 FROM n WHERE x<100000) INSERT INTO orders SELECT x,x%2000,x%3,x%10000 FROM n;
CREATE INDEX IF NOT EXISTS idx_orders ON orders(customer_id,status);
''' + '\n'.join(f'SELECT count(*),sum(amount) FROM orders WHERE customer_id={i%2000} AND status={i%3};' for i in range(10000))+'\n')
 sys.exit()
script=pathlib.Path('results/workload.sql').read_bytes(); reference=pathlib.Path('results/reference.txt').read_bytes()
cpu=min(os.sched_getaffinity(0)); records=[]
for binary in ('baseline','bolt'):
 for affinity in (False,True):
  for repeat in range(5):
   cmd=[f'build/sqlite-{binary}','results/input.db']
   if affinity: cmd=['taskset','-c',str(cpu)]+cmd
   before=resource.getrusage(resource.RUSAGE_CHILDREN); start=time.perf_counter()
   p=subprocess.run(cmd,input=script,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
   elapsed=time.perf_counter()-start; after=resource.getrusage(resource.RUSAGE_CHILDREN)
   assert p.stdout==reference, 'output differs from baseline'
   cpu_seconds=(after.ru_utime+after.ru_stime)-(before.ru_utime+before.ru_stime)
   records.append(dict(binary=binary,affinity=affinity,repeat=repeat+1,seconds=elapsed,queries_per_second=10000/elapsed,cpu_percent=100*cpu_seconds/elapsed,output_sha256=hashlib.sha256(p.stdout).hexdigest()))
pathlib.Path('results/raw.json').write_text(json.dumps(records,indent=2))
base=statistics.mean(x['seconds'] for x in records if x['binary']=='baseline' and not x['affinity'])
summary=[]
for binary in ('baseline','bolt'):
 for affinity in (False,True):
  group=[x for x in records if x['binary']==binary and x['affinity']==affinity]; mean=statistics.mean(x['seconds'] for x in group)
  summary.append(dict(binary=binary,affinity=affinity,mean_seconds=mean,stdev_seconds=statistics.stdev(x['seconds'] for x in group),queries_per_second=10000/mean,speedup=base/mean,cpu_percent=statistics.mean(x['cpu_percent'] for x in group)))
pathlib.Path('results/summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
