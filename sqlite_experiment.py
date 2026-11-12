"""Reproducible SQLite order workload; no external Python packages required."""
import sqlite3, random, time, os, platform, sys, json, statistics, tempfile, pathlib, hashlib
ROOT=pathlib.Path(__file__).resolve().parent
rng=random.Random(20261112)
rows=[(i,rng.randrange(2000),rng.randrange(3),rng.randrange(1,10000)) for i in range(100000)]
queries=[(rng.randrange(2000),rng.randrange(3)) for _ in range(200)]
records=[]; digests={}
with tempfile.TemporaryDirectory(prefix='sqlite-optimization-') as d:
 for indexed in (False,True):
  db=pathlib.Path(d)/f'{indexed}.db'; c=sqlite3.connect(db)
  c.execute('create table orders(id integer primary key, customer_id integer, status integer, amount integer)')
  c.executemany('insert into orders values(?,?,?,?)',rows); c.commit()
  if indexed: c.execute('create index idx_orders on orders(customer_id,status)'); c.commit()
  plan=c.execute('explain query plan select id,amount from orders where customer_id=? and status=? order by id',queries[0]).fetchall()
  for rep in range(5):
   t=time.perf_counter(); cpu=time.process_time(); out=[]
   for q in queries: out.append(c.execute('select id,amount from orders where customer_id=? and status=? order by id',q).fetchall())
   elapsed=time.perf_counter()-t; cpu=time.process_time()-cpu
   digest=hashlib.sha256(repr(out).encode()).hexdigest(); digests[str(indexed)]=digest
   records.append(dict(workload='query',variant='index' if indexed else 'scan',repeat=rep+1,seconds=elapsed,operations=len(queries),throughput=len(queries)/elapsed,cpu_percent=cpu/elapsed*100,checksum=digest,plan=plan))
  c.close()
 assert digests['True']==digests['False']
 for batch in (False,True):
  c=sqlite3.connect(pathlib.Path(d)/f'write-{batch}.db'); c.execute('create table events(id integer primary key, payload text)'); c.commit()
  for rep in range(5):
   c.execute('delete from events'); c.commit(); t=time.perf_counter(); cpu=time.process_time()
   if batch:
    c.executemany('insert into events(payload) values(?)',[('event',)]*500); c.commit()
   else:
    for _ in range(500): c.execute('insert into events(payload) values(?)',('event',)); c.commit()
   elapsed=time.perf_counter()-t; cpu=time.process_time()-cpu
   count=c.execute('select count(*) from events').fetchone()[0]; assert count==500
   records.append(dict(workload='write',variant='batch' if batch else 'single',repeat=rep+1,seconds=elapsed,operations=500,throughput=500/elapsed,cpu_percent=cpu/elapsed*100,verified_count=count))
  c.close()
summary=[]
for workload, variants in [('query',('scan','index')),('write',('single','batch'))]:
 groups=[[r for r in records if r['workload']==workload and r['variant']==v] for v in variants]; baseline=statistics.mean(r['seconds'] for r in groups[0])
 for g in groups:
  mean=statistics.mean(r['seconds'] for r in g)
  summary.append(dict(workload=workload,variant=g[0]['variant'],mean_seconds=mean,stdev_seconds=statistics.stdev(r['seconds'] for r in g),throughput=g[0]['operations']/mean,cpu_percent=statistics.mean(r['cpu_percent'] for r in g),speedup=baseline/mean))
result={'environment':{'platform':platform.platform(),'processor':platform.processor(),'python':sys.version,'sqlite':sqlite3.sqlite_version,'logical_cpus':os.cpu_count(),'seed':20261112,'rows':100000,'queries':200,'write_rows':500},'records':records,'summary':summary}
(ROOT/'data'/'sqlite-results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(summary,indent=2))
