"""Operator read explanation over accepted B03 queries and authorized B17 DTO."""
from app.api.view_models import GraphSubgraphDTO
from app.graph.models import QueryRequest,digest
from app.graph.queries import GraphQueries
from app.graph.repository import PreconditionFailed

def explain(repo,investigation,projection,cutoff):
 view=GraphSubgraphDTO.model_validate(projection)
 result=GraphQueries(repo).run(QueryRequest(template='hypothesis_evidence',id=investigation,as_of=cutoff,max_hops=4,limit=40))
 if result.graph_revision!=view.graph_revision:raise PreconditionFailed('EXPLANATION_CHANGED_REFETCH')
 ids={n.id for n in view.nodes};edges={e.id for e in view.edges};evidence=ids|{id for e in view.edges for id in e.source_evidence_ids}
 paths=[]
 for path in result.paths:
  if set(path.node_ids)<=ids and set(path.edge_ids)<=edges and set(path.evidence_ids)<=evidence:
   value=path.model_dump(mode='json');paths.append({'id':'EXPLAIN-'+digest(value)[:32],**value})
 return {**projection,'analysis_paths':paths,'analysis_path_kind':'ACTUAL_HYPOTHESIS_EVIDENCE_CONTEXT_NOT_MODEL_SELECTED','analysis_truncated':result.truncated,'analysis_search_limited':result.search_limited,'analysis_reservations':list(result.reservations)}
