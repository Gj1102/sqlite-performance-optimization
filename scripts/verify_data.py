import json,statistics,math,pathlib
root=pathlib.Path(__file__).resolve().parents[1]
for filename in ('sqlite-results.json','factorial-results.json','mixed-affinity-results.json'):
 d=json.loads((root/'data'/filename).read_text(encoding='utf-8')); records=d['records']; summaries=d['summary']
 for s in summaries:
  if filename=='mixed-affinity-results.json':
   g=[x for x in records if all(x[k]==s[k] for k in ('n','read_pct','index','affinity'))]; reported=s['mean']
  elif filename=='factorial-results.json':
   g=[x for x in records if all(x[k]==s[k] for k in ('transaction','journal'))]; reported=s['mean_seconds']
  else:
   g=[x for x in records if all(x[k]==s[k] for k in ('workload','variant'))]; reported=s['mean_seconds']
  assert len(g)==5 and math.isclose(statistics.mean(x['seconds'] for x in g),reported,rel_tol=1e-10), (filename,s)
  assert math.isclose(statistics.stdev(x['seconds'] for x in g),s['stdev' if filename.startswith('mixed') else 'stdev_seconds'],rel_tol=1e-10)
 if filename=='mixed-affinity-results.json':
  for n in (20000,100000):
   for r in (50,90): assert len({x['sha256'] for x in records if x['n']==n and x['read_pct']==r})==1
 print(filename, len(records), 'records; means and standard deviations verified')
