import sqlite3, random, time, statistics, json, platform, sys, os
from pathlib import Path
P=Path(__file__).resolve().parent
random.seed(42)
db=P/'experiment.db'
if db.exists(): db.unlink()
c=sqlite3.connect(db)
c.execute('CREATE TABLE orders(id INTEGER PRIMARY KEY, customer_id INTEGER, status TEXT, amount INTEGER)')
rows=[(i,random.randrange(2000),random.choice(['paid','pending','cancelled']),random.randrange(1,10000)) for i in range(1,100001)]
c.executemany('INSERT INTO orders VALUES (?,?,?,?)',rows); c.commit()
queries=[(random.randrange(2000),'paid') for _ in range(500)]
sql='SELECT id, amount FROM orders WHERE customer_id=? AND status=? ORDER BY id'
def run():
 times=[]; result=[]
 for args in queries:
  t=time.perf_counter_ns(); result.append(c.execute(sql,args).fetchall()); times.append((time.perf_counter_ns()-t)/1e6)
 return times,result
def measure(name):
 c.execute('PRAGMA shrink_memory'); c.execute(sql,queries[0]).fetchall()
 t,res=run(); return {'name':name,'mean_ms':statistics.mean(t),'p95_ms':sorted(t)[int(len(t)*.95)-1],'total_ms':sum(t),'samples_ms':t},res
base,a=measure('baseline_scan')
plan0=c.execute('EXPLAIN QUERY PLAN '+sql,queries[0]).fetchall()
c.execute('CREATE INDEX idx_customer_status ON orders(customer_id,status)'); c.commit()
indexed,b=measure('indexed')
plan1=c.execute('EXPLAIN QUERY PLAN '+sql,queries[0]).fetchall()
assert a==b
# Compare transaction policy on an identical write workload.
def writes(batch):
 c.execute('CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY, payload TEXT)'); c.execute('DELETE FROM events'); c.commit()
 t=time.perf_counter()
 if batch:
  c.executemany('INSERT INTO events(payload) VALUES (?)', [('event',)]*1000); c.commit()
 else:
  for _ in range(1000): c.execute('INSERT INTO events(payload) VALUES (?)',('event',)); c.commit()
 return (time.perf_counter()-t)*1000
single=writes(False); batch=writes(True)
result={'environment':{'python':sys.version,'sqlite':sqlite3.sqlite_version,'platform':platform.platform(),'cpu':platform.processor(),'rows':len(rows),'query_count':len(queries),'seed':42},'query':[base,indexed],'plans':{'baseline':plan0,'indexed':plan1},'writes_ms':{'individual_commits':single,'one_transaction':batch},'correctness':'all 500 result sets identical'}
(P/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
c.close(); db.unlink()
print(json.dumps({k:v for k,v in result.items() if k not in ('query',)},ensure_ascii=False,indent=2)); print([(x['name'],x['mean_ms'],x['p95_ms']) for x in result['query']])
