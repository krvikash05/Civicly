'use client';
import {useEffect,useRef} from 'react';
import Link from 'next/link';
import {useDemo} from './demo-connection';
import {useRead} from './use-read';
import {ReadMessage} from './read-state';
import {loadMetricRows,type MetricKind} from '../lib/read/dashboard';
import {translateStatus} from '../lib/read/display';
const labels:Record<MetricKind,string>={active_investigations:'Active investigations',pending_approvals:'Awaiting a decision',completed_work_orders:'Work completed',verified_work_orders:'Verified outcomes'};
const empty:Record<MetricKind,string>={active_investigations:'No active investigations were returned.',pending_approvals:'No plans are currently awaiting approval.',completed_work_orders:'No completed work orders were returned.',verified_work_orders:'No work orders with a verified resolution were returned.'};
export function MetricRecords({kind,onClose}:{kind:MetricKind;onClose:()=>void}){
 const demo=useDemo();const dialog=useRef<HTMLDialogElement>(null);
 const records=useRead('metric-records:'+kind,signal=>loadMetricRows(demo.connection.client,kind,signal));
 useEffect(()=>{const node=dialog.current;node?.showModal();return()=>node?.close();},[]);
 return <dialog ref={dialog} className="metric-dialog" aria-labelledby="metric-records-title" onCancel={onClose} onClose={onClose}>
  <div className="modal-header"><h2 id="metric-records-title">{labels[kind]}</h2><button type="button" className="modal-close" aria-label="Close records" onClick={onClose}>✕</button></div>
  <p className="metric-record-note">{kind==='verified_work_orders'?'Work orders whose latest recorded assessment verifies resolution. Open a case to review its follow-up evidence.':kind==='completed_work_orders'?'Completed work orders. Completion alone does not establish that the problem was resolved.':kind==='pending_approvals'?'Plans waiting for an authorized approval. Opening a plan does not approve it.':'Investigations that are neither completed nor cancelled. Open a case to review its findings and next step.'}</p>
  {records.status==='unavailable'?<p role="status">{records.message}</p>:records.status!=='ready'?<ReadMessage state={records} resourceName="matching records" retry={records.refresh}/>:records.data?.length?<ul className="metric-record-list">{records.data.map(row=><li key={row.id}><Link href={row.href}><strong>{row.title}</strong><span>{row.detail}</span><span className="metric-record-action">{translateStatus(row.status)} · {kind==='pending_approvals'?'View plan & approval':kind==='completed_work_orders'?'View Report':kind==='verified_work_orders'?'View monitoring & memory':'View investigation'} →</span></Link></li>)}</ul>:<p className="metric-record-empty" role="status">{empty[kind]}</p>}
  <p className="metric-record-note">Current accessible records; counts can change between reads. {records.status==='ready'?`${records.data?.length ?? 0} matching records loaded.`:''}</p>
 </dialog>;
}
