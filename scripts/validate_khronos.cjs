/* Full, untruncated Khronos validation of embedded-asset review GLBs. */
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const modules=process.env.STATION_NODE_MODULES||path.resolve(__dirname,'../../3d-tools/node/node_modules');
const v=require(path.join(modules,'gltf-validator'));
(async()=>{
 const [input,output]=process.argv.slice(2);if(!input||!output)throw Error('Use input.glb report.json');
 const bytes=fs.readFileSync(input);
 const report=await v.validateBytes(new Uint8Array(bytes),{uri:path.basename(input),format:'glb',maxIssues:0,externalResourceFunction:async(uri)=>{throw Error('External resource not allowed: '+uri)}});
 report.artifact_sha256=crypto.createHash('sha256').update(bytes).digest('hex');report.artifact_bytes=bytes.length;
 fs.writeFileSync(output,JSON.stringify(report,null,2));
 console.log(JSON.stringify({file:input,errors:report.issues.numErrors,warnings:report.issues.numWarnings,infos:report.issues.numInfos,truncated:report.issues.truncated,sha256:report.artifact_sha256}));
 if(report.issues.numErrors||report.issues.truncated)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=2});
