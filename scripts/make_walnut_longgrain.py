"""Original seamless walnut field for carved interior woodwork; not a site scan."""
from pathlib import Path
import numpy as np,json
from PIL import Image
from scipy.ndimage import gaussian_filter
r=Path(__file__).resolve().parents[1];o=r/'assets/textures/original_walnut_longgrain';o.mkdir(parents=True,exist_ok=True)
n=2048;y,x=np.mgrid[0:n,0:n].astype(np.float32)/n;rng=np.random.default_rng(3019)
warp=.011*np.sin(2*np.pi*y)+.005*np.sin(4*np.pi*y+2.8)
phase=x+warp
wave=(np.sin(2*np.pi*phase*39)+.45*np.sin(2*np.pi*phase*81+.8)+.23*np.sin(2*np.pi*phase*137+2.1))
pores=np.maximum(0,np.sin(2*np.pi*phase*173+.04*np.sin(y*2*np.pi*3))-.78)
coarse=gaussian_filter(rng.normal(size=(n,n)).astype('float32'),(80,6),mode='wrap');coarse/=coarse.std()
lin=np.array([.041,.018,.0075])[None,None,:]*(1+wave[:,:,None]*.075+coarse[:,:,None]*.055-pores[:,:,None]*.12)
srgb=np.where(lin<=.0031308,lin*12.92,1.055*lin**(1/2.4)-.055)
rough=np.clip(.30+wave*.012+coarse*.015,.24,.38);h=.5+wave*.001-pores*.003
Image.fromarray((np.clip(srgb,0,1)*255).astype('uint8')).save(o/'basecolor.png');Image.fromarray((rough*255).astype('uint8')).save(o/'roughness.png');Image.fromarray((h*65535).astype('uint16')).save(o/'height.png')
dy,dx=np.gradient(h);nn=np.stack([-dx*4,dy*4,np.ones_like(h)],2);nn/=np.sqrt((nn*nn).sum(2))[:,:,None]
Image.fromarray(((nn*.5+.5)*255).astype('uint8')).save(o/'normal.png')
(o/'provenance.json').write_text(json.dumps(dict(origin='Original mathematical walnut long-grain, seamless periodic field',repeat_m=1.0,grain='longitudinal UV-v, authored per-face alignment',physical_basis='Artistic approximation of photographed dark restored walnut, not measured grain or reflectance',rights='Original project surface; no source image pixels',normal='OpenGL +Y, conservative micrograin'),indent=2))
print(o)
