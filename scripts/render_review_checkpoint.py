"""Immutable matched-camera review renders from saved source files."""
import bpy,sys,json,hashlib,os
from pathlib import Path
R=Path(__file__).resolve().parents[1];args=sys.argv[sys.argv.index('--')+1:];era=args[0];s=bpy.context.scene
HELPER_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
LIGHTING_CODE=(R/'scripts/render_lighting.py').read_bytes();LIGHTING_SHA=hashlib.sha256(LIGHTING_CODE).hexdigest()
exec(compile(LIGHTING_CODE,'render_lighting.py','exec'))
out=R/'renders'/os.environ.get('STATION_REVIEW_DIR','review04');out.mkdir(parents=True,exist_ok=True)
s.cycles.samples=20;s.render.resolution_x=1200;s.render.resolution_y=816;s.render.resolution_percentage=100
sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
for view in args[1:]:
 p=out/f'{era}_{view}.png'
 if p.exists():print('Preserving existing immutable image',p,flush=True);continue
 s.camera=bpy.data.objects['Camera '+view];apply_camera_fill_mode(s,view);s.render.filepath=str(p);bpy.ops.render.render(write_still=True)
 (out/f'{era}_{view}.json').write_text(json.dumps(dict(era=era,view=view,source_blend_sha256=sha,build_code_sha256=s.get('build_code_sha256'),saved_component_sha256=s.get('component_sha256'),render_helper_sha256=HELPER_SHA,render_lighting_sha256=LIGHTING_SHA,runtime_lighting_mode=s.get('lighting_mode'),light_state=[dict(name=o.name,type=o.data.type,energy=o.data.energy,color=list(o.data.color),location=list(o.location),rotation_euler=list(o.rotation_euler),specular_factor=o.data.specular_factor,transmission_factor=o.data.transmission_factor) for o in s.objects if o.type=='LIGHT'],runtime_exposure=s.view_settings.exposure,exposure_note=s.get('render_exposure_note'),camera_location=list(s.camera.location),camera_euler=list(s.camera.rotation_euler),lens_mm=s.camera.data.lens,resolution=[1200,816],samples=20,status='Architectural/material review WIP; not photoreal or complete-as-built certification',scope_limits='See per-space coverage and source-gap manifests'),indent=2))
 print('REVIEW IMAGE SAVED',p,flush=True)
