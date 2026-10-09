"""Original glazed ceramic herringbone field, visibly supported by hall photographs.
Tile module is artistic rather than measured; this is not source-image texture extraction.
"""
from pathlib import Path
import numpy as np,json
from PIL import Image
from scipy.ndimage import gaussian_filter
r=Path(__file__).resolve().parents[1];o=r/'assets/textures/guastavino_restored';n=2048;rng=np.random.default_rng(60106)
y,x=np.mgrid[0:n,0:n].astype(np.float32);u=x/n*32;v=y/n*32;ix=np.floor(u).astype(int);iy=np.floor(v).astype(int);par=(ix+iy)%4
# Periodic domino herringbone: horizontal0/1 pairs alternate with vertical2/3 pairs.
vertical=par>=2;anchorx=ix-(par==1);anchory=iy-(par==3)
a=np.where(vertical,u%1,(u%1)+(par==1));b=np.where(vertical,(v%1)+(par==3),v%1)
width=np.where(vertical,1,2);height=np.where(vertical,2,1)
grout=(a<.025)|(a>width-.025)|(b<.025)|(b>height-.025)
ids=(anchorx*271+anchory*119+vertical.astype(int)*41)%1031;variation=rng.uniform(-.052,.045,1031)[ids]
fine=gaussian_filter(rng.normal(size=(n,n)).astype('float32'),.65,mode='wrap');fine/=fine.std()
c=np.zeros((n,n,3),np.float32)+[.66,.625,.525];c+=(variation+fine*.0035)[:,:,None];c[grout]=[.495,.475,.415]
# Very fine parallel grooves follow each individual tile's long axis.
groove=np.where(vertical,np.sin(u*2*np.pi*10),np.sin(v*2*np.pi*10));h=.5-grout*.018+groove*.001
rough=np.clip(.65+variation*.18+fine*.003,.60,.71)
Image.fromarray((np.clip(c,0,1)*255).astype('uint8')).save(o/'basecolor.png');Image.fromarray((rough*255).astype('uint8')).save(o/'roughness.png');Image.fromarray((np.clip(h,0,1)*65535).astype('uint16')).save(o/'height.png')
dy,dx=np.gradient(h);norm=np.stack([-dx*8,dy*8,np.ones_like(h)],2);norm/=np.sqrt((norm*norm).sum(2))[:,:,None];Image.fromarray(((norm*.5+.5)*255).astype('uint8')).save(o/'normal.png')
(o/'provenance.json').write_text(json.dumps(dict(origin='Original authored herringbone glazed ceramic field; no reference photograph pixels',pixels=[n,n],physical_repeat_m=4.0,nominal_tile_m=[.25,.125],module_status='Photograph-informed scale approximation, not measured station tile dimensions',evidence='Herringbone pattern visible in dated2017 and restored2023/24 GrandHall photography',normal_convention='OpenGL +Y'),indent=2))
print('Herringbone ceramic maps saved')
