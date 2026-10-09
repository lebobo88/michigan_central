"""Semantic lightweight export. Preserve envelope and dimensions, omit micro-detail.
Run Blender -b source.blend --python this.py -- ERA.
The LOD is a review/preview asset, not a replacement for authored source.
"""
import bpy,sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];era=sys.argv[sys.argv.index('--')+1]
removed=[];before=sum(len(o.data.vertices) for o in bpy.context.scene.objects if o.type=='MESH')
keywords=['individual leaves','rosette','coffer border','acanthus','foliate','standing roof seams','marquee bulbs','chandelier radial arms','chandelier basket ribs','plaster rubble','paint strokes','herringbone inlay','window transoms','tower window frames','chandelier lamps','Yellow Light physical perforated ceiling panels','Yellow Light curved brass mesh screen wires','West corridor glazed white subway tiles','West connecting corridor original hex-tile geometry','hall arch continuous molded fillets','relief beads','curled horns','radial leaves','curled petals','West entablature carved palmette frieze']
for ob in list(bpy.context.scene.objects):
 if ob.type=='MESH' and any(k in ob.name for k in keywords):removed.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
# Viewer texture budget. Blender source retains full2048px source maps.
for im in bpy.data.images:
 if im.source=='FILE' and max(im.size)>512:
  factor=512/max(im.size);im.scale(max(1,round(im.size[0]*factor)),max(1,round(im.size[1]*factor)))
path=ROOT/'exports'/f'michigan_central_{era}_preview_lod.glb'
bpy.ops.object.select_all(action='DESELECT')
for ob in bpy.context.scene.objects:
 if (ob.type=='MESH' and ob.name!='landscape context') or ob.get('export_group') or ob.get('export_coverage_marker'):ob.select_set(True)
bpy.ops.export_scene.gltf(use_selection=True,filepath=str(path),export_format='GLB',export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_extras=True)
sys.path.insert(0,str(ROOT/'scripts'))
from repair_glb_tangents import repair_glb_tangents
repair_glb_tangents(path,ROOT/'manifests'/f'tangent_repair_{era}_preview_lod.json')
after=sum(len(o.data.vertices) for o in bpy.context.scene.objects if o.type=='MESH')
(ROOT/'manifests'/f'lod_{era}.json').write_text(json.dumps(dict(era=era,kind='semantic preview LOD',texture_resolution=512,vertices_before=before,vertices_after=after,removed_detail_objects=removed,limitations='Micro-detail omitted. Shared historic envelope retained; not a separate survey.'),indent=2))
print('LOD SAVED',path)
