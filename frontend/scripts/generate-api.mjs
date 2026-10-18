import {readFile, writeFile, mkdir} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {compile} from 'json-schema-to-typescript';
const root = new URL('../../', import.meta.url);
const models = JSON.parse(await readFile(new URL('contracts/api_models.json',root),'utf8'));
const contract = JSON.parse(await readFile(new URL('contracts/api_endpoints.json',root),'utf8'));
const header = '/* Generated from Civicly contracts. Run npm run generate:api. Do not edit. */';
const schema = {title:'ApiModels',type:'object',additionalProperties:false,
 properties:Object.fromEntries(Object.keys(models.$defs).map(key=>[key,{$ref:`#/$defs/${key}`}])),
 required:Object.keys(models.$defs),$defs:models.$defs};
const types = await compile(schema,'ApiModels',{bannerComment:header,ignoreMinAndMaxItems:true,format:true});
const routes = Object.fromEntries(contract.routes.map(route=>[`${route.method} ${route.path}`,route]));
const routeTypes = Object.entries(routes).map(([key,r])=>{
 const req = r.request_schema_id ? `ApiModels[${JSON.stringify(r.request_schema_id)}]` : 'undefined';
 const response = r.response_schema_id ? `ApiModels[${JSON.stringify(r.response_schema_id)}]` : 'unknown';
 const query = r.query_schema_id ? `ApiModels[${JSON.stringify(r.query_schema_id)}]` : (r.query_parameters?.length ? '{limit?: number; cursor?: string}' : 'Record<string, never>');
 return `  ${JSON.stringify(key)}: {request: ${req}; response: ${response}; query: ${query}};`;
}).join('\n');
const output = new Map([
 ['models.ts', types],
 ['schemas.json', JSON.stringify({$defs:models.$defs})+'\n'],
 ['routes.ts', `${header}\nimport type {ApiModels} from './models';\nexport const routes = ${JSON.stringify(routes,null,2)} as const;\nexport interface ApiRoutes {\n${routeTypes}\n}\n`],
]);
const directory = new URL('../lib/generated/',import.meta.url);await mkdir(directory,{recursive:true});
let changed = false;
for(const [name,content] of output){
 const path = new URL(name,directory);
 if(process.argv.includes('--check')){
  const current = await readFile(path,'utf8').catch(()=>null);
  if(current!==content){console.error(`STALE generated file: ${name}`);changed=true;}
 }else await writeFile(path,content);
}
if(changed)process.exitCode=1;
else console.log(`PASS: ${Object.keys(models.$defs).length} generated model schemas / ${Object.keys(routes).length} route contracts${process.argv.includes('--check')?' are current':''}.`);
