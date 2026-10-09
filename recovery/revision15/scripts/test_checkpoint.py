"""Standard-library-only unit tests. Never imports bpy or launches Blender."""
import sys
sys.dont_write_bytecode = True
import ast,copy,json,struct,tempfile,unittest,zipfile,stat
from pathlib import Path
from glb_io import GLB,sha,digest,canonical
import verify_package as vp
import preserve_2026 as preservation
from verify_references import verify as verify_refs
PKG=Path(__file__).resolve().parents[1]
class PackageTests(unittest.TestCase):
    def test_reference_payloads(self):self.assertTrue(verify_refs()['passed'])
    def test_python_syntax(self):
        for p in PKG.rglob('*.py'):compile(p.read_bytes(),str(p),'exec')
    def test_runtime_dependencies(self):
        required=['original/integration/scripts/artifact_provenance.py','original/integration/scripts/placement_checks.py','original/integration/scripts/bounded_import_checks.py','original/integration/scripts/candidates/glass_shell_rules.py','original/integration/scripts/candidates/elevator_lobby_detail.py','original/dependencies/repair_glb_tangents.py']
        for p in required:self.assertTrue((PKG/p).is_file(),p)
        tree=ast.parse((PKG/'original/study/build_study.py').read_bytes());names=json.loads((PKG/'recovery_contract.json').read_text())['geometry_function_names'];defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
        globals_needed=set()
        for n in defs:
            assigned={x.id for x in ast.walk(n) if isinstance(x,ast.Name) and isinstance(x.ctx,ast.Store)}|{a.arg for a in ast.walk(n) if isinstance(a,ast.arg)}
            globals_needed|={x.id for x in ast.walk(n) if isinstance(x,ast.Name) and isinstance(x.ctx,ast.Load)}-assigned
        self.assertLessEqual(globals_needed,{'bpy','bmesh','math','s','ERA','terra','metal','cy','front','new','mesh','extrude','box','rounded','ring','bead','add_detail','list','tuple','range','len','max','abs','enumerate','any','reversed'})
    def test_original_geometry_emission_without_blender(self):
        import types,math,collections
        source=ast.parse((PKG/'original/study/build_study.py').read_bytes());contract=json.loads((PKG/'recovery_contract.json').read_text());defs=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in contract['geometry_function_names']]
        f32=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
        for era in ['2017','2026']:
            old=types.SimpleNamespace(name='concourse west small opening profiled lintel');objects=[old];removed=[];emitted=[];counter=collections.Counter()
            def remove(ob,do_unlink):removed.append(ob.name);objects.remove(ob)
            ns={'bpy':types.SimpleNamespace(data=types.SimpleNamespace(objects=types.SimpleNamespace(remove=remove))),'bmesh':None,'math':math,'s':types.SimpleNamespace(objects=objects),'ERA':era,'terra':'terracotta','metal':'metal','cy':63.4,'front':29.4894,'new':[]}
            exec(compile(ast.Module(body=defs,type_ignores=[]),'pinned original functions','exec'),ns)
            def capture(name,verts,faces,mat):
                n=counter[name];counter[name]+=1;actual=name+(f'.{n:03d}' if n else '');emitted.append((actual,verts,faces,mat))
            ns['mesh']=capture;ns['add_detail']()
            ref=json.loads((PKG/f'references/details_{era}.json').read_text())['objects'];self.assertEqual([r[0] for r in emitted],[r['name'] for r in ref]);self.assertEqual(removed,['concourse west small opening profiled lintel'])
            for generated,accepted in zip(emitted,ref):
                name,verts,faces,mat=generated;self.assertEqual(len(verts),accepted['placement']['evaluated_vertices']);self.assertEqual(sum(len(f)-2 for f in faces),accepted['placement']['evaluated_polygons'])
                bounds=[[min(f32(v[k]) for v in verts) for k in range(3)],[max(f32(v[k]) for v in verts) for k in range(3)]]
                delta=max(abs(a-b) for x,y in zip(bounds,accepted['placement']['evaluated_world_bounds']) for a,b in zip(x,y));self.assertLess(delta,1e-5,name)
    def test_world_transform_hierarchy(self):
        from glb_io import scene_transforms
        d={'nodes':[{'name':'parent','translation':[1,2,3],'children':[1]},{'name':'child','translation':[4,5,6]}]}
        out=scene_transforms(d);self.assertEqual(out['child']['parent'],'parent');self.assertEqual([out['child']['world_matrix'][i][3] for i in range(3)],[5,7,9])
        d['nodes'][1]['children']=[0]
        with self.assertRaises(ValueError):scene_transforms(d)
    def test_driver_does_not_trust_exit_zero(self):
        import importlib.util,types,sys
        from unittest import mock
        spec=importlib.util.spec_from_file_location('recovery_driver_under_test',PKG/'recover.py');driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)
        pin=json.loads((PKG/'recovery_contract.json').read_text())['inputs']['2017']
        with tempfile.TemporaryDirectory(dir=PKG.parent) as tmp:
            root=Path(tmp);source=root/'input.blend';source.write_bytes(b'unit-test stub, not Blender');out=root/'result'
            args=['recover.py','--blender','unit-test-blender-stub','--era','2017','--r14-blend',str(source),'--output',str(out)]
            with mock.patch.object(sys,'argv',args),mock.patch.object(driver,'verify_directory',return_value={'passed':True}),mock.patch.object(driver,'verify_refs',return_value={'passed':True}),mock.patch.object(driver,'digest',return_value=pin['r14_blend_sha256']),mock.patch.object(driver.shutil,'which',return_value='nonexistent-unit-test-command'),mock.patch.object(driver.subprocess,'run',return_value=types.SimpleNamespace(returncode=0)) as run:
                with self.assertRaisesRegex(RuntimeError,'without required source result files'):driver.main()
                run.assert_called_once();self.assertFalse((out/'RECOVERY_RESULT.json').exists())
    def test_zip_attack_names(self):
        for name in ['../evil','/abs','a/../b','a//b','./x','C:/x','a\\b','a/']:
            with self.assertRaises(ValueError):vp.safe_name(name)
    def test_zip_symlink_duplicate_and_hash(self):
        with tempfile.TemporaryDirectory(dir=PKG.parent) as tmp:
            tmp=Path(tmp);manifest={'schema':1,'blender_reconstruction':'NOT YET VALIDATED','files':{'a.txt':{'bytes':1,'sha256':sha(b'x')}}}
            for mode in ['good','symlink','duplicate','wrong_hash','extra']:
                p=tmp/(mode+'.zip')
                with zipfile.ZipFile(p,'w') as z:
                    z.writestr('PACKAGE_MANIFEST.json',json.dumps(manifest))
                    i=zipfile.ZipInfo('a.txt');i.create_system=3;i.external_attr=((stat.S_IFLNK if mode=='symlink' else stat.S_IFREG)|0o644)<<16;z.writestr(i,b'z' if mode=='wrong_hash' else b'x')
                    if mode=='duplicate':
                        import warnings
                        with warnings.catch_warnings():warnings.simplefilter('ignore');z.writestr('a.txt',b'x')
                    if mode=='extra':z.writestr('extra',b'x')
                if mode=='good':self.assertTrue(vp.verify_zip(p)['passed'])
                else:
                    with self.assertRaises(ValueError):vp.verify_zip(p)

class PreservationTests(unittest.TestCase):
    def fixture(self,root):
        d={'asset':{'version':'2.0'},'buffers':[{'byteLength':0}],'bufferViews':[],'accessors':[],'meshes':[],'materials':[{'name':'Test material','pbrMetallicRoughness':{'metallicFactor':0}}],'nodes':[],'scenes':[{'nodes':[0,1,2,3]}],'scene':0};blob=bytearray();reference=[];payload=bytearray()
        for j in range(4):
            attrs={};descs={};data={}
            for label,typ,ct,values in [('POSITION','VEC3',5126,[0,0,0,1,0,0,0,1,0]),('NORMAL','VEC3',5126,[0,0,1]*3),('TEXCOORD_0','VEC2',5126,[0,0,1,0,0,1]),('TANGENT','VEC4',5126,[1,0,0,1]*3),('indices','SCALAR',5125,[0,1,2])]:
                raw=struct.pack('<'+('I' if ct==5125 else 'f')*len(values),*values);view=len(d['bufferViews']);d['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':len(raw)});blob.extend(raw);ai=len(d['accessors']);desc={'componentType':ct,'count':3,'type':typ};d['accessors'].append({'bufferView':view,**desc});attrs[label]=ai;descs[label]=desc;data[label]=raw
            name='test '+str(j);p={'attributes':{k:v for k,v in attrs.items() if k!='indices'},'indices':attrs['indices'],'material':0};d['meshes'].append({'name':name,'primitives':[p]});d['nodes'].append({'name':name,'mesh':j})
            material=d['materials'][0];r={'mesh':name,'material_fingerprint_sha256':sha(canonical(material)),'guards':{},'restore':{}}
            for label in ['POSITION','NORMAL','indices']:r['guards'][label]={'sha256':sha(data[label]),'accessor':descs[label]}
            for label in ['TEXCOORD_0','TANGENT']:
                raw=data[label];r['restore'][label]={'offset':len(payload),'bytes':len(raw),'sha256':sha(raw),'accessor':descs[label]};payload.extend(raw)
            reference.append(r)
        d['buffers'][0]['byteLength']=len(blob);js=json.dumps(d).encode();js+=b' '*((-len(js))%4);raw=struct.pack('<4sII',b'glTF',2,28+len(js)+len(blob))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(blob),0x004e4942)+blob
        (root/'references').mkdir();(root/'references/inherited_2026.bin').write_bytes(payload);(root/'references/inherited_2026.json').write_text(json.dumps({'binary_sha256':sha(payload),'objects':reference}));path=root/'candidate.glb';path.write_bytes(raw);return path,raw
    def test_guarded_recovery_and_rejections(self):
        with tempfile.TemporaryDirectory(dir=PKG.parent) as tmp:
            root=Path(tmp);path,baseline=self.fixture(root);saved=preservation.PKG;preservation.PKG=root
            try:
                g=GLB(path);_,p=g.primitive('test 0');uv=g.layout(p['attributes']['TEXCOORD_0']);tan=g.layout(p['attributes']['TANGENT']);pos=g.layout(p['attributes']['POSITION']);candidate=bytearray(baseline);struct.pack_into('<f',candidate,uv['start'],.5);struct.pack_into('<f',candidate,tan['start'],.75);path.write_bytes(candidate);before=digest(path)
                report=preservation.recover(path,root/'restored.glb');self.assertTrue(report['passed']);self.assertEqual((root/'restored.glb').read_bytes(),baseline);self.assertEqual(digest(path),before)
                for bad,offset in [('position',pos['start']),('handedness',tan['start']+12)]:
                    data=bytearray(candidate);struct.pack_into('<f',data,offset,.5);path.write_bytes(data)
                    with self.assertRaises(ValueError):preservation.recover(path,root/(bad+'.glb'))
                    self.assertFalse((root/(bad+'.glb')).exists())
                # Semantic material and declared accessor alias changes must fail before output.
                def rewrite(doc,original):
                    size=struct.unpack_from('<I',original,12)[0];binary=original[28+size:];js=json.dumps(doc).encode();js+=b' '*((-len(js))%4)
                    return struct.pack('<4sII',b'glTF',2,28+len(js)+len(binary))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(binary),0x004e4942)+binary
                doc=copy.deepcopy(g.doc);doc['materials'][0]['pbrMetallicRoughness']['metallicFactor']=1;path.write_bytes(rewrite(doc,candidate))
                with self.assertRaises(ValueError):preservation.recover(path,root/'material.glb')
                self.assertFalse((root/'material.glb').exists())
                doc=copy.deepcopy(g.doc);doc['accessors'].append(copy.deepcopy(doc['accessors'][p['attributes']['TEXCOORD_0']]));path.write_bytes(rewrite(doc,candidate))
                with self.assertRaises(ValueError):preservation.recover(path,root/'alias.glb')
                self.assertFalse((root/'alias.glb').exists())
                path.write_bytes(baseline);r=preservation.recover(path,root/'noop.glb');self.assertEqual(r['changed_ranges'],0);self.assertEqual((root/'noop.glb').read_bytes(),baseline)
            finally:preservation.PKG=saved
if __name__=='__main__':unittest.main(verbosity=2)
