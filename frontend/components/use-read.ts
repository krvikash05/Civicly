'use client';
import {useEffect,useRef,useState} from 'react';
import {useDemo} from './demo-connection';
import {ApiError} from '../lib/api/errors';
import {LatestRead} from '../lib/read/latest';
import {visibleReadState,type ReadState,type OwnedRead} from '../lib/read/read-state';
export type {ReadState} from '../lib/read/read-state';
export function useRead<T>(key:string,load:(signal:AbortSignal)=>Promise<T>,enabled=true):ReadState<T>&{refresh:()=>void}{
 const demo=useDemo();const [refresh,setRefresh]=useState(0);const loader=useRef(load);loader.current=load;
 const [saved,setSaved]=useState<OwnedRead<T>|null>(null);
 useEffect(()=>{
  if(demo.status!=='connected'||!demo.identity||!enabled)return;
  const read=new LatestRead<T>();const owner=demo.identity;
  setSaved(prev => {
   if (prev && prev.owner === owner && prev.key === key && prev.state.data !== null) {
    return prev;
   }
   return {owner,key,state:{status:'loading',data:null,message:'Loading recorded data…',requestId:null}};
  });
  read.run(signal=>loader.current(signal),data=>setSaved({owner,key,state:{status:'ready',data,message:'',requestId:null}}),error=>setSaved({owner,key,state:{status:'error',data:null,errorCode:error instanceof ApiError?error.code:undefined,httpStatus:error instanceof ApiError?error.status:undefined,message:error instanceof ApiError?error.message:'The recorded data could not be loaded.',requestId:error instanceof ApiError?error.requestId:null}}));
  return()=>read.cancel();
 },[demo.status,demo.identity,key,refresh,enabled]);
 const fresh=()=>setRefresh(value=>value+1);
 return {...visibleReadState(demo,key,enabled,saved),refresh:fresh};
}
