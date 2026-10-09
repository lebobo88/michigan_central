"""Original mathematical textures, no study photographs loaded or used as pixels."""
from pathlib import Path
from PIL import Image
import numpy as np
P=Path(__file__).resolve().parent/'materials';P.mkdir(exist_ok=True)
n=1024;y,x=np.mgrid[0:n,0:n]/n;rng=np.random.default_rng(617)
def noise(scale):
 # Fourier filtering makes the texture and its derivatives periodic at tile edges.
 raw=rng.normal(size=(n,n));fy=np.fft.fftfreq(n)[:,None]*n;fx=np.fft.rfftfreq(n)[None,:]*n
 filt=np.exp(-.5*(fx*fx+fy*fy)/(scale*.38)**2)
 field=np.fft.irfft2(np.fft.rfft2(raw)*filt,s=(n,n));field-=field.mean()
 return np.clip(field/(field.std()+1e-9)*.16,-.5,.5)
def save(name,col,h,rough):
 d=P/name;d.mkdir(exist_ok=True);Image.fromarray(np.uint8(np.clip(col,0,1)*255)).save(d/'basecolor.png')
 Image.fromarray(np.uint8(np.clip(rough,0,1)*255)).save(d/'roughness.png')
 dy,dx=np.gradient(h);normal=np.stack((-dx*8,dy*8,np.ones_like(h)),axis=-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
 Image.fromarray(np.uint8((normal*.5+.5)*255)).save(d/'normal.png');Image.fromarray(np.uint16(np.clip(h,0,1)*65535)).save(d/'height.png')
a=noise(6);b=noise(36);c=noise(180);w=np.sin(2*np.pi*(y*10+.35*np.sin(x*2*np.pi)+a*.8));vein=np.exp(-((w+.78)/.10)**2);tone=.91-.12*vein+.025*b+.007*c
save('yl_pale_counter',np.stack([tone*.99,tone*.99,tone],axis=-1),.5+.07*vein+.025*c,np.clip(.28+.10*b,.1,1))
a=noise(5);b=noise(32);c=noise(280);tone=.53+.21*a+.085*b+.035*c
save('yl_polished_concrete',np.stack([tone*1.04,tone*1.02,tone*.93],axis=-1),.5+.1*b+.1*c,np.clip(.46+.18*b+.09*c,0,1))
a=noise(9);b=noise(70);c=noise(400);tone=.62+.14*a+.10*b+.09*c
save('yl_salvaged_ocher',np.stack([tone*1.06,tone*.80,tone*.44],axis=-1),.5+.20*b+.18*c,np.clip(.53+.2*b+.12*c,0,1))
