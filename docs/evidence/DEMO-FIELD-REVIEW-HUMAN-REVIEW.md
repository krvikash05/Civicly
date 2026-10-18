# Exact pending human reviews

These two requests are PENDING. This artifact is not approval or execution authority. No work order was created by this task. Review the scope, evidence, procedure limitations and conditions before deciding in the authenticated OP-APPROVER role. Analyst and admin have no approval bypass.

## WATERLOGGING

Plan `PLAN-B12-da6d426cc7a42982a3dac6c8a76af2a6`, version **1**, immutable hash `1b04b300f41379529bd0e7b6667bf28c1fbaaec5f1bbe38f4cfb5803a3a74286`.

Approval `APPROVAL-B13-8be3619083045ba6f1d947cbf2a69ca3`, current status **PENDING**.

- `DRAIN_BLOCKAGE_CLEARANCE` on `DRAIN-101`; department `DEPT-DRAIN`, assignee `OP-DRAIN-LEAD`.
- Procedure `D019` version 1; synthetic PROPOSED guidance.
- Remediation conditions: {"mode": "SUPPORTED_NOW", "conditions": [{"kind": "CAUSAL_INSPECTION", "status": "MET", "evidence_ids": ["EV-REPORT-B09-e391ab25460225848fa1bc7ee58af6f9"], "depends_on_task_id": null}, {"kind": "SAFETY_REVIEW", "status": "MET", "evidence_ids": ["EV-REPORT-B09-e391ab25460225848fa1bc7ee58af6f9"], "depends_on_task_id": null}]}.

Monitoring and unresolved limitations:

```json
{
  "monitoring": {
    "issue": "WATERLOGGING",
    "required_evidence": [
      "COMPARABLE_FOLLOWUP_RAINFALL",
      "FOLLOWUP_WATERLOGGING"
    ],
    "observation_opportunity": "Monitor DRAIN-101 and surrounding surface catchment across next significant rainfall event.",
    "verification_criteria": "Absence of surface waterlogging under comparable rainfall intensity following clearance clearance.",
    "missing_opportunity": "UNRESOLVED",
    "completion_implies_resolution": false
  },
  "uncertainties": [
    "Residual hydraulic capacity deficit may persist under peak storm conditions.",
    "Long-term maintenance frequency unknown from current records."
  ],
  "risks": [
    "Downstream sediment accumulation or localized flooding during clearance operations."
  ]
}
```

The approval decision must bind the same plan/version/hash/assignments, current approval expected_hash, and an explicit human reason. Re-read `/approvals/{id}` immediately before a decision; stale hashes must fail. Approval does not satisfy unmet task gates, create orders, perform work or verify resolution.

## ROAD_DAMAGE

Plan `PLAN-B12-3a26fd93b1eb567bf101905dc4c43b76`, version **1**, immutable hash `a39f811a8913ba4c5870a6acff9a05b918027db1768c64146e32bc4f90a2c834`.

Approval `APPROVAL-B13-421f1dfc4187d58155e9d190f5085551`, current status **PENDING**.

- `SUBGRADE_REPAIR` on `ROAD-DEMO-SUBGRADE-02`; department `DEPT-ROAD`, assignee `OP-ROAD-LEAD`.
- Procedure `D020` version 1; synthetic PROPOSED guidance.
- Remediation conditions: {"mode": "SUPPORTED_NOW", "conditions": [{"kind": "CAUSAL_INSPECTION", "status": "MET", "evidence_ids": ["EV-REPORT-B09-aa69698f124f46d2900d8a93e537005b"], "depends_on_task_id": null}, {"kind": "SAFETY_REVIEW", "status": "MET", "evidence_ids": ["EV-REPORT-B09-aa69698f124f46d2900d8a93e537005b"], "depends_on_task_id": null}]}.

Monitoring and unresolved limitations:

```json
{
  "monitoring": {
    "issue": "ROAD_DAMAGE",
    "required_evidence": [
      "FOLLOWUP_PAVEMENT",
      "WEAR_EXPOSURE"
    ],
    "observation_opportunity": "Follow-up pavement visual inspection and structural profile assessment following post-repair wear exposure.",
    "verification_criteria": "No recurring depression, cracking, or subgrade movement following 30 days of standard traffic exposure.",
    "missing_opportunity": "UNRESOLVED",
    "completion_implies_resolution": false
  },
  "uncertainties": [
    "Long-term pavement durability remains subject to meaningful wear exposure and post-repair traffic load."
  ],
  "risks": [
    "Subsurface excavation hazards and traffic disruption during repair operations."
  ]
}
```

The approval decision must bind the same plan/version/hash/assignments, current approval expected_hash, and an explicit human reason. Re-read `/approvals/{id}` immediately before a decision; stale hashes must fail. Approval does not satisfy unmet task gates, create orders, perform work or verify resolution.

