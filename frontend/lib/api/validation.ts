import Ajv2020 from 'ajv/dist/2020.js';
import type { ValidateFunction } from 'ajv';
import schemas from '../generated/schemas.json' with { type: 'json' };

const ajv = new Ajv2020({strict:false,allErrors:false,coerceTypes:false,useDefaults:false,removeAdditional:false,validateFormats:true});
ajv.addFormat('password',true);
ajv.addSchema({$id:'civicly',$defs:schemas.$defs});
const validators = new Map<string,ValidateFunction>();
export function validSchema(name: string, value: unknown): boolean {
  let validate = validators.get(name);
  if(!validate) { validate=ajv.compile({$ref:`civicly#/$defs/${name}`}); validators.set(name,validate); }
  return !!validate(value);
}
export function validQuery(allowed: readonly string[], schema: string | undefined, value: Record<string,unknown>): boolean {
  if(Object.keys(value).some(key=>!allowed.includes(key))) return false;
  if(schema) return validSchema(schema,value);
  return Object.entries(value).every(([key,v])=> key==='limit' ? Number.isInteger(v) && Number(v)>=1 && Number(v)<=50 : key==='cursor' && typeof v==='string' && v.length>=1 && v.length<=200);
}
