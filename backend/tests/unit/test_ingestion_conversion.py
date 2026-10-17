from copy import deepcopy
import json
from pathlib import Path
import subprocess

import pytest

from app.graph.schema import Registry,SchemaError
from app.ingestion.conversion import convert,validate_bundle,SourceError,ROOT,edge_identity
from tests.ingestion_examples import example,source,with_dependencies,complete_source,COMPILED

R=Registry()


@pytest.mark.parametrize('kind',sorted(R.nodes))
def test_each_registry_source_node_type(kind):
    n=example(kind);bundle,report=convert(complete_source([n]),COMPILED)
    assert not report['quarantine']
    assert any(x['label']==kind and x['properties']['id']==n['properties']['id'] for x in bundle['nodes'])
    validate_bundle(bundle)


@pytest.mark.parametrize('kind',sorted(R.edges))
def test_each_registry_source_relationship_type(kind):
    a=example(R.edges[kind]['from'][0],'SOURCE');b=example(R.edges[kind]['to'][0],'TARGET')
    e={'type':kind,'source_id':'SOURCE','target_id':'TARGET','properties':{}}
    bundle,report=convert(complete_source([a,b],[e]),COMPILED)
    assert not report['quarantine']
    assert any(x['properties']['id']==edge_identity(e) for x in bundle['relationships'])


def test_all_55_numeric_measurements_lossless():
    raw=json.loads((ROOT/'contracts/seed_graph_expanded.json').read_text())
    obs=[n for n in raw['nodes'] if n['label']=='Observation']
    bundle,report=convert(source(obs),COMPILED)
    by={n['properties']['id']:n['properties'] for n in bundle['nodes']}
    assert len(obs)==55 and not report['quarantine']
    for i,n in enumerate(obs):
        old=n['properties'];new=by[old['id']]
        assert new['value']==old['value_number'] and new['unit']==old['unit']
        assert new['observed_at']==old['observed_at'] and new['source_kind']==old['source_kind']
        assert 'value_number' not in new and report['provenance'][old['id']]['pointer']==f'/nodes/{i}'
    assert sum(c['field']=='value_number' for c in report['changes'])==55


@pytest.mark.parametrize('bad',[{'unknown':1},{'name':None},{'created_at':'broken'},{'municipality_id':'other'}, {'schema_version':True}])
def test_unknown_type_scope_dates_and_versions_quarantined(bad):
    n=example('Location');n['properties'].update(bad)
    bundle,report=convert(source([n]),COMPILED)
    assert len(report['quarantine'])==1 and report['quarantine'][0]['record']==n
    assert not any(x['properties']['id']==n['properties']['id'] for x in bundle['nodes'])


def test_missing_required_and_reference_and_duplicate_ids():
    n=example('Location');del n['properties']['name']
    raw=source([n,example('OperatorAccount'),example('Zone','DUP'),example('Zone','DUP')])
    bundle,report=convert(raw,COMPILED)
    assert len(report['quarantine'])==4
    with pytest.raises(SchemaError):R.validate_node('PickupExecution',{**example('PickupExecution')['properties'],'schema_version':3,'municipality_id':'demo-city','status':'NOT_VALID'})


def test_endpoint_and_evidence_resolution_quarantine():
    e={'type':'DRAINS_TO','source_id':'A','target_id':'MISSING','properties':{}}
    raw=source([example('DrainSegment','A'),example('DrainSegment','B')],[e,{**e,'target_id':'B','properties':{'source_evidence_id':'NONE'}}])
    bundle,report=convert(raw,COMPILED)
    assert [q['reason'] for q in report['quarantine']]==['UNRESOLVED_ENDPOINT','UNRESOLVED_EVIDENCE_REFERENCE']


def test_verification_requires_actual_dated_evidence_no_invented_date():
    ev=example('Evidence','EV');ev['properties']['reliability']='VERIFIED'
    e={'type':'DRAINS_TO','source_id':'A','target_id':'B','properties':{'association_status':'VERIFIED','source_evidence_id':'EV'}}
    raw=source([example('DrainSegment','A'),example('DrainSegment','B'),ev],[e])
    bundle,report=convert(raw,COMPILED)
    converted=next(n['properties'] for n in bundle['nodes'] if n['properties']['id']=='EV')
    assert 'observed_at' not in converted and converted['reliability']=='UNVERIFIED'
    assert next(x for x in bundle['relationships'] if x['type']=='DRAINS_TO')['properties']['association_status']=='CANDIDATE'
    ev['properties'].update(observed_at='2026-08-31T00:00:00Z',source_record_id='ACTUAL-SYNTHETIC-RECORD')
    bundle,report=convert(raw,COMPILED)
    assert next(x for x in bundle['relationships'] if x['type']=='DRAINS_TO')['properties']['association_status']=='VERIFIED'


def test_temporal_and_schedule_conflict_quarantine():
    route=example('CollectionRoute','R');a=example('ServiceSchedule','A');b=example('ServiceSchedule','B')
    edges=[{'type':'HAS_SCHEDULE','source_id':'R','target_id':id,'properties':{}} for id in ('A','B')]
    bundle,report=convert(source([route,a,b],edges),COMPILED)
    assert len(report['quarantine'])==1 and 'Schedule overlap' in report['quarantine'][0]['reason']
    b['properties']['valid_from']='2026-09-10T00:00:00Z';a['properties']['valid_to']='2026-09-10T00:00:00Z'
    bundle,report=convert(source([route,a,b],edges),COMPILED)
    assert not report['quarantine']


def test_stage_answers_and_future_inspection_not_visible(monkeypatch):
    def guarded(self,*a,**kw):
        assert self.name not in {'hidden_truth.json','event_reveals.json','catalog.json'}
        return original(self,*a,**kw)
    original=Path.read_text;monkeypatch.setattr(Path,'read_text',guarded)
    late=example('Observation','LATE');late['stage']='EVIDENCE_REVEALED'
    ins=example('Inspection','FUTURE');ins['properties']['completed_at']='2027-01-01T00:00:00Z'
    bundle,report=convert(source([late,ins]),COMPILED)
    assert len(report['quarantine'])==2
    for key in ['hidden_ground_truth','underlying_cause','revealed_observation','expected_safe_next_actions']:
        raw=source([]);raw[key]='DO_NOT_IMPORT'
        with pytest.raises(SourceError):convert(raw,COMPILED)
    assert 'DO_NOT_IMPORT' not in json.dumps(bundle)


def test_deterministic_bundle_hash_and_tamper_detection():
    raw=source([example('Location')]);one,report=convert(raw,COMPILED);two,_=convert(raw,COMPILED)
    assert one==two
    next(n for n in one['nodes'] if n['label']=='Location')['properties']['name']='ALTERED'
    with pytest.raises(SourceError):validate_bundle(one)


def test_corrected_generator_is_reproducible_and_original_immutable(tmp_path):
    from hashlib import sha256
    original=(ROOT/'contracts/seed_graph_expanded.json').read_bytes()
    a=tmp_path/'a.json';b=tmp_path/'b.json'
    for p in (a,b):subprocess.run([str(ROOT/'backend/.venv/bin/python'),str(ROOT/'scripts/generate_demo_seed.py'),'--output',str(p)],check=True,capture_output=True)
    assert a.read_bytes()==b.read_bytes() and original==(ROOT/'contracts/seed_graph_expanded.json').read_bytes()
    s=json.loads(a.read_text());assert len(s['nodes'])==838
    obs=[n['properties'] for n in s['nodes'] if n['label']=='Observation']
    assert len(obs)==55 and all('value' in n and 'value_number' not in n for n in obs)
    assert not any(n['properties']['status']=='MISSED' and 'actual_at' in n['properties'] for n in s['nodes'] if n['label']=='PickupExecution')


def test_coordinate_wire_precision_is_explicit_and_measurements_never_rounded():
    n=example('Location');n['properties']['longitude']=82.96839999999999
    bundle,report=convert(source([n]),COMPILED)
    assert next(x for x in bundle['nodes'] if x['label']=='Location')['properties']['longitude']==82.9684
    assert any(x['field']=='longitude' and x['rule']=='VERIFIED_COORDINATE_WIRE_PRECISION' for x in report['changes'])
    n=example('Observation');n['properties']['value']=1.2345678901234567
    _,report=convert(source([n]),COMPILED)
    assert any('UNSUPPORTED_NUMERIC_WIRE_PRECISION:value' in x['reason'] for x in report['quarantine'])


def test_source_manifests_record_exact_deltas_without_changing_originals():
    from app.ingestion.audit import input_manifest,generator_changes
    s=json.loads((ROOT/'data/generated/source_city_v2.json').read_text())
    changes=generator_changes(s)
    assert changes['change_counts']=={'route_id':109,'actual_at':8,'reported_at':254,'value':55,'value_number':55,'target_id':109}
    b=json.loads((ROOT/'data/ingestion/city-v3.json').read_text())
    m=input_manifest('data/generated/source_city_v2.json',b)
    assert m['canonical_source_hash']==b['source_hash']
    assert len(m['document_sha256'])==18
    assert m['file_sha256']['contracts/schema_registry.json']==R.sha256


def test_future_report_is_quarantined_instead_of_initial_visibility():
    n=example('Complaint');n['properties']['reported_at']='2027-01-01T00:00:00Z'
    _,report=convert(source([n]),COMPILED)
    assert any(x['reason']=='FUTURE_STAGE_DATE' for x in report['quarantine'])


@pytest.mark.parametrize('invalid',[None,[],{}])
def test_malformed_source_root_is_explicit(invalid):
    with pytest.raises(SourceError):convert(invalid,COMPILED)


@pytest.mark.parametrize('invalid',[None,[],{}])
def test_malformed_bundle_root_is_explicit(invalid):
    with pytest.raises(SourceError):validate_bundle(invalid)


def test_compiled_record_unknown_envelope_cannot_be_ignored():
    bundle,_=convert(source([example('Location')]),COMPILED)
    bundle['nodes'][0]['unknown']='should fail even with valid property hashes'
    with pytest.raises(SourceError,match='envelope'):validate_bundle(bundle)
