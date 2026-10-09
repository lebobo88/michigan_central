"""Transient close QA camera; no saved source or authored geometry is changed."""
import bpy,hashlib
from pathlib import Path
from mathutils import Vector
name='Camera north_entry_upper_detail';scene=bpy.context.scene
if name in bpy.data.objects:raise RuntimeError('Do not silently replace an existing camera')
data=bpy.data.cameras.new('North upper facade source review');ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob)
ob.location=(0,-22,10);ob.rotation_euler=(Vector((0,-.4,14.8))-ob.location).to_track_quat('-Z','Y').to_euler();data.lens=52;data.clip_end=1000
ob['qa_camera_only']=True;ob['purpose']='Actual integrated capital/arch/cornice review; source geometry and support datums unchanged'
scene['runtime_camera_script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
