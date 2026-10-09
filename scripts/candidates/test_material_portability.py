"""Pure Python regression tests with tiny GLB material-channel fixtures (not schema-validation fixtures)."""
import copy,io,json,struct,tempfile,unittest
from pathlib import Path
import numpy as np
from PIL import Image
from material_portability import ROOT,OUT,source_specs
from check_material_portability import check

class PortabilityRegression(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=OUT);self.path=Path(self.tmp.name)/'fixture.glb'
        self.era='2026';self.name='Secondary brushed bronze';self.spec=source_specs(self.era)[self.name]
        rec=json.loads((OUT/'candidate_assets/manifest.json').read_text())['materials'][self.name]
        self.images=[(OUT/'candidate_assets'/rec['basecolor']).read_bytes(),(OUT/'candidate_assets'/rec['normal_by_era'][self.era]).read_bytes()]
        self.material={'name':self.name,'pbrMetallicRoughness':{'baseColorTexture':{'index':0},
            'roughnessFactor':self.spec['roughness'],'metallicFactor':self.spec['metallic']},'normalTexture':{'index':1}}
    def tearDown(self):self.tmp.cleanup()
    def run_check(self,material=None):
        payload=b'';views=[]
        for raw in self.images:
            views.append({'buffer':0,'byteOffset':len(payload),'byteLength':len(raw)})
            payload+=raw+b'\0'*((-len(raw))%4)
        d={'asset':{'version':'2.0'},'materials':[material or self.material],
           'meshes':[{'primitives':[{'material':0,'attributes':{'POSITION':0,'TEXCOORD_0':1}}]}],
           'textures':[{'source':0},{'source':1}], 'images':[{'bufferView':i,'mimeType':'image/png'} for i in range(2)],
           'bufferViews':views,'buffers':[{'byteLength':len(payload)}]}
        raw=json.dumps(d).encode();raw+=b' '*((-len(raw))%4)
        self.path.write_bytes(struct.pack('<4sII',b'glTF',2,12+8+len(raw)+8+len(payload))+struct.pack('<II',len(raw),0x4e4f534a)+raw+struct.pack('<II',len(payload),0x004e4942)+payload)
        return check(self.path,self.era,allow_subset=True)
    def test_candidate_channels_pass(self):self.assertTrue(self.run_check()['passed'])
    def test_default_white_fails(self):
        m=copy.deepcopy(self.material);del m['pbrMetallicRoughness']['baseColorTexture'];self.assertFalse(self.run_check(m)['passed'])
    def test_correct_flat_color_still_rejects_silent_variation_loss(self):
        m=copy.deepcopy(self.material);del m['pbrMetallicRoughness']['baseColorTexture'];m['pbrMetallicRoughness']['baseColorFactor']=self.spec['base_color_linear']+[1];r=self.run_check(m)
        self.assertIn('Authored variation silently lost or texture is constant',r['failures'][0]['issues'])
    def test_wrong_color_space_fails(self):
        p=np.full((8,8,3),self.spec['base_color_linear'])*255;b=io.BytesIO();Image.fromarray(p.astype('uint8')).save(b,format='PNG');self.images[0]=b.getvalue()
        self.assertIn('Linear-light mean outside source palette tolerance',self.run_check()['failures'][0]['issues'])
    def test_multiplier_detected(self):
        m=copy.deepcopy(self.material);m['pbrMetallicRoughness']['baseColorFactor']=[.5,.5,.5,1];self.assertFalse(self.run_check(m)['passed'])
    def test_roughness_detected(self):
        m=copy.deepcopy(self.material);m['pbrMetallicRoughness']['roughnessFactor']=.9;self.assertFalse(self.run_check(m)['passed'])
    def test_normal_drop_detected(self):
        m=copy.deepcopy(self.material);del m['normalTexture'];self.assertFalse(self.run_check(m)['passed'])
    def test_source_calls_are_extracted(self):
        s=source_specs('2017');self.assertEqual(s['Secondary iron rust']['base_color_linear'],[.14,.071,.035]);self.assertEqual(s['Secondary original abstract marking 2']['base_color_linear'],[.51,.35,.035])

if __name__=='__main__':unittest.main()
