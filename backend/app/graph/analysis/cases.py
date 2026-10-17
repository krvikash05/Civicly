"""Historical candidates from stored relationships, never fabricated resolutions."""
from collections import defaultdict
from app.graph.schema import timestamp
from .models import AnalysisRow


def retrieve(r,q):
    gaps=[];assets=set(q.asset_ids);clusters=set();zone=q.zone_id;issue=q.issue_type
    before=q.before or q.as_of;exclude=q.seed_incident_id;seed=None
    if exclude:
        seed=r.root(exclude,'Incident');issue=issue or seed.properties['issue_type']
        if timestamp(seed.properties['started_at'])<timestamp(before):before=seed.properties['started_at']
        context=r.paths('seed_context',id=exclude)
        assets|={p.node_ids[-1] for p in context if r.edges[p.edge_ids[-1]].kind=='AFFECTS'}
        clusters|={p.node_ids[-1] for p in context if r.edges[p.edge_ids[-1]].kind=='PART_OF'}
        locations=[p.node_ids[-1] for p in context if r.edges[p.edge_ids[-1]].kind=='OCCURRED_AT']
        if locations and q.max_hops>=2:
            zones=r.paths('zone_context',locations=locations)
            if not zone and zones:zone=zones[0].node_ids[-1]
    if zone:r.root(zone,'Zone')
    derived=set();connectors=2 if seed else 1
    for id in sorted(assets):
        r.root(id,'InfrastructureAsset')
        if q.max_hops>connectors:
            for direction in ('down','up'):
                derived|={p.node_ids[-1] for p in r.paths(direction,id=id,_hops=q.max_hops-connectors)}
    derived-=assets
    params={'assets':sorted(assets|derived),'after':timestamp(q.after).strftime('%Y-%m-%dT%H:%M:%S.%f') if q.after else None,
        'before':timestamp(before).strftime('%Y-%m-%dT%H:%M:%S.%f'),'exclude':exclude,'zone':zone,'issue':issue,'clusters':sorted(clusters)}
    matches=[]
    if assets:matches+=r.paths('case_asset',**params)
    if zone:
        if q.max_hops>=2:matches+=r.paths('case_zone',**params)
        else:gaps.append('Zone branch needs2 total hops and was omitted')
    if clusters:matches+=r.paths('case_cluster',**params)
    if issue:matches+=r.paths('case_issue',**params)
    ids=sorted({p.node_ids[0] for p in matches})
    context=r.paths('case_context',incidents=ids) if ids else []
    asset_by_inc=defaultdict(set);cluster_by_inc=defaultdict(set);location_by_inc=defaultdict(set)
    for e in r.edges.values():
        r.step()
        if e.kind=='AFFECTS':asset_by_inc[e.source].add(e.target)
        elif e.kind=='PART_OF':cluster_by_inc[e.source].add(e.target)
        elif e.kind=='OCCURRED_AT':location_by_inc[e.source].add(e.target)
    locations=sorted({loc for id in ids for loc in location_by_inc[id]})
    zones=r.paths('zone_context',locations=locations) if locations and q.max_hops>=2 else []
    zone_by_location=defaultdict(set)
    for e in r.edges.values():
        r.step()
        if e.kind=='IN_ZONE':zone_by_location[e.source].add(e.target)
    all_assets=sorted({asset for id in ids for asset in asset_by_inc[id]})
    history=[]
    for template,length in [('inspection',1),('inspection_evidence',2),('work_order',2),('outcome',3)]:
        if all_assets and q.max_hops>=length:history+=r.paths(template,assets=all_assets)
        elif all_assets:gaps.append(f'{template} history branch omitted by hop budget')
    rows=[]
    for id in ids:
        r.step();n=r.nodes[id];own=[p for p in context if p.node_ids[0]==id]
        current_assets=asset_by_inc[id];current_clusters=cluster_by_inc[id];current_locations=location_by_inc[id]
        current_zones={z for loc in current_locations for z in zone_by_location[loc]}
        if q.issue_type and n.properties['issue_type']!=q.issue_type:continue
        if q.zone_id and q.zone_id not in current_zones:continue
        hist=[p for p in history if p.node_ids[0] in current_assets]
        histnodes={x for p in hist for x in p.node_ids};ins={x for x in histnodes if r.nodes[x].kind=='Inspection'}
        orders={x for x in histnodes if r.nodes[x].kind=='WorkOrder'};outcomes={x for x in histnodes if r.nodes[x].kind=='InterventionOutcome'}
        factors={'shared_asset_count':len(current_assets&assets),'drainage_dependency_asset_count':len(current_assets&derived),
            'shared_cluster_count':len(current_clusters&clusters),'same_zone':bool(zone and zone in current_zones),
            'same_issue':bool(issue and n.properties['issue_type']==issue),'started_at':n.properties['started_at'],
            'age_days':int((timestamp(q.as_of)-timestamp(n.properties['started_at'])).total_seconds()//86400),
            'inspection_context_count':len(ins),'work_order_context_count':len(orders),'outcome_context_count':len(outcomes)}
        missing=['Asset-linked interventions are context, not proof they resolved this incident']
        if not ins:missing.append('No linked historical inspection in bounded export')
        if not orders:missing.append('No linked historical repair/work order in bounded export')
        if not outcomes:missing.append('No linked historical outcome in bounded export')
        if not current_assets:missing.append('No qualifying asset association; category/zone similarity is weak context')
        related_context=[p for p in r.proofs.values() if (p.context['template'] in ('down','up') and p.node_ids[-1] in current_assets) or p.context['template']=='seed_context' or (p.context['template']=='zone_context' and p.node_ids[0] in current_locations)]
        relevant=[p for p in [*matches,*own,*hist,*related_context] if id in p.node_ids or p in hist or p in related_context]
        rows.append(AnalysisRow(id=id,related_ids=tuple(sorted(current_assets|ins|orders|outcomes)),factors=factors,
            path_ids=tuple(sorted({p.id for p in relevant})),gaps=tuple(missing)))
    rows.sort(key=lambda row:(-row.factors['shared_asset_count'],-row.factors['drainage_dependency_asset_count'],
        -row.factors['shared_cluster_count'],-int(row.factors['same_zone']),-int(row.factors['same_issue']),
        -timestamp(row.factors['started_at']).timestamp(),row.id))
    if not rows:gaps.append('No historical candidates within time/evidence/budget filters; no history manufactured')
    gaps+=['Ranking is lexicographic over declared factors; similarity is not causal or resolution proof',
           'Case memory/GraphRAG/recurrence classification are not implemented']
    return rows,gaps
