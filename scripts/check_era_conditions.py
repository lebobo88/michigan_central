"""Source-supported era differences checked on actual saved geometry."""
import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from artifact_provenance import file_sha256
E=sys.argv[sys.argv.index('--')+1];s=bpy.context.scene;assert E==s['era'];old=E=='2017';checks=[]
def count(predicate):return sum(o.type=='MESH' and predicate(o) for o in s.objects)
def check(name,value,expected):
 checks.append(dict(condition=name,actual=value,expected=expected));assert value==expected,(name,value,expected)
for prefix in ['concourse restored individual glazing panels','Passenger ramp restored glazed roof','hall chandelier pendant vase','hall alcove restored sash glazing']:
 check(prefix+' present',count(lambda o:o.name.startswith(prefix))>0,not old)
check('documented2026 mixed canopy roof present',count(lambda o:o.name.startswith('2026 north canopy roof_opaque'))>0,not old)
check('retained canopy wall bosses present',count(lambda o:o.name.startswith(E+' north canopy anchor'))>0,True)
check('2015 replacement tower windows present',count(lambda o:o.name.startswith('tower regular replacement window insulating glazing'))>0,True)
check('2023 north park geometry present',count(lambda o:o.get('space','').startswith('00C ROOSEVELT PARK'))>0,not old)
check('bounded historical forecourt present',count(lambda o:o.get('space','').startswith('00F 2017 FORECOURT'))>0,old)
reliefs=json.loads(s.get('hall_cartouche_metadata','[]'));check('modeled substantial cartouches',len(reliefs),1 if old else 6)
if old:
 cov=json.loads(s.get('hall_cartouche_coverage','[]'));check('cartouche six-bay condition schedule',len(cov),6)
 check('documented lost south cartouches',sum(c['state']=='documented absence' for c in cov),2)
check('unobserved southern structure is not silently aligned',any(o.get('export_coverage_marker') and 'Southern platform' in o.name for o in s.objects),True)
report=dict(era=E,source_blend_sha256=file_sha256(bpy.data.filepath),checks=checks,passed=True,scope='Presence/absence regression only; no complete room or per-pane inventory certification',sources='See hall_lunettes/2017_cartouche_schedule.json, period source ledger and2017 roof-condition evidence')
(R/'manifests'/f'era_condition_checks_{E}.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
