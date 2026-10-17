"""Eight named GRAPH.RO_QUERY templates; caller-supplied Cypher is never accepted."""

from pydantic import Field

from app.graph.models import EdgeRecord, GraphModel, GraphResult, PathRecord, QueryBudget, QueryRequest
from app.graph.repository import GraphRepository, PreconditionFailed, OutcomeUnknown
from app.graph.schema import timestamp


class ReadLimits(GraphModel):
    max_hops: int = Field(default=6, ge=1, le=6)
    max_results: int = Field(default=100, ge=1, le=100)
    max_nodes: int = Field(default=120, ge=1, le=120)
    max_edges: int = Field(default=200, ge=1, le=200)
    timeout_ms: int = Field(default=1000, ge=1, le=1000)


class GraphQueries:
    def __init__(self, repository: GraphRepository, limits: ReadLimits | None = None):
        self.repository = repository
        self.limits = limits or ReadLimits()

    def _state(self):
        rows = self.repository._read(
            "MATCH (m:CivicSchemaMigration {id:$migration}) WHERE m.state='READY' RETURN coalesce(m.repo_revision,0),coalesce(m.repo_pending,'') LIMIT 1",
            {"migration": "0001"})
        if not rows or rows[0][1]:
            raise OutcomeUnknown("Graph has an unresolved write; recover before evidence retrieval")
        return rows[0][0]

    @staticmethod
    def _time_key(expression):
        # Registry accepts UTC seconds with optional fractions. Pad/truncate to the
        # Python datetime microsecond precision; lexical comparison is then valid.
        return (f"substring(replace({expression},'Z','') + CASE WHEN {expression} CONTAINS '.' "
                "THEN '000000' ELSE '.000000' END,0,26)")

    @classmethod
    def _time_filter(cls):
        key = cls._time_key
        node_times = ["created_at", "updated_at", "observed_at", "recorded_at", "started_at",
                      "opened_at", "assessed_at", "evaluated_at", "completed_at", "requested_at"]
        checks = [f"(n.{field} IS NULL OR {key('n.' + field)}<=$as_of)" for field in node_times]
        checks += [f"(n.valid_from IS NULL OR {key('n.valid_from')}<=$as_of)",
                   f"(n.valid_to IS NULL OR $as_of<{key('n.valid_to')})"]
        return ("size(relationships(p)) <= $hops AND "
                "all(n IN nodes(p) WHERE n.municipality_id=$scope AND " + " AND ".join(checks) + ") AND "
                "all(e IN relationships(p) WHERE e.municipality_id=$scope AND " + key('e.created_at') + "<=$as_of "
                "AND (e.valid_from IS NULL OR " + key('e.valid_from') + "<=$as_of) "
                "AND (e.valid_to IS NULL OR $as_of<" + key('e.valid_to') + "))")

    @staticmethod
    def _verified_filter():
        # Only physical/incident associations need this filter; structural links aren't causal claims.
        return ("all(e IN relationships(p) WHERE NOT type(e) IN $physical OR "
                "($candidates OR e.association_status='VERIFIED'))")

    def _budget(self, request: QueryRequest) -> QueryBudget:
        spec = self.repository.policy["query_hop_budgets"][request.template]
        minimum, maximum = spec["min"], spec["max"]
        if request.template == "hypothesis_evidence":
            root = self.repository.get_node(request.id)
            minimum = spec["investigation_min"] if root.kind == "Investigation" else minimum
            maximum = minimum
        if request.max_hops < minimum:
            raise PreconditionFailed(f"Template requires at least {minimum} total path hops")
        effective = min(request.max_hops, maximum)
        fixed = spec["fixed_edges"]
        return QueryBudget(requested_total_hops=request.max_hops, effective_total_hops=effective,
                           template_min_hops=minimum, template_max_hops=maximum,
                           fixed_connector_hops=fixed,
                           infrastructure_hops=effective - fixed if spec["variable"] == "DRAINS_TO" else None)

    def _branches(self, request: QueryRequest, budget: QueryBudget):
        h = budget.effective_total_hops  # Finite total budget, including connectors.
        kind = request.template
        condition = self._time_filter()
        verified = condition + " AND " + self._verified_filter()
        if kind == "drainage_paths":
            self.repository.get_node(request.id, "InfrastructureAsset")
            pattern = f"(a:InfrastructureAsset {{id:$id}})-[:DRAINS_TO*1..{h}]->(b:InfrastructureAsset)"
            if request.direction == "upstream":
                pattern = f"(a:InfrastructureAsset {{id:$id}})<-[:DRAINS_TO*1..{h}]-(b:InfrastructureAsset)"
            return [("MATCH p=" + pattern + " WHERE " + verified, "{}")]
        if kind == "shared_infrastructure":
            if len(set(request.incident_ids)) < 2:
                raise PreconditionFailed("Shared retrieval needs at least two distinct incidents")
            for id in request.incident_ids:
                self.repository.get_node(id, "Incident")
            prefix = (f"MATCH p=(i:Incident)-[:AFFECTS]->(a:InfrastructureAsset)-[:DRAINS_TO*0..{h - 1}]->(shared:InfrastructureAsset) "
                      "WHERE i.id IN $incidents AND " + verified +
                      " WITH shared,collect(p) AS matched_paths,collect(DISTINCT i.id) AS matched_ids "
                      "WHERE size(matched_ids)>=2 UNWIND matched_paths AS p")
            return [(prefix, "{shared_incident_ids:matched_ids,shared_asset_id:shared.id}")]
        if kind == "incident_history":
            root = self.repository.get_node(request.id)
            if "InfrastructureAsset" in root.labels:
                pattern = "(i:Incident)-[:AFFECTS]->(a:InfrastructureAsset {id:$id})"
            elif root.kind == "Location":
                pattern = "(i:Incident)-[:OCCURRED_AT]->(a:Location {id:$id})"
            else:
                raise PreconditionFailed("Incident history needs a location or asset")
            return [("MATCH p=" + pattern + " WHERE " + verified +
                     " AND ($after IS NULL OR $after<=" + self._time_key("i.started_at") + ")", "{classification:'related_incidents_not_recurrence_verdict'}")]
        if kind == "maintenance_history":
            self.repository.get_node(request.id, "InfrastructureAsset")
            patterns = [
                "(a:InfrastructureAsset {id:$id})<-[:INSPECTS]-(i:Inspection)",
                "(a:InfrastructureAsset {id:$id})<-[:INSPECTS]-(i:Inspection)-[:PRODUCED]->(e:Evidence)",
                "(a:InfrastructureAsset {id:$id})<-[:TARGETS]-(t:ActionTask)<-[:IMPLEMENTS]-(o:WorkOrder)",
                "(a:InfrastructureAsset {id:$id})<-[:TARGETS]-(t:ActionTask)<-[:IMPLEMENTS]-(o:WorkOrder)-[:RESULTED_IN]->(out:InterventionOutcome)",
            ]
            return [("MATCH p=" + pattern + " WHERE " + condition, "{}") for length, pattern in zip((1, 2, 2, 3), patterns, strict=True) if length <= h]
        if kind == "cross_category_paths":
            self.repository.get_node(request.id, "WasteCollectionPoint")
            pattern = (f"(w:WasteCollectionPoint {{id:$id}})-[:LOCATED_AT]->(l:Location)<-[:SERVES]-(d:InfrastructureAsset)"
                       f"-[:DRAINS_TO*1..{h - 4}]->(down:InfrastructureAsset)-[:SERVES]->(rl:Location)<-[:LOCATED_AT]-(road:RoadSegment)")
            return [("MATCH p=" + pattern + " WHERE " + verified, "{classification:'CANDIDATE_CONNECTION_NOT_CAUSATION'}")]
        if kind == "hypothesis_evidence":
            root = self.repository.get_node(request.id)
            if root.kind == "Investigation":
                pattern = "(i:Investigation {id:$id})-[:PROPOSES]->(h:Hypothesis)"
            elif root.kind == "Hypothesis":
                pattern = "(h:Hypothesis {id:$id})"
            else:
                raise PreconditionFailed("Evidence paths need investigation or hypothesis")
            return [("MATCH p=" + pattern + "-[:HAS_ASSESSMENT]->(a:HypothesisAssessment)-[:SUPPORTED_BY|CONTRADICTED_BY]->(e:Evidence) WHERE " + condition, "{}")]
        if kind == "ownership_dependencies":
            self.repository.get_node(request.id)
            patterns = ["(a:InfrastructureAsset {id:$id})-[:MAINTAINED_BY]->(d:Department)",
                        "(a:WasteCollectionPoint {id:$id})-[:COLLECTED_BY]->(route:CollectionRoute)",
                        "(a:WasteCollectionPoint {id:$id})-[:COLLECTED_BY]->(route:CollectionRoute)-[:HAS_SCHEDULE]->(schedule:ServiceSchedule)",
                        "(a:ActionTask {id:$id})-[:ASSIGNED_TO]->(d:Department)"]
            return [("MATCH p=" + pattern + " WHERE " + condition, "{classification:'assignment_not_causal_finding'}") for length, pattern in zip((1, 1, 2, 1), patterns, strict=True) if length <= h]
        if kind == "task_dependencies":
            self.repository.get_node(request.id, "ActionTask")
            return [(f"MATCH p=(t:ActionTask {{id:$id}})-[:DEPENDS_ON*1..{h}]->(dependency:ActionTask) WHERE " + condition, "{}")]
        raise PreconditionFailed("Unknown preapproved query template")

    def _decode(self, rows, request):
        repo = self.repository
        nodes, edges, paths = {}, {}, []
        truncated = len(rows) > request.limit
        for raw_nodes, raw_edges, revision, context in rows[:request.limit]:
            path_nodes = [repo.decode_node(node.labels, node.properties) for node in raw_nodes]
            by_internal_id = {node.id: record for node, record in zip(raw_nodes, path_nodes, strict=True)}
            path_edges = []
            future_evidence = False
            for edge in raw_edges:
                source, target = by_internal_id[edge.src_node], by_internal_id[edge.dest_node]
                repo.registry.validate_edge(edge.relation, source.kind, source.properties, target.kind, target.properties, dict(edge.properties))
                evidence = repo._check_evidence(dict(edge.properties))
                if evidence is not None:
                    future_evidence |= any(timestamp(evidence.properties[field]) > timestamp(request.as_of)
                                           for field in ("created_at", "updated_at", "observed_at", "recorded_at")
                                           if field in evidence.properties)
                path_edges.append(EdgeRecord(id=edge.properties["id"], kind=edge.relation, source=source.id,
                                              target=target.id, properties=dict(edge.properties)))
            if future_evidence:
                continue
            if len(set(nodes) | {n.id for n in path_nodes}) > self.limits.max_nodes or len(set(edges) | {e.id for e in path_edges}) > self.limits.max_edges:
                truncated = True
                break  # Never return half a path.
            for n in path_nodes:
                if n.id in nodes and nodes[n.id].content_hash != n.content_hash:
                    raise PreconditionFailed("Inconsistent node snapshots in result")
                nodes[n.id] = n
            for e in path_edges:
                if e.id in edges and edges[e.id].content_hash != e.content_hash:
                    raise PreconditionFailed("Ambiguous relationship identity in result")
                edges[e.id] = e
            context = dict(context)
            if request.template == "hypothesis_evidence" and path_edges:
                context["evidence_relation"] = path_edges[-1].kind
            paths.append(PathRecord(node_ids=tuple(n.id for n in path_nodes), edge_ids=tuple(e.id for e in path_edges),
                                    directions=tuple("OUTGOING" if e.source == path_nodes[i].id else "INCOMING" for i, e in enumerate(path_edges)),
                                    evidence_ids=tuple(sorted({str(e.properties["source_evidence_id"]) for e in path_edges if e.properties.get("source_evidence_id")} | {n.id for n in path_nodes if n.kind == "Evidence"})),
                                    context=context))
        return nodes, edges, paths, truncated

    def run(self, request: QueryRequest) -> GraphResult:
        if not isinstance(request, QueryRequest):
            raise TypeError("Use typed QueryRequest; raw Cypher is not an input")
        if request.max_hops > self.limits.max_hops or request.limit > self.limits.max_results or request.timeout_ms > self.limits.timeout_ms:
            raise PreconditionFailed("Requested query exceeds configured budget")
        if request.after is not None and timestamp(request.after) > timestamp(request.as_of):
            raise PreconditionFailed("History window is reversed")
        if request.template != "shared_infrastructure" and not request.id.strip():
            raise PreconditionFailed("Template requires an application ID")
        budget = self._budget(request)
        params = {"migration": "0001", "scope": self.repository.registry.scope, "id": request.id,
                  "incidents": list(request.incident_ids), "as_of": timestamp(request.as_of).strftime("%Y-%m-%dT%H:%M:%S.%f"),
                  "after": timestamp(request.after).strftime("%Y-%m-%dT%H:%M:%S.%f") if request.after else None,
                  "hops": budget.effective_total_hops, "limit": request.limit + 1, "candidates": request.include_candidates,
                  "physical": self.repository.policy["verified_associations"]}
        branches = self._branches(request, budget)
        query = " UNION ALL ".join(
            body +
            f" RETURN nodes(p) AS ns,relationships(p) AS es,$snapshot AS revision,{context} AS context LIMIT $limit"
            for body, context in branches)
        for _ in range(2):
            # Before/after monotonic revision checks avoid projecting a disconnected
            # metadata node through a path plan (incorrect on installed 6.0.2).
            before = self._state()
            rows = self.repository.graph.ro_query(query, params={**params, "snapshot": before}, timeout=request.timeout_ms).result_set
            nodes, edges, paths, truncated = self._decode(rows, request)
            after = self._state()
            if before != after or any(row[2] != before for row in rows):
                continue
            variable = self.repository.policy["query_hop_budgets"][request.template]["variable"]
            search_limited = variable is not None or budget.effective_total_hops < budget.template_max_hops
            reservations = ["Graph connections are evidence context, not verified physical causation.",
                            "Historical node versions are not reconstructed; future-updated records are excluded."]
            if search_limited:
                reservations.append(f"Search limited to {budget.effective_total_hops} total path edges; no result does not prove global absence.")
            if any("valid_from" not in e.properties for e in edges.values()):
                reservations.append("Some relationship validity start dates are unknown.")
            if truncated:
                reservations.append("Result budget reached; omitted paths must not be treated as absent.")
            return GraphResult(template=request.template, as_of=request.as_of, graph_revision=before,
                               nodes=tuple(nodes.values()), edges=tuple(edges.values()), paths=tuple(paths),
                               truncated=truncated, search_limited=search_limited, search_budget=budget,
                               reservations=tuple(reservations))
        raise PreconditionFailed("Graph changed during bounded retrieval; retry later")
