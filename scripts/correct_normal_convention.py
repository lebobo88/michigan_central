"""Regenerate legacy authored normal channels from their own height maps.
Pillow rows descend while Blender/OpenGL UV-v ascends, hence tangent normalY=+image dH/drow.
No color asset or source photograph is edited by this technical channel conversion.
"""
from pathlib import Path
import json,numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];records=[]
manifest=json.loads((R/'assets/textures/material_manifest.json').read_text())
for q in manifest:
 name=q['material']
 if name=='guastavino_restored':continue # replaced by a newer, already-correct herringbone field
 folder=R/'assets/textures'/name
 h=np.asarray(Image.open(folder/'height.png'),dtype=np.float32)/65535
 dy,dx=np.gradient(h);n=np.stack([-dx*20,dy*20,np.ones_like(h)],2);n/=np.sqrt((n*n).sum(2))[:,:,None]
 Image.fromarray(((n*.5+.5)*255).astype('uint8')).save(folder/'normal.png');records.append(name)
for folder in (R/'manifests/current_fitouts/materials').iterdir():
 if not folder.is_dir() or not(folder/'height.png').exists():continue
 h=np.asarray(Image.open(folder/'height.png'),dtype=np.float32)/65535
 dy,dx=np.gradient(h);n=np.stack([-dx*8,dy*8,np.ones_like(h)],2);n/=np.sqrt((n*n).sum(2))[:,:,None]
 Image.fromarray(((n*.5+.5)*255).astype('uint8')).save(folder/'normal.png');records.append(str(folder.relative_to(R)))
(R/'manifests/normal_channel_convention.json').write_text(json.dumps(dict(normal_convention='OpenGL tangent space +Y, UV-v upwards',image_rows='downwards; technical derivative conversion accounted for',legacy_channels_regenerated=records,newer_channels='Generated-stone, brick_v2, fullhall2017, herringbone, and longgrain scripts already use positive image-row gradient for green channel',limitations='Normals derive from authored/inferred height maps, not measured site microgeometry'),indent=2))
print('Regenerated',len(records),'normal channels')
