import {proxy} from '../../../../lib/api/proxy';
export const dynamic='force-dynamic';
export async function GET(request:Request){return proxy(request,process.env.CIVICLY_API_ORIGIN);}
export async function POST(request:Request){return proxy(request,process.env.CIVICLY_API_ORIGIN);}
