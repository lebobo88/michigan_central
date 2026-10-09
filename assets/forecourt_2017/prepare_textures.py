"""Original procedural period-informed surfaces. No reference pixels sampled or copied."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np, math, json
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'assets/forecourt_2017/textures';OUT.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(170819);N=512;manifest=[]
for name,color,rough,repeat in [('weathered_apron',(126,124,115),.90,4.0),('exposed_soil',(107,88,63),.96,2.0),('pale_sidewalk',(170,166,152),.88,3.0),('median_concrete',(158,155,140),.92,3.0)]:
 p=OUT/name;p.mkdir(exist_ok=True)
 fine=rng.normal(0,1,(N,N));low=np.asarray(Image.fromarray(rng.integers(0,256,(12,12),dtype=np.uint8)).resize((N,N),Image.Resampling.BICUBIC),dtype=float)/255-.5
 med=np.asarray(Image.fromarray(rng.integers(0,256,(80,80),dtype=np.uint8)).resize((N,N),Image.Resampling.BICUBIC),dtype=float)/255-.5
 h=.5+med*.20+fine*.025;c=np.asarray(color)[None,None,:]+(fine*2.8+med*20+low*11)[:,:,None]
 if name=='weathered_apron':
  grit=rng.random((N,N))>.992;c[grit]-=rng.uniform(5,25,(grit.sum(),1))
 if name=='exposed_soil':
  grit=rng.random((N,N))>.97;c[grit]-=rng.uniform(8,22,(grit.sum(),1));h[grit]-=.08
 Image.fromarray(np.uint8(np.clip(c,0,255))).save(p/'basecolor.png')
 Image.fromarray(np.uint8(np.clip(rough+med*.04+fine*.015,0,1)*255)).save(p/'roughness.png')
 dy,dx=np.gradient(h);normal=np.dstack((-dx*.6,-dy*.6,np.ones_like(dx)));normal/=np.linalg.norm(normal,axis=2)[:,:,None]
 Image.fromarray(np.uint8(np.clip(normal*.5+.5,0,1)*255)).save(p/'normal.png')
 Image.fromarray(np.uint16(np.clip(h,0,1)*65535)).save(p/'height.png')
 manifest.append({'name':name,'size_px':[N,N],'repeat_m':repeat,'provenance':'Original seeded procedural pixels, no source photograph pixels','seed':170819,'normal_convention':'OpenGL tangent-space +Y; height supplied but displacement off'})
# Independently drawn symbolic US flag. Geometry will drape the material.
W,H=760,400;im=Image.new('RGB',(W,H),'#e8e5d8');d=ImageDraw.Draw(im)
for j in range(13):
 if j%2==0:d.rectangle((0,round(H*j/13),W,round(H*(j+1)/13)),fill='#9c3440')
cw,ch=round(W*.4),round(H*7/13);d.rectangle((0,0,cw,ch),fill='#253450')
for row in range(9):
 count=6 if row%2==0 else 5
 for col in range(count):
  x=cw*(col+(.5 if count==6 else 1))/6;y=ch*(row+1)/10;r=ch*.039
  pts=[(x+math.cos(-math.pi/2+k*math.pi/5)*r*(1 if k%2==0 else .382),y+math.sin(-math.pi/2+k*math.pi/5)*r*(1 if k%2==0 else .382)) for k in range(10)]
  d.polygon(pts,fill='#e8e5d8')
p=OUT/'authored_us_flag';p.mkdir(exist_ok=True);im.save(p/'basecolor.png')
manifest.append({'name':'authored_us_flag','size_px':[W,H],'provenance':'Original geometric drawing of 13 stripes and 50 stars; no downloaded artwork','not_claimed':'Exact wind state, folds, flag condition or size in 2017'})
(ROOT/'manifests/forecourt_2017/texture_provenance.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Created four original PBR surface sets and one original symbolic flag map')
