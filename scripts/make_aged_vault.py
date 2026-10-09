"""Unique full-hall weathering atlas, original interpretation rather than repeating damage.
Not a2017 damage survey. No reference photograph pixels enter the output.
"""
from pathlib import Path
import numpy as np
from scipy.ndimage import zoom,gaussian_filter
from PIL import Image
import json
r=Path(__file__).resolve().parents[1];out=r/'assets/textures/aged_vault_unique';out.mkdir(parents=True,exist_ok=True)
W=4096;H=2048;yy,xx=np.mgrid[0:H,0:W].astype(np.float32);wx=xx/W*71.0184-35.5092;wy=yy/H*31.6992
rng=np.random.default_rng(19882017)
def field(h,w):
 a=zoom(rng.normal(size=(h,w)).astype(np.float32),(H/h,W/w),order=3)[:H,:W];return (a-a.mean())/(a.std()+1e-6)
coarse=field(7,18);fine=field(19,72);streak=gaussian_filter(field(80,100),(12,1))
alpha=np.clip(.27+coarse*.19+fine*.08+streak*.06,0,.78)
folder=r/'assets/textures/guastavino_restored'
def sample(file):
 im=np.asarray(Image.open(folder/file));h,w=im.shape[:2];ix=((wx/4%1)*w).astype(int);iy=((wy/4%1)*h).astype(int);return im[iy,ix]
base=sample('basecolor.png').astype(np.float32)/255
base=base*(1-alpha[:,:,None])+np.array([.13,.12,.085])[None,None,:]*alpha[:,:,None]
Image.fromarray((np.clip(base,0,1)*255).astype('uint8')).save(out/'basecolor.png')
Image.fromarray((np.clip(.74+alpha*.15,0,1)*255).astype('uint8')).save(out/'roughness.png')
Image.fromarray(sample('normal.png')).save(out/'normal.png')
Image.fromarray(sample('height.png')).save(out/'height.png')
(out/'provenance.json').write_text(json.dumps(dict(origin='Original procedural ceramic base plus unique full-room weathering interpretation',rights='Original project asset; no reference photograph pixels used',physical_mapping_m=[71.0184,31.6992],pixels=[W,H],limits=['Not an exact2017 stain/loss inventory','Historic material class is source-supported; location/intensity of stains is artistic','No invented image-generation damage used as architectural evidence']),indent=2))
print('Unique full-hall vault weather atlas saved')
