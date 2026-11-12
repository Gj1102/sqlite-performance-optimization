import os, sys, sqlite3, random, tempfile, pathlib, time, json, hashlib, statistics, platform, subprocess
import psutil
ROOT=pathlib.Path(__file__).resolve().parents[1]
def worker(n,read_pct,indexed,pinned):
 p=psutil.Process(); allowed=p.cpu_affinity(); selected=min(allowed)
 if pinned: p.cpu_affinity([selected])
 rng=random.Random(271828+n+read_pct); ops=[('r',rng.randrange(1000)) if rng.randrange(100)<read_pct else ('w',rng.randrange(1000)) for _ in range(300)]
 with tempfile.TemporaryDirectory(prefix='sqlite-mixed-') as d:
  db=pathlib.Path(d)/'orders.db'; c=sqlite3.connect(db); c.execute('CREATE TABLE orders(id INTEGER PRIMARY KEY,customer INTEGER,amount INTEGER)'); c.executemany('INSERT INTO orders VALUES(?,?,?)',((i,i%1000,(i*13)%10000) for i in range(n))); c.commit()
  if indexed: c.execute('CREATE INDEX idx_customer ON orders(customer)'); c.commit()
  plan=c.execute('EXPLAIN QUERY PLAN SELECT count(*),coalesce(sum(amount),0) FROM orders WHERE customer=?',(1,)).fetchall(); c.close()
  c=sqlite3.connect(db); p.cpu_percent(None); mem0=p.memory_info().rss; io0=p.io_counters(); ct0=p.cpu_times(); start=time.perf_counter(); answers=[]; c.execute('BEGIN')
  for i,(op,key) in enumerate(ops):
   if op=='r': answers.append(c.execute('SELECT count(*),coalesce(sum(amount),0) FROM orders WHERE customer=?',(key,)).fetchone())
   else: c.execute('INSERT INTO orders VALUES(?,?,?)',(n+i,key,i*7))
  c.commit(); c.close(); wall=time.perf_counter()-start; ct=p.cpu_times(); io=p.io_counters(); mem=p.memory_info().rss
  c=sqlite3.connect(db); rows=c.execute('SELECT id,customer,amount FROM orders ORDER BY id').fetchall(); c.close(); assert len(rows)==n+sum(op=='w' for op,_ in ops)
  digest=hashlib.sha256(repr((answers,rows)).encode()).hexdigest()
  return dict(n=n,read_pct=read_pct,index=indexed,affinity=pinned,cpu=selected,allowed_cpus=allowed,seconds=wall,throughput=len(ops)/wall,user_seconds=ct.user-ct0.user,system_seconds=ct.system-ct0.system,cpu_percent=100*((ct.user-ct0.user)+(ct.system-ct0.system))/wall,rss_before=mem0,rss_after=mem,read_bytes=io.read_bytes-io0.read_bytes,write_bytes=io.write_bytes-io0.write_bytes,sha256=digest,plan=plan,reads=sum(x[0]=='r' for x in ops),writes=sum(x[0]=='w' for x in ops))
if __name__=='__main__':
 if len(sys.argv)>1 and sys.argv[1]=='worker':
  print(json.dumps(worker(int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5])))); sys.exit()
 cases=[(n,r,i,a,k) for n in (20000,100000) for r in (50,90) for i in (0,1) for a in (0,1) for k in range(1,6)]; random.Random(99).shuffle(cases); records=[]
 for n,r,i,a,k in cases:
  try:
   out=subprocess.check_output([sys.executable,__file__,'worker',str(n),str(r),str(i),str(a)],text=True); rec=json.loads(out); rec['repeat']=k; records.append(rec)
  except (subprocess.CalledProcessError,OSError) as e: print('FAILED',n,r,i,a,k,e,file=sys.stderr); raise
 for n in (20000,100000):
  for r in (50,90): assert len({x['sha256'] for x in records if x['n']==n and x['read_pct']==r})==1
 summary=[]
 for n in (20000,100000):
  for r in (50,90):
   base=statistics.mean(x['seconds'] for x in records if x['n']==n and x['read_pct']==r and not x['index'] and not x['affinity'])
   for i in (0,1):
    for a in (0,1):
     g=[x for x in records if x['n']==n and x['read_pct']==r and x['index']==i and x['affinity']==a]; m=statistics.mean(x['seconds'] for x in g)
     summary.append(dict(n=n,read_pct=r,index=i,affinity=a,mean=m,median=statistics.median(x['seconds'] for x in g),stdev=statistics.stdev(x['seconds'] for x in g),throughput=300/m,speedup=base/m,cpu_percent=statistics.mean(x['cpu_percent'] for x in g)))
 out={'environment':{'platform':platform.platform(),'processor':platform.processor(),'python':sys.version,'sqlite':sqlite3.sqlite_version,'logical_cpus':os.cpu_count(),'psutil':psutil.__version__,'affinity':psutil.Process().cpu_affinity()},'records':records,'summary':summary,'timing':'300 mixed operations, transaction commit and connection close; setup and verification excluded; DELETE journal default','seed':271828,'order_seed':99}
 dest=pathlib.Path(os.environ.get('MIXED_OUTPUT', ROOT/'data'/'mixed-affinity-results.json')); dest.parent.mkdir(parents=True,exist_ok=True); dest.write_text(json.dumps(out,indent=2),encoding='utf-8'); print(json.dumps(summary,indent=2))
