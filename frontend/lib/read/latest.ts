/** Small abortable read controller: stale reads never publish over a new scope. */
export class LatestRead<T>{
 private version=0;
 private controller:AbortController|null=null;
 async run(load:(signal:AbortSignal)=>Promise<T>,publish:(value:T)=>void,reject:(error:unknown)=>void){
  this.cancel();const version=this.version;const controller=new AbortController();this.controller=controller;
  try{const value=await load(controller.signal);if(version===this.version&&!controller.signal.aborted)publish(value);}catch(error){if(version===this.version&&!controller.signal.aborted)reject(error);}
 }
 cancel(){this.version++;this.controller?.abort();this.controller=null;}
}
