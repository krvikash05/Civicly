import {demoSession} from '../../../lib/api/proxy';
export const dynamic='force-dynamic';
export async function POST(request:Request){
  const response=await demoSession(request,{origin:process.env.CIVICLY_API_ORIGIN,password:process.env.CIVICLY_DEMO_PASSWORD,operator:process.env.CIVICLY_DEMO_OPERATOR_ID});
  return response;
}
