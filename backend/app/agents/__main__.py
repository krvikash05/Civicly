"""Trusted local operator CLI. No public agent graph selection or write endpoint."""
import argparse,asyncio,json
from app.active import load,active_scope
from app.config import Settings
from app.graph.connection import connect
from app.graph.repository import GraphRepository
from app.graph.schema import utc_now
from app.services.evidence.reader import Reader
from .mcp import brokers
from .runtime import InvestigationAgent
from .checkpoints import saver
from .models import InvestigationState
from .provider import Gemini,ProviderSettings
from .policy import Permit

async def execute(args):
    profile=load(args.profile)
    permit=Permit.explicit_live(approved=args.live,investigation_id=args.investigation,thread_id=args.thread,max_usd=args.max_cost_usd)
    settings=Settings(_env_file='.env');model=Gemini(ProviderSettings(_env_file='.env'),permit=permit)
    with connect(settings) as db,active_scope(profile):
        repo=GraphRepository(db,profile.graph,lease_seconds=30)
        async with brokers(profile,args.profile) as tools:
            agent=InvestigationAgent(profile,repo,tools,model,saver(profile))
            initial=None
            if not args.resume:
                reader=Reader(repo,utc_now());repo.get_node(args.investigation,'Investigation')
                cluster=[e.target for e in reader.edges('INVESTIGATES',source=args.investigation) if repo.get_node(e.target).kind=='ProblemCluster']
                ids=[e.target for e in reader.edges('INVESTIGATES',source=args.investigation) if repo.get_node(e.target).kind=='Incident']
                if not ids:raise ValueError('Investigation has no current incident')
                issues={repo.get_node(id).properties['issue_type'] for id in ids}
                if len(issues)!=1:raise ValueError('One issue per investigation thread')
                assets=sorted({e.target for id in ids for e in reader.edges('AFFECTS',source=id)})
                initial=InvestigationState(graph=profile.graph,investigation_id=args.investigation,thread_id=args.thread,
                    problem_cluster_id=cluster[0],discovered_tool_names=[t['name'] for t in tools.catalog()],incident_ids=ids,asset_ids=assets,issue=issues.pop(),graph_revision=agent.revision(),inventory_hash=tools.inventory_hash,as_of=utc_now())
            result=await agent.run(initial,thread_id=args.thread,resume=args.resume)
            # Public state only, no model private reasoning or credentials.
            print(json.dumps(result,default=str))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--profile',required=True);parser.add_argument('--thread',required=True)
    parser.add_argument('--live',action='store_true',help='Explicitly authorize only this investigation/thread');parser.add_argument('--max-cost-usd',default='.15');parser.add_argument('--investigation');parser.add_argument('--resume',action='store_true');args=parser.parse_args()
    try:asyncio.run(execute(args))
    except Exception as exc:
        print(json.dumps({'status':'RECOVERY_REQUIRED','code':type(exc).__name__,'detail':'Wake failed closed; reconcile private runtime configuration and public checkpoint. No implicit retry.'}));raise SystemExit(1)

if __name__=='__main__':main()
