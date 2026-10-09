"""Bounded 2017 hall-floor derivative. Does not change completed v2 maps or geometry.
No third-party pixels are read. Run with the project's NumPy/Pillow/SciPy Python.
"""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import map_coordinates,gaussian_filter
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
MAN=ROOT/'manifests/material_refinement_v2'
QA=HERE/'qa';QA.mkdir(exist_ok=True)
OLD=ROOT/'assets/textures/great_hall_floor_2017'
N=3072;SX,SY=71.0184,31.6992
rng=np.random.default_rng(20170516006)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
frozen={str(p.relative_to(ROOT)):sha(p) for d in ['limestone_2017_pale','rose_marble_polished','great_hall_floor_2026'] for p in (HERE.parent/d).glob('*') if p.is_file()}
def noise(ny,nx):
 grid=rng.normal(size=(ny,nx)).astype(np.float32)
 y,x=np.mgrid[0:N,0:N].astype(np.float32)
 a=map_coordinates(grid,[y*ny/N,x*nx/N],order=3,mode='grid-wrap')
 return (a-a.mean())/(a.std()+1e-6)
def save_img(name,a):Image.fromarray(np.rint(np.clip(a,0,1)*255).astype(np.uint8)).save(HERE/(name+'.png'))
y,x=np.mgrid[0:N,0:N].astype(np.float32)
wx=x/N*SX-SX/2;wy=y/N*SY
original=np.asarray(Image.open(OLD/'basecolor.png').convert('RGB'),np.float32)/255
oldr=np.asarray(Image.open(OLD/'roughness.png'),np.float32)/255
oldh=np.asarray(Image.open(OLD/'height.png'),np.uint16)
u=(wy-wx+80)/2.30;v=(wy+wx+80)/2.30
joint=(np.minimum(u%1,1-u%1)<.004)|(np.minimum(v%1,1-v%1)<.004)
# Read only original project-created material. No restoration inlay colors or layout copied.
stone=np.asarray(Image.open(HERE.parent/'rose_marble_polished/basecolor.png'),np.float32)/255
h,w=stone.shape[:2]
filtered=gaussian_filter(stone,sigma=((SY/N)/(1.2/h)*.45,(SX/N)/(1.2/w)*.45,0),mode='wrap')
xx=(wx/1.2%1)*w;yy=(wy/1.2%1)*h
marble=np.stack([map_coordinates(filtered[:,:,k],[yy,xx],order=1,mode='grid-wrap') for k in range(3)],2)
# Remove the already authored tiny joint darkening during material blending, then
# restore the exact same mask and multiplier. A small per-pixel quantization is expected.
field=original.copy();field[joint]/=.84
# Cleared center and uneven peripheral deposits are material-class observations only.
edge_dist=np.minimum(np.minimum(wy,SY-wy),np.minimum(wx+SX/2,SX/2-wx))
edge=np.exp(-edge_dist/1.55).astype(np.float32)
spread=noise(19,27)*.60+noise(63,83)*.25
# Grit density is driven by coverage, not shadow baking or invented rubble geometry.
deposit=np.clip((spread+.30)*.20,0,.48)*edge**.68
# Low-contrast elongated sweep/dust variation, never a surveyed route or exact wear map.
sweep=noise(45,18)
visible=np.clip(.080+.035*sweep+.018*noise(16,29),.015,.19)
# A few original short, soft scuff marks, deliberately not aligned into fake fracture lines.
scuff_img=Image.new('L',(N,N),0);dr=ImageDraw.Draw(scuff_img)
for i in range(560):
 cx=float(rng.uniform(-SX/2+1,SX/2-1));cy=float(rng.uniform(.6,SY-.6))
 angle=float(rng.uniform(-np.pi,np.pi));length=float(rng.uniform(.14,.75))
 ex=cx+np.cos(angle)*length;ey=cy+np.sin(angle)*length
 points=[((cx+SX/2)/SX*N,cy/SY*N),((ex+SX/2)/SX*N,ey/SY*N)]
 dr.line(points,fill=int(rng.integers(90,210)),width=1)
scuff=gaussian_filter(np.asarray(scuff_img,np.float32)/255,.7,mode='nearest')
visible=np.clip(visible+scuff*.11,0,.22)
color=field*(1-visible[:,:,None])+marble*visible[:,:,None]
# Deposits are warm gray mineral dust; darkness is restrained and has no lighting baked in.
deposit_color=np.array([.35,.335,.303],np.float32)
color=color*(1-deposit[:,:,None])+deposit_color*deposit[:,:,None]
# Sparse fine aggregate coverage, averaged at this full-room atlas resolution.
grit_probability=.0015+edge*.010
seeds=(rng.random((N,N))<grit_probability).astype(np.float32)
grit=gaussian_filter(seeds,.60,mode='nearest')
color-=grit[:,:,None]*np.array([.060,.057,.051],np.float32)
# Faint lifted dust on small scuffs produces fine surface differences, not cracks.
color+=scuff[:,:,None]*.010
color[joint]*=.84
rough=np.clip(oldr-visible*.60+deposit*.065+grit*.045-scuff*.015,.70,.94)
# Preserve all existing inferred joint relief pixels exactly; infer physical decoding
# conservatively instead of using deep normal/displacement to fabricate age.
Image.fromarray(oldh).save(HERE/'height.png')
height_range=.008
hm=(oldh.astype(np.float32)/65535-.5)*height_range
# Atlas isn't tiled: one-sided finite differences at room boundaries.
gy,gx=np.gradient(hm)
nn=np.stack([-gx/(SX/N),gy/(SY/N),np.ones_like(hm)],2)
nn/=np.linalg.norm(nn,axis=2)[:,:,None]
save_img('basecolor',color);save_img('roughness',rough);save_img('normal',nn*.5+.5)
orm=np.zeros((N,N,3),np.uint8);orm[:,:,0]=255;orm[:,:,1]=np.rint(rough*255).astype(np.uint8)
Image.fromarray(orm).save(HERE/'orm.png')
limits=[
 'Original material-class study, not a surveyed or photo-projected May 2017 damage map.',
 'The existing unlit atlas already contained historic joints and perimeter grit; the dark scene render does not prove those were missing.',
 'Scuff/deposit positions and marble visibility are procedural estimates, not documented exact locations.',
 'Source photos establish a largely cleared dusty center and localized peripheral deposits. They do not justify indiscriminate deep cracks, rubble coverage, wetness, or restored bench-infill patches.',
 'Existing floor geometry, joint mask, joint rhythm, and 16-bit inferred height pixels are unchanged. No restored terrazzo bench footprints are introduced.',
 'No copyrighted study-photo pixels are sampled, embedded, reprojected or redistributed.',
 'Albedo, roughness, and microrelief scale are inferred; no measured scan or BRDF is claimed.',
 'This full-room atlas is not seamless or repeatable. Keep room mapping and clamp-to-edge.',
 'No Blender render has been performed for this follow-up; inspect under corrected station exposure before accepting or increasing texture contrast.',
]
sources=[
 {'id':'pre_p16','date':'May 2017','local':'research/interior/study_only/pre_p16.jpg','url':'https://historicdetroit.org/galleries/michigan-central-station-pre-restoration-interior#p16','credit':'Bob Laperriere / HistoricDetroit.org','observed':'Largely clear, pale dusty central floor; faint historic stone joints; uneven edge deposits and some local fallen material. Exact fall locations are outside this material study.'},
 {'id':'pre_p6','date':'May 2017','local':'research/interior/study_only/pre_p6.jpg','url':'https://historicdetroit.org/galleries/michigan-central-station-pre-restoration-interior#p6','credit':'Bob Laperriere / HistoricDetroit.org','observed':'Dull rose-gray historic floor near the Ticket Lobby, visible joints and dusty surface; no restored bench infill.'},
]
rec={'material':'great_hall_floor_2017','origin':'Original procedural refinement of original project atlas; no new imagegen call or third-party image pixels',
 'pixels':[N,N],'physical_repeat_m':None,'mapped_extent_m':[SX,SY],'periodic':False,
 'integration_target':'2017 Grand Hall floor assembly only','uv_rule':'Keep existing UV=(world.x/71.0184+0.5, world.y/31.6992)','texture_extension':'EXTEND / clamp to edge',
 'basecolor_encoding':'sRGB','roughness_encoding':'linear','normal_encoding':'OpenGL +Y; image-row derivative converted to UV-v-up',
 'height_encoding':{'bits':16,'original_pixels_preserved':True,'full_range_m':height_range,'decode_m':'(uint16/65535-0.5)*0.008','origin':'Conservative inferred physical scale, not measured','displacement_enabled':False},
 'normal_origin':'Derived from the unchanged original inferred joint-height pixels at conservative physical scale. No micro-rubble displacement.',
 'gltf':{'baseColorTexture':'basecolor.png','metallicRoughnessTexture':'orm.png','metallicFactor':0,'roughnessFactor':1,'normalTexture':'normal.png','normalTexture_scale':1,'height':'Sidecar only; no core glTF displacement'},
 'source_original_atlas':str(OLD.relative_to(ROOT)),'input_sha256':{f.name:sha(f) for f in OLD.glob('*.png')},
 'sources':sources,'limitations':limits}
rec['output_sha256']={p.name:sha(p) for p in HERE.glob('*.png')}
(HERE/'provenance.json').write_text(json.dumps(rec,indent=2))
# Separate notes prevent mutation of the completed v2 material registry.
(MAN/'great_hall_floor_2017.json').write_text(json.dumps(rec,indent=2))
newc=np.asarray(Image.open(HERE/'basecolor.png'),np.float64)/255
newr=np.asarray(Image.open(HERE/'roughness.png'),np.float64)/255
newn=np.asarray(Image.open(HERE/'normal.png'),np.float32)/255*2-1
height_unchanged=bool(np.array_equal(np.asarray(Image.open(HERE/'height.png')),oldh))
# The existing original height map independently encodes exactly the joint mask.
old_joint=oldh<32760
joint_unchanged=bool(np.array_equal(old_joint,joint))
frozen_unchanged=all(sha(ROOT/p)==digest for p,digest in frozen.items())
report={'status':'PASS','map_encoding':{'height_16_bit':(HERE/'height.png').read_bytes()[24]==16,'normal_max_channel_error':float(abs(newn-nn).max()),'orm_roughness_exact':bool(np.array_equal(orm[:,:,1],np.asarray(Image.open(HERE/'roughness.png'))))},
 'joint_mask_unchanged':joint_unchanged,'height_pixels_unchanged':height_unchanged,'frozen_v2_targets_unchanged':frozen_unchanged,
 'joint_pixels':int(joint.sum()),'height_peak_to_peak_m':float(hm.max()-hm.min()),
 'albedo_mean_srgb':newc.mean(axis=(0,1)).tolist(),'albedo_p01_srgb':np.percentile(newc,1,axis=(0,1)).tolist(),'albedo_p99_srgb':np.percentile(newc,99,axis=(0,1)).tolist(),
 'roughness_mean':float(newr.mean()),'roughness_p01_p99':np.percentile(newr,[1,99]).tolist(),
 'marble_visibility_fraction_p01_p99':np.percentile(visible,[1,99]).tolist(),
 'stone_visibility_role':'Dust-film blend fraction, not restoration or patch coverage probability',
 'full_scene_render':'NOT RUN; waiting for coordinated exposure-corrected comparison','limitations':limits}
assert height_unchanged and joint_unchanged and frozen_unchanged
assert report['map_encoding']['height_16_bit'] and report['map_encoding']['normal_max_channel_error']<.0041 and report['map_encoding']['orm_roughness_exact']
(MAN/'great_hall_floor_2017_validation.json').write_text(json.dumps(report,indent=2))
# Original project maps only. These deliverable comparisons contain no reference pixels.
try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',21)
except OSError:font=ImageFont.load_default()
canvas=Image.new('RGB',(1700,1000),(26,28,31));d=ImageDraw.Draw(canvas)
for col,path,label in [(0,OLD/'basecolor.png','Existing unlit atlas'),(1,HERE/'basecolor.png','2017 v2: dust, scuffs, stone visibility')]:
 im=Image.open(path).convert('RGB');thumb=im.resize((820,366),Image.Resampling.LANCZOS)
 canvas.paste(thumb,(col*850+15,55));d.text((col*850+15,18),label,fill='white',font=font)
 # 12 m square near the side-perimeter, with a neighboring clearer interior.
 x0=int((-6+SX/2)/SX*N);x1=int((6+SX/2)/SX*N);y0=0;y1=int(12/SY*N)
 crop=im.crop((x0,y0,x1,y1)).resize((505,505),Image.Resampling.LANCZOS)
 canvas.paste(crop,(col*850+15,450))
 d.text((col*850+535,480),'12 x 12 m detail',fill=(225,225,225),font=font)
 d.text((col*850+535,516),'No added geometry',fill=(225,225,225),font=font)
 d.text((col*850+535,552),'Unlit sRGB',fill=(225,225,225),font=font)
 d.text((col*850+535,588),'WIP / inferred PBR',fill=(225,225,225),font=font)
canvas.save(QA/'floor_2017_before_after_unlit.png')
Image.open(HERE/'basecolor.png').resize((1792,800),Image.Resampling.LANCZOS).save(QA/'floor_2017_physical_aspect.png')
(HERE/'README.txt').write_text('''2017 GRAND HALL FLOOR / BOUNDED FOLLOW-UP

New, isolated full-room atlas only. No completed v2 maps or live assets changed.
Use this directory for 2017 Grand Hall floor assembly, retaining room UVs:
u=world.x/71.0184+0.5; v=world.y/31.6992. Clamp to edge. Do not tile.

The original unlit atlas already included faint joints and perimeter grit.
This derivative adds restrained dust-film variation, sparse short scuffs,
partial dull rose-gray marble visibility and uneven fine edge deposits.
The exact existing joint mask and all original 16-bit height pixels are preserved.
Normal relief is conservatively decoded to 0.072 mm peak-to-peak, not rubble.
No new cracks, major damage, restored bench footprints or floor geometry added.

Maps: basecolor sRGB; roughness linear; normal OpenGL +Y; inferred height16;
orm contains occlusion=1, roughness in G and metallic=0. Height is a sidecar,
not core glTF displacement. Provenance and input/output hashes are recorded.

QA: qa/floor_2017_before_after_unlit.png and qa/floor_2017_physical_aspect.png.
No Blender render was performed for this follow-up. Correct the hall exposure,
then compare the material in the final scene before increasing contrast.
Evidence: May 2017 Historic Detroit pre_p16 and pre_p6, linked in provenance.
This is an original material-class interpretation, not a surveyed damage map.
No reference-photo pixels are included. All numerical PBR values are inferred.

Reproduce with the project NumPy/Pillow/SciPy interpreter and this prepare.py.
''')
print(json.dumps(report,indent=2))
