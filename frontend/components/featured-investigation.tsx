'use client';
import Link from 'next/link';
import {useDemo} from './demo-connection';
import {useRead} from './use-read';
import {ReadMessage} from './read-state';
import {Icon} from './icons';
import {caseHref} from '../lib/read/cases';

const investigationId='INV-B09-b9d4d66e130ed348c4f6a50e9d66a891';
const stages=['Report','Investigation','Evidence','Plan & approval','Work','Monitoring & memory'];

export function FeaturedInvestigation(){
 const demo=useDemo();
 const saved=useRead('featured-road-investigation',async signal=>{
  const investigation=(await demo.connection.client.request('GET /api/v1/investigations/{id}',{params:{id:investigationId},signal})).data;
  const plan=investigation.current_plan_id?(await demo.connection.client.request('GET /api/v1/plans/{id}',{params:{id:investigation.current_plan_id},signal})).data:null;
  return {investigation,plan};
 });
 const complete=saved.data?.investigation.status==='COMPLETED'&&saved.data?.plan?.status==='COMPLETED';
 return <section className="featured-investigation" aria-labelledby="featured-investigation-title">
  <div className="featured-investigation-body">
   <div>
    <p className="eyebrow">START HERE · FEATURED CASE</p>
    <h2 id="featured-investigation-title">Why did the potholes keep coming back?</h2>
    <p className="featured-investigation-description">Start with a road that kept sinking at Market Junction. Follow the saved investigation through evidence, a reviewed repair plan, human approval and independent follow-up.</p>
    <p className="featured-investigation-origin">Recorded AI investigation · Analyst-assisted plan · Simulated field work</p>
   </div>
   <div className="featured-investigation-action">
    {saved.status==='ready'?<>
     <span className="small-tag">{complete?'Completed investigation':'Recorded investigation'}</span>
     <Link className="button primary" href={caseHref({investigation:investigationId,section:'report'})}>
      {complete?'Follow a complete investigation':'Follow this investigation'} <Icon name="arrow" size={17}/>
     </Link>
     <span>Begin with the original report.</span>
    </>:saved.status==='loading'?<p role="status">Checking the saved case…</p>:<ReadMessage state={saved} resourceName="featured investigation" retry={saved.refresh}/>}
   </div>
  </div>
  <ol className="featured-investigation-stages" aria-label="Six stages of the case walkthrough">
   {stages.map((stage,index)=><li key={stage}><span aria-hidden="true">{String(index+1).padStart(2,'0')}</span>{stage}</li>)}
  </ol>
 </section>;
}
