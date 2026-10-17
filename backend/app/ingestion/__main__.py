"""Offline audit/prepare or guarded repository import; no arbitrary Cypher input."""
import argparse
import json
from pathlib import Path
from app.graph.connection import connect
from app.config import Settings
from app.graph.migration import MigrationRunner
from app.graph.repository import GraphRepository
from app.ingestion.conversion import ROOT,convert,SourceError


def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(value,indent=2)+'\n');temp.replace(path)


def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('audit');a.add_argument('--output',default='data/ingestion/source-audit.json')
    a=sub.add_parser('prepare');a.add_argument('--source',default='data/generated/source_city_v2.json');a.add_argument('--conversion-at');a.add_argument('--output-dir',default='data/ingestion');a.add_argument('--documents',action='store_true')
    a=sub.add_parser('import');a.add_argument('--bundle',default='data/ingestion/city-v3.json');a.add_argument('--graph',required=True);a.add_argument('--report',required=True)
    args=p.parse_args()
    if args.command=='audit':
        from app.ingestion.audit import audit_repository
        write(args.output,audit_repository());return
    if args.command=='prepare':
        from app.ingestion.audit import audit_dataset,scenario_reports,input_manifest,generator_changes
        source=json.loads(Path(args.source).read_text());out=Path(args.output_dir)
        write(out/'selected-source-audit.json',audit_dataset(source))
        from app.graph.schema import utc_now
        bundle,report=convert(source,args.conversion_at or utc_now(),documents=json.loads((ROOT/'data/documents/manifest.json').read_text()) if args.documents else None)
        write(out/'input-manifest.json',input_manifest(args.source,bundle))
        if source.get('generator_version')=='2.1':write(out/'generator-revision-changes.json',generator_changes(source))
        write(out/'city-v3.json',bundle);write(out/'conversion-report.json',report)
        readiness,releases=scenario_reports(bundle);write(out/'scenario-readiness.json',readiness);write(out/'release-manifest.json',releases)
        print(json.dumps({'manifest':{k:v for k,v in bundle['manifest'].items() if k!='record_hashes'},'quarantined':len(report['quarantine'])}));return
    from app.ingestion.importer import Importer,ImportFailure
    # Target guard is checked before migration/client writes.
    from app.graph.targets import is_disposable_graph
    if not is_disposable_graph(args.graph) or not args.graph.startswith('civicly_b04_test_'):raise SourceError('B04 target refused')
    with connect(Settings(_env_file='.env')) as client:
        MigrationRunner(client,args.graph).apply();repo=GraphRepository(client,args.graph)
        try:report=Importer(repo).run(json.loads(Path(args.bundle).read_text()))
        except ImportFailure as error:write(args.report,error.report);raise
        write(args.report,report)


if __name__=='__main__':main()
