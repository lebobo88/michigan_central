"""Authored material interpretation of dated 2017 photographs; no copied pixels.
The maps preserve material scale and historic joints; they are NOT damage surveys.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, zoom
R=Path(__file__).resolve().parents[1];rng=np.random.default_rng(171006)
def noise(n,grid):
 q=rng.normal(size=(grid,grid)).astype(np.float32);q=zoom(q,(n/grid,n/grid),order=2,mode='wrap')[:n,:n];return q/(q.std()+1e-6)
def output(name,c,rough,h,repeat,notes):
 o=R/'assets/textures'/name;o.mkdir(parents=True,exist_ok=True)
 Image.fromarray((np.clip(c,0,1)*255).astype('uint8')).save(o/'basecolor.png')
 Image.fromarray((np.clip(rough,0,1)*255).astype('uint8')).save(o/'roughness.png')
 Image.fromarray((np.clip(h,0,1)*65535).astype('uint16')).save(o/'height.png')
 dy,dx=np.gradient(h);nn=np.stack([-dx*3,dy*3,np.ones_like(h)],2);nn/=np.sqrt((nn*nn).sum(2))[:,:,None]
 Image.fromarray(((nn*.5+.5)*255).astype('uint8')).save(o/'normal.png')
 (o/'provenance.json').write_text(json.dumps(dict(origin='Original procedural project surface, no reference-image pixels',physical_repeat_m=repeat,normal='OpenGL +Y',evidence_basis='May2017 Grand Hall photographs, especially Historic Detroit pre_p16',limitations=notes),indent=2))
# The full hall carries dusty historic marble; restored terrazzo bench repairs do not exist yet.
n=3072;y,x=np.mgrid[0:n,0:n].astype(np.float32);wx=x/n*71.0184-35.5092;wy=y/n*31.6992
q=noise(n,42);fine=rng.normal(size=(n,n)).astype(np.float32)
c=np.zeros((n,n,3),np.float32)+[.49,.482,.458];c+=(q*.012+fine*.008)[:,:,None]
# Faint diagonal joints and stone-by-stone variation show through settled pale dust.
u=(wy-wx+80)/2.30;v=(wy+wx+80)/2.30
cid=(np.floor(u).astype(int)*73+np.floor(v).astype(int)*29)%131
stone=rng.uniform(-.010,.010,131)[cid];c+=stone[:,:,None]
joint=(np.minimum(u%1,1-u%1)<.004)|(np.minimum(v%1,1-v%1)<.004)
c[joint]*=.84
# Fine dispersed perimeter grit, photo-supported class, not exact recorded debris.
edge=np.exp(-np.minimum(wy,31.6992-wy)/2.0)
grit=(rng.random((n,n))<(.045+edge*.22))
c[grit]-=(.07+edge[grit]*.09)[:,None]
rough=np.clip(.87+q*.009+fine*.004,.80,.95);h=np.full((n,n),.5,np.float32);h[joint]-=.009
output('great_hall_floor_2017',c,rough,h,[71.0184,31.6992],'Photo-informed dusty marble color and generic historic joint rhythm; joint inventory and grime distribution are approximate. No 2024 terrazzo repairs.')
del c,rough,h,x,y,wx,wy,q,fine,u,v,joint,cid,stone,edge,grit
# Mixed pale/orange masonry and surviving mortar/plaster seen on stripped pier faces.
n=2048;y,x=np.mgrid[0:n,0:n].astype(np.float32)/n;row=np.floor(y*20).astype(int);col=np.floor(x*12+(row%2)*.5).astype(int)%12
bx=(x*12+(row%2)*.5)%1;by=(y*20)%1;joints=(bx<.015)|(by<.027)
palette=np.array([[.47,.445,.39],[.50,.48,.415],[.44,.42,.355],[.50,.455,.375],[.46,.435,.37],[.42,.405,.35],[.54,.52,.45],[.47,.395,.305]],np.float32)
ci=rng.choice(len(palette),size=(20,12),p=[.19,.16,.12,.12,.13,.09,.13,.06]);c=palette[ci[row,col]].copy()
q=noise(n,100);fine=rng.normal(size=(n,n)).astype(np.float32);c+=(q*.019+fine*.006)[:,:,None]
c[joints]=[.42,.405,.36]
# Thin uneven residual plaster is integral to this material class; no clean rectangular red-brick field.
field=noise(n,5)+.25*noise(n,45);residue=np.clip((field+.55)*.60,0,.96)
pl=np.zeros_like(c)+[.54,.525,.47];pl+=(q*.011)[:,:,None];c=c*(1-residue[:,:,None])+pl*residue[:,:,None]
h=.5+q*.007-joints*.024+residue*.006
output('mixed_hall_backing_2017',c,np.full((n,n),.91,np.float32),h,6.0,'Approximate mixed masonry/plaster-residue appearance; individual materials, block dimensions and exact surviving patches are not a surveyed damage map. Avoid treating this as evidence.')
print('2017 hall surface maps saved')
