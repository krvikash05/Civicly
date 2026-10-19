export type ReadState<T>={status:'loading'|'ready'|'error'|'unavailable';data:T|null;message:string;requestId:string|null;errorCode?:string;httpStatus?:number};
export type OwnedRead<T>={owner:object|null;key:string;state:ReadState<T>};
type ReadConnection={status:'connecting'|'connected'|'unavailable'|'ended';identity:object|null;message:string;requestId:string|null};

/** Connecting is not failure; cached data belongs to exactly one session and scope. */
export function visibleReadState<T>(connection:ReadConnection,key:string,enabled:boolean,saved:OwnedRead<T>|null):ReadState<T>{
  if(!enabled)return {status:'unavailable',data:null,message:'Select a case to get started.',requestId:null};
  if(connection.status==='connecting')return {status:'loading',data:null,message:'Connecting to the demo workspace…',requestId:null};
  if(connection.status!=='connected')return {status:'unavailable',data:null,message:connection.message,requestId:connection.requestId};
  if(!connection.identity||!saved||saved.owner!==connection.identity||saved.key!==key)return {status:'loading',data:null,message:'Loading recorded data…',requestId:null};
  return saved.state;
}
