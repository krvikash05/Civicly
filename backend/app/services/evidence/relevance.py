"""B09-R occurrence attribution; no new ontology, queries or write privileges."""
from app.graph.repository import PreconditionFailed
from app.graph.schema import timestamp


def inspection_incidents(reader, report):
    edges = reader.edges('INSPECTS', source=report.inspection_id)
    sources = {e.properties.get('source_evidence_id') for e in edges}
    if len(sources) != 1 or None in sources:
        raise PreconditionFailed('Unique inspection request source required for attribution')
    journal = reader.journal(next(iter(sources)))
    command = journal.command
    if command['operation'] != 'request_inspection' or journal.receipt.entity_id != report.inspection_id:
        raise PreconditionFailed('Inspection occurrence request binding mismatch')
    inv = command['investigation_id']
    reader.node(inv, 'Investigation')
    memberships = reader.edges('INVESTIGATES', source=inv)
    origins = {e.properties.get('source_evidence_id') for e in memberships}
    if len(origins) != 1 or None in origins:
        raise PreconditionFailed('Unique investigation occurrence source required')
    opened = reader.journal(next(iter(origins)))
    original = opened.command
    if (original['operation'] != 'open' or opened.receipt.entity_id != inv
            or {e.target for e in memberships} != {original['cluster_id'], *original['incident_ids']}):
        raise PreconditionFailed('Actual investigation occurrence bindings disagree with opening journal')
    # Use immutable identity bindings, not a cluster's later mutable pattern/status.
    # The hypothesis incidents themselves are still read with full as_of visibility.
    return set(original['incident_ids'])


def inside(incident, observed_at):
    props = incident.properties
    at = timestamp(observed_at)
    if props['status'] == 'INVALIDATED':
        return False
    if at < timestamp(props['started_at']):
        return False
    if 'ended_at' in props:
        return at < timestamp(props['ended_at'])
    # A terminal state without its end timestamp cannot establish a temporal interval.
    return props['status'] != 'ENDED'


def attribute(reader, report, observation, incidents, definition, affected):
    """Return incident IDs, reason, derivative basis IDs. A matching asset is insufficient."""
    if observation.asset_id not in definition.asset_ids or observation.result != 'OBSERVED':
        return [], 'Unrelated asset or non-observed result; context only', []
    bound = inspection_incidents(reader, report)
    attribution = report.attribution
    if attribution:
        named = set(attribution.incident_ids)
        if not named <= bound:
            raise PreconditionFailed('Explicit attribution outside inspection investigation')
    else:
        named = bound
    candidates = [i for i in incidents if i.id in named and (observation.asset_id in affected[i.id]
        or definition.topology and observation.asset_id == definition.topology.source_id
        and definition.topology.target_id in affected[i.id])]
    if not candidates:
        return [], 'Inspection request belongs to another incident occurrence', []
    if attribution and attribution.mode == 'RETROSPECTIVE':
        if not report.review:
            return [], 'Retrospective claim requires independent review and dated source basis', []
        accepted = set()
        for evidence_id in attribution.basis_evidence_ids:
            basis = reader.evidence(evidence_id).report
            if (not basis or not basis.review or basis.attribution and basis.attribution.mode == 'RETROSPECTIVE'
                    or timestamp(basis.recorded_at) >= timestamp(report.recorded_at)):
                raise PreconditionFailed('Retrospective basis must be an earlier reviewed direct inspection')
            basis_bound = inspection_incidents(reader, basis)
            if basis.attribution:
                basis_bound &= set(basis.attribution.incident_ids)
            for incident in candidates:
                if incident.id in basis_bound and any(
                    ob.asset_id == observation.asset_id and ob.code == observation.code
                    and ob.result == 'OBSERVED' and inside(incident, ob.observed_at)
                    for ob in basis.observations):
                    accepted.add(incident.id)
        return sorted(accepted), ('Explicit reviewed retrospective attribution with prior occurrence-specific evidence'
                                 if accepted else 'Retrospective source basis does not establish this observation for this occurrence'), list(attribution.basis_evidence_ids)
    relevant = [i.id for i in candidates if inside(i, observation.observed_at)]
    if not attribution and len(relevant) > 1:
        return [], 'Ambiguous overlapping occurrences require explicit named attribution', []
    return sorted(relevant), ('Inspection request and observation fall within named occurrence interval'
                             if relevant else 'Observation outside incident occurrence interval or end unknown'), []


def independent(a, b):
    """Source independence includes derivative lineage, not just record count."""
    report_a, lineage_a = a
    report_b, lineage_b = b
    return (report_a.inspection_id != report_b.inspection_id
            and report_a.inspector_id != report_b.inspector_id
            and report_a.source_id != report_b.source_id
            and (report_a.source_id, report_a.record_id) != (report_b.source_id, report_b.record_id)
            and not lineage_a & lineage_b)
