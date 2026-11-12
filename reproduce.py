import os,sys,subprocess,pathlib,datetime,importlib.util
root=pathlib.Path(__file__).resolve().parent
for package in ('psutil','matplotlib'):
 if not importlib.util.find_spec(package): sys.exit('缺少依赖：'+package+'；请运行 python -m pip install -r requirements.txt')
if not hasattr(__import__('psutil').Process(),'cpu_affinity'): sys.exit('当前系统不支持 CPU 亲和性；其他历史结果仍可查看。')
run=root/'runs'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'); run.mkdir(parents=True)
env=os.environ.copy(); env['MIXED_OUTPUT']=str(run/'mixed-affinity-results.json'); env['FIGURE_OUTPUT']=str(run/'figures'); env['MPLCONFIGDIR']=str(run/'mpl-cache')
for script in ('scripts/verify_data.py','scripts/mixed_experiment.py','scripts/figures.py'):
 subprocess.run([sys.executable,str(root/script)],cwd=root,env=env,check=True)
print('新结果：',run,'；历史数据和图表未覆盖。')
