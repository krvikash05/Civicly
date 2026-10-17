"""Offline review evaluation; no catalog, hidden truth or delayed payload access."""
from collections import Counter
import hashlib
import json
from pathlib import Path
from app.graph.models import digest
from app.graph.schema import utc_now
from .engine import GraphAnalysis
from .models import AnalysisRequest,CaseRequest

ROOT=Path(__file__).resolve().parents[4]
CITY_GRAPH='civicly_b04_test_a84beda80da64aacbc367a9399e07a97'


def verify_city(repo,bundle):
    """Accepted B04 administrative manifest verification, not an analysis export."""
    if len(bundle['nodes'])+len(bundle['relationships'])>5000:raise ValueError('B04 source budget exceeded')
    from app.ingestion.conversion import validate_bundle
    validate_bundle(bundle)
    hashes={n['properties']['id']:repo.get_node(n['properties']['id']).content_hash for n in bundle['nodes']}
    hashes.update({e['properties']['id']:repo.get_relationship(e['properties']['id']).content_hash for e in bundle['relationships']})
    if hashes!=bundle['manifest']['record_hashes']:raise ValueError('Retained city differs from accepted manifest')
    counts=repo._read('MATCH (n:CivicEntity) RETURN count(n)')[0][0]
    edges=repo._read('MATCH ()-[r]->() RETURN count(r)')[0][0]
    if counts!=len(bundle['nodes']) or edges!=len(bundle['relationships']):raise ValueError('Unexpected city records')
    row=repo._read("MATCH (m:CivicSchemaMigration {id:$id}) RETURN m.repo_revision,m.repo_audit,m.repo_pending,m.repo_epoch,m.repo_owner",{'id':'0001'})[0]
    if row[2]:raise ValueError('City has pending mutation')
    return {'graph':repo.graph.name,'content_hash':digest(hashes),'revision':row[0],
        'audit_hash':hashlib.sha256(row[1].encode()).hexdigest(),'audit_entries':len(json.loads(row[1])),
        'writer_state_hash':digest([row[3],row[4]]),'nodes':counts,'edges':edges}


def classify_bindings(scenario,exploration):
    actual=set(scenario['actual_incident_assets']);bound=set(scenario['asset_ids']);extra=bound-actual
    proofs={id:[p.id for p in exploration.paths if p.node_ids[0] in actual and p.node_ids[-1]==id] for id in sorted(extra)}
    if bound==actual:asset_class='EXACT_RECORDED_ASSETS'
    elif actual<=bound and all(proofs.values()):asset_class='BROADER_EXPLORATORY_CANDIDATE_SET'
    elif actual<=bound:asset_class='UNPROVEN_EXTRA_BINDING_CONTEXT_WITHIN_BUDGET'
    else:asset_class='STARTING_ASSET_BINDING_SOURCE_CONFLICT'
    actual_clusters=set(scenario['actual_incident_clusters']);bound_clusters=set(scenario['cluster_ids'])
    cluster_class=('EXACT_PRIMARY_CLUSTER_SET' if actual_clusters==bound_clusters else
                   'UNSPECIFIED_CLUSTER_CONTEXT' if not bound_clusters else 'PRIMARY_CLUSTER_BINDING_SOURCE_CONFLICT')
    return {'scenario_id':scenario['scenario_id'],'recorded_asset_ids':sorted(actual),'bound_asset_ids':sorted(bound),
        'asset_classification':asset_class,'extra_binding_proof_path_ids':proofs,
        'missing_recorded_assets_from_binding':sorted(actual-bound),'unsupported_extra_bindings':sorted(id for id,p in proofs.items() if not p),
        'recorded_cluster_ids':sorted(actual_clusters),'bound_cluster_ids':sorted(bound_clusters),'cluster_classification':cluster_class,
        'rationale':'Broader requires every recorded affected asset retained and every extra backed by an explicit bounded typed network path; candidate paths justify investigation only. Missing/incompatible starting or primary bindings require source-author review, not automatic remapping.',
        'classification_limited':exploration.truncated or exploration.search_limited,
        'proof_graph_revision':exploration.graph_revision}


def evaluate_city(repo):
    bundle=json.loads((ROOT/'data/ingestion/city-v3.json').read_text())
    readiness=json.loads((ROOT/'data/ingestion/scenario-readiness.json').read_text())
    before=verify_city(repo,bundle);as_of=utc_now();engine=GraphAnalysis(repo);scenarios=[];dependencies=[]
    for scenario in readiness['scenarios']:
        actual=tuple(sorted(set(scenario['actual_incident_assets'])))
        modes={}
        for candidate in (False,True):
            component=engine.run(AnalysisRequest(operation='components',ids=actual,as_of=as_of,include_candidates=candidate))
            cases=engine.cases(CaseRequest(seed_incident_id=scenario['incident_ids'][0],as_of=as_of,include_candidates=candidate))
            modes['exploratory' if candidate else 'verified_only']={'components':component.model_dump(mode='json'),'cases':cases.model_dump(mode='json')}
            if candidate:dependencies.append(classify_bindings(scenario,component))
        classification=dependencies[-1]
        explorer=modes['exploratory'];verified=modes['verified_only']
        scenarios.append({'scenario_id':scenario['scenario_id'],'modes':modes,
            'starting_evidence':{'verified_network_paths':len(verified['components']['paths']),
                'exploratory_network_paths':len(explorer['components']['paths']),
                'historical_case_candidates':len(explorer['cases']['rows']),
                'case_search_truncated':explorer['cases']['truncated'],
                'meaningful_exploratory_context':bool(explorer['components']['paths'] or explorer['cases']['rows']),
                'binding_usable_as_broader_context':classification['asset_classification'] in ('EXACT_RECORDED_ASSETS','BROADER_EXPLORATORY_CANDIDATE_SET'),
                'verified_causal_scenario_ready':False},
            'b05_readiness':'Meaningful exploratory network/history context only; no verified drainage/causal scenario proof',
            'cross_category_source_gap':scenario['cross_category_gap'],'behavior_status':'NOT_IMPLEMENTED'})
    examples={}
    for candidate in (False,True):
        mode='exploratory' if candidate else 'verified_only'
        examples[mode]={op:engine.run(AnalysisRequest(operation=op,ids=('INLET-I01','DRAIN-D12','DRAIN-D18') if op=='criticality' else ('DRAIN-D12',),
                       as_of=as_of,include_candidates=candidate)).model_dump(mode='json') for op in ('reachability','criticality','impacted_assets','dependencies')}
        examples[mode]['shared_downstream']=engine.run(AnalysisRequest(operation='shared_downstream',incident_ids=('INC-FLOOD-02','INC-ROAD-01','INC-WASTE-01'),as_of=as_of,include_candidates=candidate)).model_dump(mode='json')
        examples[mode]['waste_dependencies']=engine.run(AnalysisRequest(operation='dependencies',ids=('WASTE-W03',),as_of=as_of,include_candidates=candidate)).model_dump(mode='json')
        examples[mode]['road_dependencies']=engine.run(AnalysisRequest(operation='components',ids=('ROAD-R08',),as_of=as_of,include_candidates=candidate)).model_dump(mode='json')
        examples[mode]['upstream']=engine.run(AnalysisRequest(operation='reachability',ids=('DRAIN-D18',),direction='upstream',as_of=as_of,include_candidates=candidate)).model_dump(mode='json')
        examples[mode]['road_historical_cases']=engine.cases(CaseRequest(asset_ids=('ROAD-R08',),as_of=as_of,include_candidates=candidate)).model_dump(mode='json')
        examples[mode]['waste_historical_cases']=engine.cases(CaseRequest(asset_ids=('WASTE-W03',),as_of=as_of,include_candidates=candidate)).model_dump(mode='json')
    status=repo._read('MATCH ()-[r:DRAINS_TO]->() RETURN r.association_status,count(r) LIMIT 10')
    kinds=repo._read('MATCH (n:CivicEntity) RETURN labels(n),count(n) LIMIT 100')
    after=verify_city(repo,bundle)
    if before!=after:raise ValueError('City source changed during evaluation')
    dependency_report={'version':1,'source_graph':repo.graph.name,'graph_revision':before['revision'],
        'accepted_bundle_content_hash':bundle['manifest']['content_hash'],'runtime_source_unchanged':True,
        'scenarios':dependencies,'asset_classification_counts':dict(Counter(s['asset_classification'] for s in dependencies)),
        'cluster_classification_counts':dict(Counter(s['cluster_classification'] for s in dependencies)),
        'remediation_dependencies':{'B08':['55 unlinked Observations: require legitimate event/asset association sources','Pickup schedule clock/alias interpretation; no guessed execution dates'],
            'B09':['Supply dated attributed physical proof before VERIFIED topology','Do not equate candidate connectivity/criticality with cause'],
            'B11':['Document owners/version/effective metadata and sourced PDF coverage'],
            'B19':['Review8 incompatible starting-asset binding sets and6 primary-cluster conflicts;3 unspecified cluster contexts',
                   'Author missing S07 source-backed cross-category topology','Supply historical repairs/decisions/outcomes and counterfactual cases',
                   'Implement authorized staged releases and evaluator-runtime isolation']},
        'prohibited_remediation':'No dataset rewrite, hidden-answer reading, date fabrication or candidate promotion in B05'}
    return {'as_of':as_of,'source_before':before,'source_after':after,'drainage_status_counts':status,'node_label_inventory':kinds,
            'examples':examples,'scenarios':scenarios,
            'limitations':['42 city DRAINS_TO remain candidate-level; verified-only drainage returns no paths',
                'No historical WorkOrder/AgentDecision/InterventionOutcome chain;1 Inspection and55 unlinked Observations',
                'Search horizon/caps qualified in every result; task DAG unavailable in city because no plans/tasks seeded',
                'Source binding classifications are source-authoring diagnostics, not causal judgments; no full scenario behavior implemented']},dependency_report
