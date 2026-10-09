"""Original full-room PBR assembly; flush inlays, no copyrighted source image pixels."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];N=3072;out=ROOT/'assets/textures/great_hall_floor_2026';out.mkdir(parents=True,exist_ok=True)
y,x=np.mgrid[0:N,0:N].astype(np.float32);wx=x/N*71.0184-35.5092;wy=y/N*31.6992
ix=((wx/4%1)*2048).astype(int);iy=((wy/4%1)*2048).astype(int)
def sample(name):
 im=np.asarray(Image.open(ROOT/'assets/textures'/name/'basecolor.png').convert('RGB'),dtype=np.float32);hh,ww=im.shape[:2];repeat=1.2 if name=='generated_rose_marble_v1' else 4.0
 xx=((wx/repeat%1)*ww).astype(int);yy=((wy/repeat%1)*hh).astype(int)
 return im[yy,xx]/255
base=sample('generated_rose_marble_v1');pale=sample('pale_marble');terra=sample('terrazzo')
bands=np.zeros((N,N),bool)
for direction in [-1,1]:
 f=(wy-direction*wx+80)%2.30;bands|=(f<.09)|(f>2.21)
for yy in [4.0,5.1,26.6,27.7]:bands|=abs(wy-yy)<.08
base[bands]=pale[bands]
repairs=np.zeros((N,N),bool)
for xx in [-20,0,20]:
 for yy in [8.3,23.4]:repairs|=(abs(wx-xx)<7.15)&(abs(wy-yy)<.85)
base[repairs]=terra[repairs]
rough=np.full((N,N),.24,np.float32);rough[repairs]=.28
# Submillimeter joint lines are represented in color, not misleading centimeter-high geometry.
for d in [-1,1]:
 f=(wy-d*wx+80)%2.30;mask=((f<.008)|(f>2.292))&(~repairs);base[mask]*=.78
Image.fromarray((np.clip(base,0,1)*255).astype('uint8')).save(out/'basecolor.png')
Image.fromarray((rough*255).astype('uint8')).save(out/'roughness.png')
Image.new('RGB',(N,N),(128,128,255)).save(out/'normal.png')
Image.fromarray(np.full((N,N),32768,dtype='uint16')).save(out/'height.png')
(out/'provenance.json').write_text(json.dumps(dict(origin='Original procedural assembly from original generated marble and terrazzo maps',rights='Original project-generated assembly; no third-party photograph used',pixels=[N,N],mapped_room_m=[71.0184,31.6992],limitations='Photograph-informed pattern and benchmark repairs; not a measured floor-stone inventory'),indent=2))
print('Flush floor assembly',out)
