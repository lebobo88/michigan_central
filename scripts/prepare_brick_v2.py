from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
r=Path(__file__).resolve().parents[1];N=2048;rng=np.random.default_rng(21831917)
y,x=np.mgrid[0:N,0:N].astype(np.float32)/N;row=np.floor(y*24).astype(int);col=np.floor(x*8+(row%2)*.5).astype(int)%8
bx=(x*8+(row%2)*.5)%1;by=(y*24)%1;joint=(bx<.04)|(by<.12)
coarse=gaussian_filter(rng.normal(size=(N,N)).astype(np.float32),9,mode='wrap');coarse/=coarse.std();fine=rng.normal(size=(N,N)).astype(np.float32)
cell=rng.uniform(-.055,.055,(24,8))[row,col];height=.56+coarse*.012+fine*.002-joint*.12
for name,base in [('brick_v2_common',[.36,.22,.135]),('brick_v2_buff',[.56,.49,.34])]:
 o=r/'assets/textures'/name;o.mkdir(parents=True,exist_ok=True)
 c=np.array(base)[None,None,:]+(cell+coarse*.012+fine*.003)[:,:,None];c[joint]=[.42,.405,.37]
 Image.fromarray((np.clip(c,0,1)*255).astype('uint8')).save(o/'basecolor.png')
 Image.fromarray((np.clip(.78+coarse*.015,0,1)*255).astype('uint8')).save(o/'roughness.png')
 Image.fromarray((np.clip(height,0,1)*65535).astype('uint16')).save(o/'height.png')
 gy,gx=np.gradient(height);normal=np.stack([-gx*18,gy*18,np.ones_like(height)],2);normal/=np.sqrt((normal*normal).sum(2))[:,:,None]
 Image.fromarray(((normal*.5+.5)*255).astype('uint8')).save(o/'normal.png')
 (o/'provenance.json').write_text(json.dumps(dict(origin='Original deterministic running-bond material',physical_repeat_m=1.7,nominal_module_m=[1.7/8,1.7/24],mortar_m_approx=.0085,warning='Idealized plausible brick scale, not measured station brick dimensions',normal_convention='OpenGL +Y'),indent=2))
print('Brick v2 materials saved')
