'use client';
import {useEffect,useRef,useState} from 'react';
import {useDemo} from './demo-connection';
import {ApiError} from '../lib/api/errors';
import {LatestRead} from '../lib/read/latest';
export type ReadState<T>={status:'loading'|'ready'|'error'|'unavailable';data:T|null;message:string;requestId:string|null};
export function useRead<T>(key:string,load:(signal:AbortSignal)=>Promise<T>,enabled=true):ReadState<T>&{refresh:()=>void}{
 const demo=useDemo();const [refresh,setRefresh]=useState(0);const loader=useRef(load);loader.current=load;
 const [saved,setSaved]=useState<{owner:object|null;key:string;state:ReadState<T>}|null>(null);
 useEffect(()=>{
  if(demo.status!=='connected'||!demo.identity||!enabled)return;
  const read=new LatestRead<T>();const owner=demo.identity;
  setSaved(prev => {
   if (prev && prev.owner === owner && prev.key === key && prev.state.data !== null) {
    return prev;
   }
   return {owner,key,state:{status:'loading',data:null,message:'Loading recorded data…',requestId:null}};
  });
  read.run(signal=>loader.current(signal),data=>setSaved({owner,key,state:{status:'ready',data,message:'',requestId:null}}),error=>setSaved({owner,key,state:{status:'error',data:null,message:error instanceof ApiError?error.message:'The recorded data could not be loaded.',requestId:error instanceof ApiError?error.requestId:null}}));
  return()=>read.cancel();
 },[demo.status,demo.identity,key,refresh,enabled]);
 const fresh=()=>setRefresh(value=>value+1);
 if(demo.status!=='connected')return {status:'unavailable',data:null,message:demo.message,requestId:demo.requestId,refresh:fresh};
 if(!enabled)return {status:'unavailable',data:null,message:'Select a case to get started.',requestId:null,refresh:fresh};
 if(!saved||saved.owner!==demo.identity||saved.key!==key)return {status:'loading',data:null,message:'Loading recorded data…',requestId:null,refresh:fresh};
 return {...saved.state,refresh:fresh};
}
