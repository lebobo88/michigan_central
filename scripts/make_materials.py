"""Original deterministic, seamless construction-material maps. No photographic inputs.
Run with ../3d-tools/venv/bin/python scripts/make_materials.py.
Maps are approximations, not scans of Michigan Central's fabric.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, zoom, map_coordinates

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/textures'; OUT.mkdir(parents=True,exist_ok=True)
N=2048; rng=np.random.default_rng(19132026)
y,x=np.mgrid[0:N,0:N].astype(np.float32)/N

def noise(scale):
    a=rng.normal(size=(scale,scale)).astype(np.float32)
    a=np.pad(a,((0,1),(0,1)),mode='wrap')
    yy,xx=np.mgrid[0:N,0:N].astype(np.float32)*scale/N
    a=map_coordinates(a,[yy,xx],order=3,mode='wrap')
    a=(a-a.mean())/(a.std()+1e-6)
    return a

n1=noise(8); n2=noise(35); n3=noise(145); fine=rng.normal(size=(N,N)).astype(np.float32)
base=n1*.018+n2*.012+n3*.006+fine*.002
records=[]
def output(name,c,h,r,physical=4.0):
    folder=OUT/name; folder.mkdir(exist_ok=True)
    c=np.clip(c,0,1);h=np.clip(h,0,1);r=np.clip(r,0,1)
    Image.fromarray((c*255).astype('uint8')).save(folder/'basecolor.png')
    Image.fromarray((r*255).astype('uint8')).save(folder/'roughness.png')
    Image.fromarray((h*65535).astype('uint16')).save(folder/'height.png')
    gy,gx=np.gradient(h)
    nor=np.stack([-gx*20,gy*20,np.ones_like(h)],2);nor/=np.sqrt((nor*nor).sum(2))[:,:,None]
    Image.fromarray(((nor*.5+.5)*255).astype('uint8')).save(folder/'normal.png')
    records.append(dict(material=name,pixels=[N,N],physical_repeat_m=physical,
        origin='original deterministic procedural texture',rights='Original project-generated material; no third-party photograph used',
        normal_convention='OpenGL +Y',height_bits=16,
        limitations='Art-directed approximation; not a measured or photographed scan'))

for era in ['restored','2017']:
    aged=era=='2017'
    # Large-scale moisture mottling includes elongated vertical stains.
    streak=gaussian_filter(rng.random((N,N)).astype(np.float32),sigma=(75,4),mode='wrap')
    streak=(streak-streak.min())/(streak.max()-streak.min())
    stain=np.clip(n1*.19+n2*.06+.07,0,1)*(.95 if aged else .08)
    for name,color in [('limestone',[.62,.57,.46]),('plaster',[.77,.735,.64]),('mankato',[.55,.46,.32])]:
        factor={'limestone':.45,'mankato':.30,'plaster':.65}[name]
        c=np.array(color)[None,None,:]+base[:,:,None]*.50-stain[:,:,None]*np.array([.8,.86,.82])*factor
        h=.5+base*.6;rough=np.clip(.64+base*3+stain*.2,.2,.96)
        output(name+'_'+era,c,h,rough,4)
    # Grooved buff ceramic Guastavino tile, a tiled stochastic material.
    rows=36;cols=18;row=np.floor(y*rows).astype(int)
    xx=(x*cols+(row%2)*.5)%1; yy=(y*rows)%1
    grout=(xx<.022)|(yy<.045)
    cellrng=rng.uniform(-.045,.045,(rows,cols+1))
    ci=np.floor(x*cols+(row%2)*.5).astype(int)%cols
    vary=cellrng[row,ci]
    grooves=(np.sin(x*N*.4)>.65)*.014
    c=np.array([.66,.61,.48])[None,None,:]+(vary+base)[:,:,None]-stain[:,:,None]*.60
    if aged:c-=np.clip(n1*.28+n2*.12+.2,0,.65)[:,:,None]*.88
    c[grout]=[.43,.41,.35]
    output('guastavino_'+era,c,.55+base*.3-grout*.07-grooves,.69+base*2+stain*.2,4)

# Rose Tennessee marble. Veins are deliberately soft and sparse.
warp=noise(18)*.16+noise(5)*.44+n3*.045
vein=np.exp(-np.abs(warp-.24)*80)+.45*np.exp(-np.abs(warp+.18)*120)
c=np.array([.36,.285,.255])[None,None,:]+(n1*.018+n2*.010)[:,:,None]+vein[:,:,None]*.12
output('rose_marble',c,.5+vein*.00006,np.clip(.23+n2*.020,.12,.4),4)
c=np.array([.49,.41,.37])[None,None,:]+(n1*.015+n2*.008)[:,:,None]+vein[:,:,None]*.05
output('pale_marble',c,.5+vein*.00006,.25+n2*.012,4)
c=np.array([.39,.39,.37])[None,None,:]+(fine*.07+base)[:,:,None]
output('terrazzo',c,.5+fine*.025,.27+base,4)

# Structural common brick, used only where photographs show exposed masonry.
row=np.floor(y*24).astype(int); bx=(x*8+(row%2)*.5)%1;by=(y*24)%1
joint=(bx<.035)|(by<.075)
brickcolors=rng.uniform(-.11,.10,(24,9)); ci=np.floor(x*8+(row%2)*.5).astype(int)%8
v=brickcolors[row,ci]+base
c=np.array([.36,.22,.135])[None,None,:]+v[:,:,None];c[joint]=[.36,.34,.28]
output('exposed_brick',c,.53+base-joint*.12,.81+base,1.7)
c=np.array([.56,.49,.34])[None,None,:]+(v*.42)[:,:,None];c[joint]=[.46,.43,.35]
output('buff_brick',c,.53+base-joint*.09,.73+base,1.7)

c=np.array([.38,.375,.35])[None,None,:]+(base*2)[:,:,None]
output('dust_concrete',c,.5+base*2,.88+base,4)
c=np.array([.20,.27,.105])[None,None,:]+(base*1.4+n3*.008)[:,:,None]
output('grass',c,.5+n3*.04,.95+base*.1,4)
(OUT/'material_manifest.json').write_text(json.dumps(records,indent=2))
print(f'Wrote {len(records)} original PBR texture sets to {OUT}')
