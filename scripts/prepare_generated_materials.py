"""PBR support maps for actual imagegen outputs. Color remains unchanged.
Roughness/height/normal are low-amplitude ARTISTIC INFERENCES, never scanned or measured.
"""
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
import json,shutil,hashlib
r=Path(__file__).resolve().parents[1];rows=[]
for name,src,repeat,rough in [('generated_mankato_v1','mankato_basecolor_v1.png',1.5,.56),('generated_rose_marble_v1','rose_marble_basecolor_v1.png',1.2,.23),('generated_walnut_herringbone_v1','walnut_herringbone_v1.png',.65,.31)]:
 p=r/'assets/generated_originals'/src;o=r/'assets/textures'/name;o.mkdir(parents=True,exist_ok=True);shutil.copy2(p,o/'basecolor.png')
 rgb=np.asarray(Image.open(p).convert('RGB'),np.float32)/255;h,w=rgb.shape[:2];gray=rgb.mean(2);detail=gray-gaussian_filter(gray,4,mode='wrap')
 # Stone grain inference is conservative. Polished marble receives a flat normal intentionally.
 if 'mankato' in name:
  height=np.clip(.5+detail*.22,.4,.6);gy,gx=np.gradient((height-.5)*.0006)
  norm=np.stack([-gx/(repeat/w),gy/(repeat/h),np.ones_like(gray)],2);norm/=np.sqrt((norm*norm).sum(2))[:,:,None]
 else:height=np.full_like(gray,.5);norm=np.zeros((*gray.shape,3),np.float32);norm[:,:,2]=1
 roughness=np.clip(rough-detail*.08,rough-.035,rough+.035)
 Image.fromarray((roughness*255).astype('uint8')).save(o/'roughness.png')
 Image.fromarray((height*65535).astype('uint16')).save(o/'height.png')
 Image.fromarray(((norm*.5+.5)*255).astype('uint8')).save(o/'normal.png')
 edge_h=float(np.abs(rgb[:,0]-rgb[:,-1]).mean());edge_v=float(np.abs(rgb[0]-rgb[-1]).mean());near=float(np.abs(rgb[:,1:]-rgb[:,:-1]).mean())
 rows.append(dict(material=name,basecolor_origin='Actual built-in image_gen output, original artwork, no reference photograph supplied',basecolor_original_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),pixels=[w,h],physical_repeat_m=repeat,roughness_origin='Artistic inference, not measured',height_origin='Conservative inferred micrograin' if 'mankato' in name else 'Intentionally flat polished surface; color veins are not height',normal_convention='OpenGL +Y',normal_origin='Derived only from the conservative height estimate',seam_diagnostics=dict(horizontal_edge_mean_difference=edge_h,vertical_edge_mean_difference=edge_v,mean_adjacent_pixel_difference=near),warnings=['Generated swatch is not a station scan or evidence of actual fabric','Seamlessness must be judged in actual mapped render','No true displacement enabled at this LOD']))
(r/'manifests/generated_materials.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
