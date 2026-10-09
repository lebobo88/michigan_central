"""Original imagegen wall-field artwork, technical periodicization and inferred PBR.
No copyrighted image pixels are read. Never changes any accepted/live asset.
"""
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import gaussian_filter,map_coordinates
import hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
MAN=ROOT/'manifests/material_refinement_v2';QA=HERE/'qa';QA.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
frozen={str(p.relative_to(ROOT)):sha(p) for d in ['limestone_2017_pale','limestone_2017_ashlar_optional','rose_marble_polished','great_hall_floor_2026','great_hall_floor_2017'] for p in (HERE.parent/d).rglob('*.png')}
source=HERE/'generated_original.png'
a=np.asarray(Image.open(source).convert('RGB'),np.float32)/255
N=2048
# The actual generated image has eight courses, but crops the last course before
# its ending joint. Resample measured image-grid controls to exactly 8 courses;
# fill its small cropped remainder by reflection, then rebuild edge continuity.
# These are image controls of original artwork, not surveyed station dimensions.
ys=np.array([19,181,342,502,662,822,984,1146,1307],np.float32)
padded=np.pad(a,((0,72),(0,0),(0,0)),mode='reflect')
y,x=np.mgrid[0:N,0:N].astype(np.float32)
source_y=np.interp((y[:,0]+.5)*8/N,np.arange(9),ys).astype(np.float32)
sy=np.broadcast_to(source_y[:,None],(N,N));sx=x*(a.shape[1]-1)/(N-1)
c=np.stack([map_coordinates(padded[:,:,ch],[sy,sx],order=1,mode='nearest') for ch in range(3)],2)
# Color rendering is not a scan: modest neutralization and contrast compression
# distinguish gray soiling from the previous yellow-brown camouflage material.
c=.72*gaussian_filter(c,sigma=(.8,.8,0),mode='wrap')+.28*c
lum=c@np.array([.2126,.7152,.0722],np.float32)
c=(lum*.88-.025)[:,:,None]+(c-lum[:,:,None])*.28+np.array([.007,.003,-.002],np.float32)
c=np.maximum(c,.375)
# Finish the cut-off final joint using the generated top joint as an original
# texture-edge source. Only the edge strip is repaired, not the image's interior.
for k in range(12):
 t=(1-k/12)**2
 c[-1-k]=c[-1-k]*(1-t)+c[0]*t
# Opposing edge-strip average; first derivatives remain mild and tiled boundary
# colors are identical. This is technical texture preparation, not scene lighting.
def periodicize(im,width=18):
 im=im.copy()
 for k in range(width):
  weight=(1-k/width)**2
  mean=(im[:,k]+im[:,-1-k])*.5
  im[:,k]=im[:,k]*(1-weight)+mean*weight
  im[:,-1-k]=im[:,-1-k]*(1-weight)+mean*weight
 for k in range(width):
  weight=(1-k/width)**2
  mean=(im[k]+im[-1-k])*.5
  im[k]=im[k]*(1-weight)+mean*weight
  im[-1-k]=im[-1-k]*(1-weight)+mean*weight
 return im
c=periodicize(c)
gray=c.mean(2)
# Joint and stain roughness are artistically inferred from dark generated color.
# Height ignores broad discoloration entirely. Only tiny filtered micrograin is
# carried into normal, so a black wash is never mistaken for deep stone loss.
wash=np.clip((.705-gaussian_filter(gray,8,mode='wrap'))/.24,0,1)
rough=periodicize(np.clip(.64+wash*.15,.64,.82))
fine=gray-gaussian_filter(gray,2.0,mode='wrap')
height=np.clip(fine*.00018,-.000012,.000012)
height=periodicize(height)
gy=(np.roll(height,-1,axis=0)-np.roll(height,1,axis=0))*.5
gx=(np.roll(height,-1,axis=1)-np.roll(height,1,axis=1))*.5
norm=np.stack([-gx/(4/N),gy/(4/N),np.ones_like(height)],2)
norm/=np.linalg.norm(norm,axis=2)[:,:,None]
def png(name,v):Image.fromarray(np.rint(np.clip(v,0,1)*255).astype(np.uint8)).save(HERE/(name+'.png'))
png('basecolor',c);png('roughness',rough);png('normal',norm*.5+.5)
Image.fromarray(np.rint((.5+height/.0002)*65535).astype(np.uint16)).save(HERE/'height.png')
orm=np.zeros((N,N,3),np.uint8);orm[:,:,0]=255;orm[:,:,1]=np.rint(rough*255).astype(np.uint8)
Image.fromarray(orm).save(HERE/'orm.png')
source_info={
 'reference':'May 2017 main entrance photograph, hd_pre_12.jpg',
 'url':'https://storage.googleapis.com/historic-detroit-prod/uploads/photo/photo/11085/MICEN2017_5637.jpg',
 'credit':'Bob Laperriere / HistoricDetroit.org',
 'local':'research/reference_only_copyrighted/hd_pre_12.jpg',
 'use':'Viewed for gray joint-associated washing, pale retained stone and sparse runoff/rust character only. No reference-photo pixels supplied to imagegen or this generator.',
 'current_render':'renders/revision10/2017_front.png',
 'render_finding':'The previous camouflage problem is removed, but flat wall fields behind and between the exterior columns read uniformly pale. The accepted unjointed material remains appropriate as a conservative profile/ornament base; aging needs separate planar-field placement.'}
limits=[
 'Original imagegen material-class artwork plus technical periodicization, not a Michigan Central scan or exact May 2017 damage map.',
 'Generated blocks, joints, weathering, rust marks and color variation are not documentary evidence.',
 'Approximate 4 m repeat, 8 courses and 1 x 0.5 m nominal blocks are image-authoring dimensions, not surveyed masonry.',
 'Imagegen texture had a cropped final course; edge reconstruction and opposite-border matching were applied and are disclosed. Inspect tiled use.',
 'Numeric albedo, roughness and micrometre height are inferred. Tiny contrast inherited from generated artwork may not be a perfect illumination-free scan.',
 'No large sculptural wear, chipped stone, dislodged masonry, cracks, graffiti or geometry were added.',
 'All accepted materials and completed 2017 floor derivative are unchanged.',
 'No Blender or station-scene render was performed for this new variant; revision10 was inspected as the placement/contrast diagnosis.',
 'Do not tile rust marks blindly across the whole facade. Start with bounded north planar wall fields and judge whether repeating accents are visible in the actual view.',
]
placement={
 'era':2017,'create_separate_material':'2017 aged limestone wall fields',
 'physical_repeat_m':4.0,'image_v_orientation':'Image rows increase downward; orient positive UV v upward with world +Z. Do not rotate wall texture 90 degrees.',
 'recommended_initial_scope':['north facade continuous stone piers','north facade end pier','north side-wing end infill'],
 'optional_after_review':['side perimeter continuous stone piers','east southern historical aperture piers'],
 'further_scoped_candidate':'Planar infill surfaces produced by wall_with_arch may use this class if specifically assigned; do not globally replace the generically batched Exterior Indiana limestone mesh/material.',
 'do_not_assign':['column shafts, column bases and capitals','arch jambs and archivolts','monumental window stone arch','north entablature bands and dentils','pediments, cornices, moldings and carved ornament','terrace balusters/copings','tower terra-cotta materials','all 2026 surfaces','all floor materials'],
 'mapping':'Use existing world-metric UVs at 4 m. Match joints at neighboring flat faces; do not force this grid across curved profiles.',
 'verification':'Compare the actual front facade at revision10 exposure. Aging should read as broken course-related gray wash on fields with pale stone retained, without returning to all-over round spots. Check repeat visibility before expanding scope.'}
rec={'material':'stone_field_aging_2017','pixels':[N,N],'physical_repeat_m':4.0,'nominal_course_module_m':[1,.5],
 'origin':'Actual built-in image_gen output from a text-only prompt, technically prepared as a periodic stone-field material',
 'input_generated_original':source.name,'input_generated_sha256':sha(source),
 'basecolor_processing':'Eight-course normalization, small reflected final-course extension, restrained neutralization, fine-grain contrast compression and opposing-edge matching',
 'basecolor_encoding':'sRGB','roughness_encoding':'linear; same channel also packed in ORM G',
 'roughness_origin':'Artistic inference from generated dark washing, not measured',
 'normal_encoding':'OpenGL tangent space +Y, UV-v up; linear','normal_origin':'Derived only from inferred <=24 micrometre peak-to-peak micrograin; not from broad stains or cracks',
 'height_encoding':{'bits':16,'full_range_m':.0002,'decode_m':'(uint16/65535-0.5)*0.0002','peak_to_peak_m':float(height.max()-height.min()),'inferred':True,'displacement_enabled':False},
 'gltf':{'baseColorTexture':'basecolor.png','metallicRoughnessTexture':'orm.png','normalTexture':'normal.png','metallicFactor':0,'roughnessFactor':1,'normalTexture_scale':1,'height':'Sidecar only; no displacement in core glTF'},
 'source_context':source_info,'placement':placement,'limitations':limits}
rec['sha256']={p.name:sha(p) for p in HERE.glob('*.png')}
(HERE/'provenance.json').write_text(json.dumps(rec,indent=2));(MAN/'stone_field_aging_2017.json').write_text(json.dumps(rec,indent=2))
# Verify boundaries of exported maps, not the pre-quantized arrays.
check={}
for ch in ['basecolor','roughness','height','normal']:
 im=np.asarray(Image.open(HERE/(ch+'.png')),np.float32);im=im[:,:,None] if im.ndim==2 else im
 d=65535 if ch=='height' else 255;im=im/d
 check[ch]={'edge_x_mean':float(abs(im[:,0]-im[:,-1]).mean()),'edge_y_mean':float(abs(im[0]-im[-1]).mean()),'mean':im.mean(axis=(0,1),dtype=np.float64).tolist(),'p01':np.percentile(im,1,axis=(0,1)).tolist(),'p99':np.percentile(im,99,axis=(0,1)).tolist()}
all_frozen=all(sha(ROOT/p)==digest for p,digest in frozen.items())
report={'status':'PASS','accepted_and_live_maps_unchanged':all_frozen,
 'periodic_basecolor_boundaries_exact':check['basecolor']['edge_x_mean']==0 and check['basecolor']['edge_y_mean']==0,
 'periodic_roughness_boundaries_exact':check['roughness']['edge_x_mean']==0 and check['roughness']['edge_y_mean']==0,
 'height_16_bit':(HERE/'height.png').read_bytes()[24]==16,
 'height_peak_to_peak_m':float(height.max()-height.min()),'measurements':check,
 'scope':'Map encoding, matched periodic boundaries and frozen asset hashes. Blender rendering, final-scene placement and glTF round-trip are not yet run.'}
assert all_frozen and report['periodic_basecolor_boundaries_exact'] and report['periodic_roughness_boundaries_exact'] and report['height_16_bit']
(MAN/'stone_field_aging_2017_validation.json').write_text(json.dumps(report,indent=2))
try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',21)
except OSError:font=ImageFont.load_default()
canvas=Image.new('RGB',(1800,1060),(24,27,30));d=ImageDraw.Draw(canvas)
for i,path,label in [(0,HERE.parent/'limestone_2017_pale/basecolor.png','Accepted profile stone / 4 m'),(1,HERE.parent/'limestone_2017_ashlar_optional/basecolor.png','Previous optional jointed field / 4 m'),(2,HERE/'basecolor.png','NEW aged planar field / 4 m')]:
 im=Image.open(path).convert('RGB').resize((580,580),Image.Resampling.LANCZOS)
 canvas.paste(im,(i*600+10,48));d.text((i*600+10,14),label,fill='white',font=font)
view=Image.open(ROOT/'renders/revision10/2017_front.png').convert('RGB')
view=view.crop((166,520,1028,694)).resize((1740,350),Image.Resampling.LANCZOS)
canvas.paste(view,(30,675));d.text((30,640),'Current revision10 facade crop: existing material, before field-aging integration',fill='white',font=font)
canvas.save(QA/'stone_field_before_after_and_revision10.png')
im=Image.open(HERE/'basecolor.png').resize((600,600),Image.Resampling.LANCZOS);tile=Image.new('RGB',(1200,1200))
for y0 in [0,600]:
 for x0 in [0,600]:tile.paste(im,(x0,y0))
tile.save(QA/'stone_field_2x2.png')
(HERE/'placement.json').write_text(json.dumps(placement,indent=2))
print(json.dumps(report,indent=2))
