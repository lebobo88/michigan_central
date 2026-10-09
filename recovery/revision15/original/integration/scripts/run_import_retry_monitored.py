"""One Blender child; record phase logs plus process RSS/exit signal via wait4."""
import subprocess,os,sys,time,json
from pathlib import Path
O=Path(__file__).resolve().parents[1];R=O.parents[1];binary=R.parent/'3d-tools/apps/blender-5.2.2-linux-x64/blender';log=O/'logs/import_review_2026_retry.log';monitor=O/'manifests/import_2026_process_monitor.jsonl';start=time.time()
cmd=[str(binary),'-b','-t','2','--python',str(O/'scripts/import_and_render.py'),'--','--era','2026','--mode','import','--render','--samples','16','--width','1000']
with log.open('w') as out,monitor.open('w') as timeline:
 p=subprocess.Popen(cmd,stdout=out,stderr=subprocess.STDOUT,cwd=R)
 while True:
  pid,status,usage=os.wait4(p.pid,os.WNOHANG)
  if pid:
   code=os.waitstatus_to_exitcode(status);p.returncode=code;break
  try:
   lines=Path(f'/proc/{p.pid}/status').read_text().splitlines();proc={x.split(':',1)[0]:x.split(':',1)[1].strip() for x in lines if x.startswith(('VmRSS:','VmHWM:','VmPeak:','Threads:'))};mem=[x for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')]
   row={'elapsed_s':round(time.time()-start,1),'process':proc,'host_mem_available':mem};timeline.write(json.dumps(row)+'\n');timeline.flush()
  except FileNotFoundError:pass
  time.sleep(3)
 report={'command':cmd,'exit_code':code,'signal':-code if code<0 else None,'elapsed_s':round(time.time()-start,2),'maximum_resident_set_kib':usage.ru_maxrss,'user_cpu_s':usage.ru_utime,'system_cpu_s':usage.ru_stime,'threads_requested':2,'only_one_child':True,'quality_unchanged':True,'geometry_hidden_removed_or_decimated':False,'textures_resized':False}
 (O/'manifests/import_2026_retry_process_result.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
 if code!=0:raise SystemExit(code if code>0 else 128-code)
 p=O/'manifests/import_review_2026.json';d=json.loads(p.read_text());assert d['passed'] and len(d['renders'])==2
