"""Factorial SQLite transaction and storage-journal experiment."""
import sqlite3, tempfile, pathlib, time, random, json, statistics, platform, sys, os, hashlib
P=pathlib.Path(__file__).resolve().parent
N=300; REPEATS=5; records=[]; rng=random.Random(1729)
variants=[(b,j) for b in (False,True) for j in ('DELETE','WAL')]
with tempfile.TemporaryDirectory(prefix='project2-') as tmp:
 for rep in range(1,REPEATS+1):
  rng.shuffle(variants)
  for batch,journal in variants:
   path=pathlib.Path(tmp)/f'{rep}-{batch}-{journal}.db'
   c=sqlite3.connect(path); actual=c.execute('PRAGMA journal_mode='+journal).fetchone()[0].upper(); assert actual==journal
   c.execute('PRAGMA synchronous=FULL'); sync=c.execute('PRAGMA synchronous').fetchone()[0]; assert sync==2
   c.execute('CREATE TABLE events(id INTEGER PRIMARY KEY, customer_id INTEGER, amount INTEGER)'); c.commit()
   t=time.perf_counter(); cpu=time.process_time()
   if batch: c.execute('BEGIN')
   for i in range(N):
    c.execute('INSERT INTO events VALUES(?,?,?)',(i,i%50,(i*17)%1000))
    if not batch: c.commit()
   if batch: c.commit()
   elapsed=time.perf_counter()-t
   # Include checkpoint and close in wall time, ensuring WAL data is consolidated.
   if journal=='WAL':
    checkpoint=c.execute('PRAGMA wal_checkpoint(TRUNCATE)').fetchone(); assert checkpoint[0]==0
   c.close(); elapsed=time.perf_counter()-t; cpu=time.process_time()-cpu
   c=sqlite3.connect(path); rows=c.execute('SELECT * FROM events ORDER BY id').fetchall(); c.close()
   assert rows==[(i,i%50,(i*17)%1000) for i in range(N)]
   records.append(dict(repeat=rep,transaction='batch' if batch else 'single',journal=journal,seconds=elapsed,operations=N,throughput=N/elapsed,cpu_seconds=cpu,cpu_percent=100*cpu/elapsed,sha256=hashlib.sha256(repr(rows).encode()).hexdigest(),synchronous='FULL'))
summary=[]
base=statistics.mean(r['seconds'] for r in records if r['transaction']=='single' and r['journal']=='DELETE')
for b,j in [(False,'DELETE'),(True,'DELETE'),(False,'WAL'),(True,'WAL')]:
 g=[r for r in records if r['transaction']==('batch' if b else 'single') and r['journal']==j]; m=statistics.mean(r['seconds'] for r in g)
 summary.append(dict(transaction=g[0]['transaction'],journal=j,mean_seconds=m,stdev_seconds=statistics.stdev(x['seconds'] for x in g),throughput=N/m,cpu_percent=statistics.mean(x['cpu_percent'] for x in g),speedup=base/m))
result={'environment':{'platform':platform.platform(),'python':sys.version,'sqlite':sqlite3.sqlite_version,'processor':platform.processor(),'seed':1729,'rows':N,'repeats':REPEATS},'records':records,'summary':summary,'notes':'Wall time includes checkpoint and close; CPU time includes checkpoint and close. FULL synchronous; databases reopened and rows checked.'}
(P/'data').mkdir(exist_ok=True); (P/'data/factorial-results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
