'use client';
import {createContext,useContext,useEffect,useRef,useState} from 'react';
import {DemoConnection} from '../lib/api/session';
import type {DemoIdentity} from '../lib/api/session';
import {ApiError} from '../lib/api/errors';
type ConnectionState={status:'connecting'|'connected'|'unavailable'|'ended';identity:DemoIdentity|null;message:string;requestId:string|null;reconnect:()=>void;disconnect:()=>void;connection:DemoConnection};
const Context=createContext<ConnectionState|null>(null);
export function DemoProvider({children}:{children:React.ReactNode}){
  const [connection]=useState(()=>new DemoConnection());
  const [state,setState]=useState<Pick<ConnectionState,'status'|'identity'|'message'|'requestId'>>({status:'connecting',identity:null,message:'Connecting to the demo workspace…',requestId:null});
  const mounted=useRef(false);
  const generation=useRef(0);
  function reconnect(){
    const attempt=++generation.current;
    setState({status:'connecting',identity:null,message:'Connecting to the demo workspace…',requestId:null});
    connection.open().then(identity=>{if(mounted.current&&generation.current===attempt)setState({status:'connected',identity,message:'Demo connection ready',requestId:null});},error=>{
      if(mounted.current&&generation.current===attempt)setState({status:'unavailable',identity:null,message:error instanceof ApiError?error.message:'The demo connection is unavailable.',requestId:error instanceof ApiError?error.requestId:null});
    });
  }
  useEffect(()=>{
    mounted.current=true;
    connection.client.onUnauthorized(()=>{generation.current++;connection.forget();if(mounted.current)setState({status:'ended',identity:null,message:'Your demo session has ended. Reconnect to continue.',requestId:null});});
    reconnect();
    return ()=>{mounted.current=false;};
    // One automatic connection per provider; open() deduplicates Strict Mode setup.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  },[connection]);
  useEffect(()=>{
    if(!state.identity)return;
    const expire=()=>{generation.current++;connection.forget();setState({status:'ended',identity:null,message:'Your demo session has ended. Reconnect to continue.',requestId:null});};
    const check=()=>{if(Date.parse(state.identity!.expiresAt)<=Date.now())expire();};
    const timer=setTimeout(expire,Math.min(2147483647,Math.max(0,Date.parse(state.identity.expiresAt)-Date.now())));
    window.addEventListener('focus',check);return()=>{clearTimeout(timer);window.removeEventListener('focus',check);};
  },[state.identity,connection]);
  async function disconnect(){
    const attempt=++generation.current;setState({status:'ended',identity:null,message:'Demo session ended.',requestId:null});
    try{await connection.close();}catch{if(mounted.current&&generation.current===attempt)setState({status:'ended',identity:null,message:'Local session cleared. Server logout could not be confirmed; the session will expire on the backend.',requestId:null});}
  }
  return <Context.Provider value={{...state,connection,reconnect,disconnect}}>{children}</Context.Provider>;
}
export function useDemo(){const value=useContext(Context);if(!value)throw new Error('DemoProvider required');return value;}
export function DemoStatus(){
  const demo=useDemo();
  return <div className="demo-status"><span className={`connection ${demo.status}`} role="status"><span/>{demo.status==='connected'?'Demo connected':demo.status==='connecting'?'Connecting…':demo.status==='ended'?'Session ended':'Demo unavailable'}</span>{demo.status==='connected'?<details className="session-details"><summary>Demo workspace</summary><div className="session-popover"><strong>Demo analyst</strong><p>Simulated district · temporary session</p><p>Approvals and departmental actions require their authorized operators.</p><button type="button" onClick={demo.disconnect}>End demo session</button></div></details>:demo.status!=='connecting'&&<button className="reconnect-button" type="button" onClick={demo.reconnect}>Reconnect</button>}</div>;
}
export function ConnectionNotice(){
  const demo=useDemo();
  return <div className="preview-notice"><p role="status">{demo.status==='connected'?<><strong>Demo workspace connected.</strong> Active as <code>{demo.identity?.account.id ?? 'OP-ANALYST'}</code> (Role: <strong>{demo.identity?.account.role ?? 'ANALYST'}</strong>). Live investigations, FalkorDB graph evidence, and remediation plans loaded.</>:demo.message}{demo.requestId&&<span> Reference: {demo.requestId}</span>}</p></div>;
}
