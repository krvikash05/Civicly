"""Explicit evidence meaning, authority and occurrence coverage for rule v2."""
from app.graph.repository import PreconditionFailed
from .models import EvidenceUse, EvidenceClassification
from .relevance import attribute, independent

SUMMARY = {'REVIEWED_SUPPORT': 'reviewed_support_ids', 'UNREVIEWED_SUPPORT': 'unreviewed_support_ids',
           'REVIEWED_CONTRADICTION': 'reviewed_contradiction_ids', 'UNREVIEWED_CONTRADICTION': 'unreviewed_contradiction_ids',
           'CONTEXT': 'contextual_evidence_ids', 'EXCLUDED': 'excluded_evidence_ids'}


def summarize(uses):
    return EvidenceClassification(uses=uses, **{field: sorted({u.evidence_id for u in uses if u.category == category})
                                               for category, field in SUMMARY.items()})


def add_topology_context(classification, evidence_id):
    return summarize([*classification.uses, EvidenceUse(evidence_id=evidence_id, category='CONTEXT',
        reason='Verified path provenance is connectivity context, not an inspected causal observation')])


def classify_evidence(repo, reader, request, definition, incidents, rule, history):
    # Actual graph bindings, not merely the supplied or journaled definition, are normative.
    if {e.target for e in reader.edges('EXPLAINS', source=request.hypothesis_id)} != set(definition.incident_ids):
        raise PreconditionFailed('Hypothesis occurrence bindings disagree with original proposal')
    if {e.target for e in reader.edges('CONCERNS', source=request.hypothesis_id)} != set(definition.asset_ids):
        raise PreconditionFailed('Hypothesis asset bindings disagree with original proposal')
    affected = {i.id: {e.target for e in reader.edges('AFFECTS', source=i.id)} for i in incidents}
    refs, uses, gaps = {}, [], []
    known = set(request.evidence_ids)
    inspection_report_ids = set()
    prior_path_context = {evidence_id for previous in history for path in previous.paths for evidence_id in path.evidence_ids}
    for previous in history:
        known.update(previous.supporting_evidence_ids)
        known.update(previous.contradicting_evidence_ids)
        if previous.classification:
            known.update(u.evidence_id for u in previous.classification.uses)
    for asset_id in definition.asset_ids:
        for relation in reader.edges('INSPECTS', target=asset_id):
            inspection = repo.get_node(relation.source, 'Inspection')
            if not reader.visible(inspection.properties):
                gaps.append('Inspection current version unavailable at cutoff: ' + inspection.id)
                continue
            produced = {e.target for e in reader.edges('PRODUCED', source=inspection.id)}
            known.update(produced)
            inspection_report_ids.update(produced)
    if len(known) > 20:
        raise PreconditionFailed('B09 evidence union exceeds20; incomplete evidence cannot verify')
    coverage = {i.id: {'codes': set(), 'sources': {}} for i in incidents}
    for evidence_id in sorted(known):
        ev = repo.get_node(evidence_id, 'Evidence')
        if not reader.visible(ev.properties):
            uses.append(EvidenceUse(evidence_id=evidence_id, category='EXCLUDED', reason='Evidence outside cutoff/validity'))
            gaps.append('Evidence outside cutoff/validity: ' + evidence_id)
            continue
        ref = reader.evidence(evidence_id, context_only=evidence_id in prior_path_context
            and evidence_id not in inspection_report_ids and evidence_id not in request.evidence_ids)
        refs[evidence_id] = ref
        report = ref.report
        if not report:
            uses.append(EvidenceUse(evidence_id=evidence_id, category='CONTEXT', reason='Non-inspection source is context only'))
            gaps.append('Non-inspection evidence is context only: ' + evidence_id)
            continue
        if report.attribution:
            for basis_id in report.attribution.basis_evidence_ids:
                refs[basis_id] = reader.evidence(basis_id)
        for index, ob in enumerate(report.observations):
            incident_ids, reason, basis_ids = attribute(reader, report, ob, incidents, definition, affected)
            if not incident_ids:
                category = 'CONTEXT' if ob.asset_id not in definition.asset_ids or ob.result != 'OBSERVED' else 'EXCLUDED'
                gaps.append(reason + ': ' + evidence_id)
            elif rule and not set(reader.node(ob.asset_id).labels) & set(rule['asset_labels']):
                category, reason = 'CONTEXT', 'Observation lacks the domain criterion asset subtype'
            elif ob.code in definition.confirming_codes:
                category = 'REVIEWED_SUPPORT' if report.review else 'UNREVIEWED_SUPPORT'
                if report.review:
                    for incident_id in incident_ids:
                        coverage[incident_id]['codes'].add(ob.code)
                        coverage[incident_id]['sources'][evidence_id] = (report, {evidence_id, *basis_ids})
            elif rule and ob.code in rule['falsifying'] and ob.code in definition.falsifying_codes:
                category = 'REVIEWED_CONTRADICTION' if report.review else 'UNREVIEWED_CONTRADICTION'
            else:
                category, reason = 'CONTEXT', 'No approved discriminating observation for this mechanism'
                gaps.append(reason + ': ' + evidence_id)
            if category.startswith('UNREVIEWED'):
                gaps.append('Unreviewed finding is a qualified claim, not definitive support/rejection: ' + evidence_id)
            uses.append(EvidenceUse(evidence_id=evidence_id, observation_index=index, category=category,
                incident_ids=incident_ids, reason=reason, basis_evidence_ids=basis_ids))
    if len(refs) > 20:
        raise PreconditionFailed('B09 evidence and retrospective basis union exceeds20')
    # A source included only as retrospective basis remains visible and cannot acquire a causal edge by existence.
    classified_ids = {u.evidence_id for u in uses}
    for evidence_id in sorted(set(refs) - classified_ids):
        uses.append(EvidenceUse(evidence_id=evidence_id, category='CONTEXT', reason='Retrospective source basis; not independently classified as a causal observation'))
    complete = bool(rule)
    for incident_id, item in coverage.items():
        missing = set(definition.confirming_codes) - item['codes']
        sources = list(item['sources'].values())
        corroborated = any(independent(a, b) for index, a in enumerate(sources) for b in sources[:index])
        if missing:
            gaps.append('Missing reviewed confirming observations for ' + incident_id + ': ' + ','.join(sorted(missing)))
        if not corroborated:
            gaps.append('Two independent reviewed inspections/inspectors/source records required for ' + incident_id)
        complete = complete and not missing and corroborated
    if rule is None:
        gaps.append('No approved deterministic domain criterion for this cause')
    return list(refs.values()), summarize(uses), gaps, bool(complete)
