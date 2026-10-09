"""Definitions only. Optional bounded integration into a NEW station revision.
The caller owns full-scene QA and a new destination; this helper never saves.
It is not executed by the isolated study build.
"""
import json
from pathlib import Path

def apply_west_portal_detail(era,study_directory):
 import bpy
 era=str(era)
 if era not in ('2017','2026'):raise ValueError('Supported eras are2017 and2026')
 root=Path(study_directory);report=json.loads((root/f'qa_{era}.json').read_text())
 if not all(report['checks'].values()) or report['glb']['errors']:raise RuntimeError('Study acceptance failed')
 names=[row['name'] for row in report['new_geometry']]
 # No context, floors, existing glazing or old wall meshes are appended.
 if not names or not all(n.startswith(('West small feature ','West portal ','West restored lower ')) for n in names):raise RuntimeError('Unexpected integration scope')
 if any(n in bpy.data.objects for n in names):raise RuntimeError('Detail already present; refuse duplicate integration')
 old=bpy.data.objects.get('concourse west small opening profiled lintel')
 if old is None or old.type!='MESH':raise RuntimeError('Exact inherited lintel replacement target missing')
 expected_material=f'Concourse terracotta dressings {era}'
 if not any(m and m.name==expected_material for m in old.data.materials):raise RuntimeError('Era/target material mismatch')
 source=root/f'concourse_west_portal_{era}_STUDY.blend'
 with bpy.data.libraries.load(str(source),link=False) as (a,b):
  if set(names)-set(a.objects):raise RuntimeError('Study model is missing requested detail objects')
  b.objects=names
 collection=bpy.data.collections.new('05 CONCOURSE | west portal source-supported relief study');bpy.context.scene.collection.children.link(collection)
 for ob in b.objects:
  collection.objects.link(ob)
  # Prefer already-present exact-era material identities after append.
  for slot in ob.material_slots:
   m=slot.material
   if m:
    stem=m.name.rsplit('.',1)[0]
    if stem in bpy.data.materials and stem in [f'Concourse terracotta dressings {era}',f'Concourse retained portal metal {era}']:slot.material=bpy.data.materials[stem]
 bpy.data.objects.remove(old,do_unlink=True)
 # Library links must be evaluated before any caller reads matrix_world.
 bpy.context.view_layer.update()
 result={'era':era,'added_objects':len(names),'removed_objects':['concourse west small opening profiled lintel'],'changed_floor_or_opening_controls':False,'source_study':str(source),'full_scene_qa_required':True}
 bpy.context.scene['west_portal_detail_study']=json.dumps(result)
 return result
