"""Deterministic original procedural materials, never derived from reference pixels."""
from pathlib import Path
import numpy as np
from PIL import Image
P=Path(__file__).parent/'assets';P.mkdir(exist_ok=True)
r=np.random.default_rng(4815);n=1024;y,x=np.mgrid[0:n,0:n]/n
warp=x+.005*np.sin(y*18)+.011*np.sin(y*4.2)+.003*np.sin(y*44+x*3)
gr=np.sin(warp*890+np.sin(y*15)*.4)+.4*np.sin(warp*2013)
pores=np.maximum(0,np.sin(warp*3820)-.72)*np.maximum(0,np.sin(y*190+warp*83))
knot=np.sin(np.sqrt(((x-.42)*2.4)**2+((y-.38)*.38)**2)*410)*np.exp(-((x-.42)/.1)**2-((y-.38)/.36)**2)
noise=r.normal(0,1,(n,n));field=gr*4.6-pores*11+noise*1.4+knot*5.4+7*np.sin(warp*151)+5*np.sin(warp*66+y*2)+3*np.sin(warp*331)
for name,base in [('oak',(113,80,53)),('panel_walnut',(72,48,32))]:
 im=np.clip(np.array(base)[None,None,:]+field[:,:,None]*np.array([1,.85,.55]),0,255).astype('uint8');Image.fromarray(im).save(P/(name+'_color.png'))
 rough=np.clip(160+field*1.2,115,205).astype('uint8');Image.fromarray(rough).save(P/(name+'_rough.png'))
n=512;y,x=np.mgrid[0:n,0:n];weave=((x%4==0)*4+(y%4==0)*5+r.normal(0,1.5,(n,n)))
for name,base in [('bluegray',(106,119,123)),('wine',(124,25,57)),('tan',(164,108,59)),('green',(29,81,58)),('rug_blue',(63,83,100)),('rug_green',(88,92,64)),('rug_gray',(91,83,86)),('rug_brown',(65,43,35))]:
 Image.fromarray(np.clip(np.array(base)[None,None,:]+weave[:,:,None],0,255).astype('uint8')).save(P/(name+'_color.png'))

# Original ashlar coursing bitmap; photographed material class, never image projection.
from PIL import ImageDraw
im=Image.new('RGB',(1024,1024),(164,147,117));dr=ImageDraw.Draw(im);rng=np.random.default_rng(482)
for row in range(9):
 yy0=round(row*1024/9);yy1=round((row+1)*1024/9);xx=-int(rng.uniform(0,240))
 while xx<1024:
  wid=int(rng.uniform(230,360));v=rng.normal(0,5);col=tuple(int(t+v) for t in (188,170,137));dr.rectangle((xx+1,yy0+1,xx+wid,yy1),fill=col);xx+=wid
a=np.asarray(im,dtype=float);a+=rng.normal(0,1.3,a.shape[:2])[:,:,None];Image.fromarray(np.clip(a,0,255).astype('uint8')).save(P/'cream_stone_color.png')
