"""Generate candidate-only original 512 px channel sets from authored controls.

These are periodic 2D statistical approximations, not bakes of the 3D shader.
Base color is sRGB encoded from linear source colors. Normal is OpenGL tangent
+Y; source roughness/metallic remain exact scalars (no invented variation).
"""
from pathlib import Path
import hashlib,json,sys
import numpy as np
from PIL import Image,ImageDraw
from material_portability import ROOT,OUT,source_specs,sha256

SIZE=512
DEST=OUT/'candidate_assets'

def lin_to_srgb(x):
    return np.where(x<=.0031308,12.92*x,1.055*np.maximum(x,0)**(1/2.4)-.055)

def srgb_to_lin(x):
    return np.where(x<=.04045,x/12.92,((x+.055)/1.055)**2.4)

def periodic_fac(seed,cycles,fractal_roughness):
    # Band-limited four-octave periodic spectral noise. Every Fourier frequency
    # is an integer across the repeat, so bilinear wrap has no boundary jump.
    # The fourth band is omitted if it would exceed the 512px Nyquist limit.
    rng=np.random.default_rng(seed)
    fy=np.fft.fftfreq(SIZE)*SIZE;fx=np.fft.rfftfreq(SIZE)*SIZE
    radius=np.hypot(fy[:,None],fx[None,:])
    field=np.zeros((SIZE,SIZE));bands=[]
    for octave in range(4):
        frequency=cycles*2**octave
        if frequency>SIZE/2:continue
        raw=rng.normal(size=(SIZE,SIZE))
        window=np.exp(-.5*((radius-frequency*.65)/(frequency*.36))**2)
        window[0,0]=0
        noise=np.fft.irfft2(np.fft.rfft2(raw)*window,s=raw.shape)
        noise/=max(noise.std(),1e-12)
        field+=noise*fractal_roughness**octave;bands.append(frequency)
    # Symmetric compression avoids clipping bias and remains within ramp range.
    field/=field.std();fac=.5+.35*np.tanh(field*.46)
    fac-=fac.mean()-.5
    return fac,bands

def make():
    DEST.mkdir(parents=True,exist_ok=True)
    audit=json.loads((OUT/'source_export_audit.json').read_text())
    manifest={'status':'CANDIDATE ONLY; not installed in live scene',
        'resolution':[SIZE,SIZE], 'generator':str(Path(__file__).relative_to(ROOT)),
        'generator_sha256':sha256(__file__),
        'limitations':['Not an exact bake of Blender Generated 3D Noise','Source ramp palette and approximate low-amplitude stochastic variation preserved',
            'Secondary MetricUV is already divided by 4m; new maps preserve those coordinates and assume a 4m repeat',
            'West MetricUV already uses 1m repeat; original 2.2 x 8 scale becomes 17.6 base cycles per repeat',
            'No brush direction, wood fibres, rust pits, cracks or photographed wear are invented',
            'Bump-distance times strength is treated as an approximate physical height amplitude; Blender bump is not exactly reconstructed',
            'Base noise band above Nyquist is omitted rather than aliased','Roughness and metallic are unchanged source scalars'],
        'materials':{}}
    specs_by_era={e:source_specs(e) for e in ['2017','2026']}
    used_by_era={e:{s['name'] for s in r['affected']} for e,r in audit['eras'].items()}
    for name in audit['unique_affected_names']:
        eras=[e for e in ['2017','2026'] if name in used_by_era[e]]
        spec=specs_by_era[eras[0]][name]
        seed=int(hashlib.sha256(name.encode()).hexdigest()[:8],16)
        fac,bands=periodic_fac(seed,spec['candidate_base_cycles_per_repeat'],spec['source_noise_roughness'])
        color=np.array(spec['ramp_low_linear'])[None,None,:]+fac[:,:,None]*(np.array(spec['ramp_high_linear'])-spec['ramp_low_linear'])[None,None,:]
        pixels=np.rint(lin_to_srgb(color).clip(0,1)*255).astype('uint8')
        folder=DEST/spec['slug'];folder.mkdir(exist_ok=True)
        colorpath=folder/'basecolor.png';Image.fromarray(pixels).save(colorpath)
        normals={};sha={str(colorpath.relative_to(DEST)):sha256(colorpath)}
        linear=srgb_to_lin(pixels/255)
        normal_stats={}
        for era in eras:
            es=specs_by_era[era][name]
            height=(fac-.5)*es['source_bump_distance_m']*es['source_bump_strength']
            pitch=es['existing_uv_repeat_m']/SIZE
            dx=(np.roll(height,-1,axis=1)-np.roll(height,1,axis=1))/(2*pitch)
            drow=(np.roll(height,-1,axis=0)-np.roll(height,1,axis=0))/(2*pitch)
            n=np.stack([-dx,drow,np.ones_like(dx)],axis=-1);n/=np.linalg.norm(n,axis=-1)[:,:,None]
            im=np.rint((n*.5+.5)*255).clip(0,255).astype('uint8')
            npth=folder/f'normal_{era}.png';Image.fromarray(im).save(npth)
            rel=str(npth.relative_to(DEST));normals[era]=rel;sha[rel]=sha256(npth)
            normal_stats[era]={'height_peak_to_peak_m':float(np.ptp(height)),
                'height_rms_m':float(height.std()),'normal_max_tilt_degrees':float(np.degrees(np.arccos(n[:,:,2].min())))}
        rec={k:spec[k] for k in ['base_color_linear','expected_mean_linear','source_function_sha256','roughness','metallic','existing_uv_repeat_m','candidate_base_wavelength_m','source_module','source_line']}
        rec.update(basecolor=str(colorpath.relative_to(DEST)),normal_by_era=normals,sha256=sha,
            source_used_eras=eras,seed=seed,retained_noise_bands=bands,
            measured_linear_mean=linear.mean(axis=(0,1)).tolist(),measured_linear_std=linear.std(axis=(0,1)).tolist(),
            noise_fac_mean=float(fac.mean()),noise_fac_std=float(fac.std()),normal_statistics=normal_stats,
            normal_convention='OpenGL +Y; image row axis points down, UV V points up')
        manifest['materials'][name]=rec
    (DEST/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    # Informational palette, not a shaded render or a parity proof.
    cards=list(manifest['materials'].items());w=1000;cw=250;ch=185
    sheet=Image.new('RGB',(w,60+ch*((len(cards)+3)//4)),(35,37,40));draw=ImageDraw.Draw(sheet)
    draw.text((15,15),'CANDIDATE BASE-COLOR PALETTE | original procedural controls | not a render',fill='white')
    for i,(name,r) in enumerate(cards):
        x=(i%4)*cw;y=60+(i//4)*ch
        im=Image.open(DEST/r['basecolor']).resize((220,125));sheet.paste(im,(x+15,y))
        label=name.replace('Secondary ','S: ').replace('West ','W: ')
        words=label.split();lines=['']
        for word in words:
            if len(lines[-1])+len(word)>33:lines.append(word)
            else:lines[-1]+=(' ' if lines[-1] else '')+word
        draw.text((x+15,y+130),'\n'.join(lines),fill='white')
    sheet.save(OUT/'candidate_palette.png')
    print(json.dumps({'materials':len(cards),'png_count':len(list(DEST.rglob('*.png'))),'bytes':sum(p.stat().st_size for p in DEST.rglob('*.png'))},indent=2))

if __name__=='__main__':make()
