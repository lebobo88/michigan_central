/* Optional compact review asset. Full-precision source GLB is never overwritten. */
const fs=require('fs'),path=require('path');
const modules=process.env.STATION_NODE_MODULES||path.resolve(__dirname,'../../3d-tools/node/node_modules');
const {NodeIO}=require(path.join(modules,'@gltf-transform/core'));
const {ALL_EXTENSIONS}=require(path.join(modules,'@gltf-transform/extensions'));
const {dedup,prune,quantize}=require(path.join(modules,'@gltf-transform/functions'));
(async()=>{
const [input,output]=process.argv.slice(2);if(!input||!output||path.resolve(input)===path.resolve(output))throw Error('Use distinct input.glb output.glb');
const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).setAllowNetwork(false);const d=await io.read(input);
await d.transform(dedup(),prune({keepAttributes:true,keepLeaves:true,keepExtras:true,keepSolidTextures:true}),quantize({pattern:/^(POSITION|NORMAL|TANGENT)$/,quantizationVolume:'mesh',quantizePosition:16,quantizeNormal:12,cleanup:false}),dedup(),prune({keepAttributes:true,keepLeaves:true,keepExtras:true,keepSolidTextures:true}));
await io.write(output,d);console.log(JSON.stringify({input,output,before:fs.statSync(input).size,after:fs.statSync(output).size,operations:['deduplicate','retain UVs/room groups/coverage markers and authored near-flat texture channels','16bit mesh-local position quantization;12bit normal precision;float32 UVs preserved'],status:'preview only; source precision unchanged'}));
})().catch(e=>{console.error(e);process.exitCode=1});
