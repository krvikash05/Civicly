# B04 dataset quality and scenario readiness

This is a static data inventory, not proof of working scenario behavior. All R01–R18 remain required. See machine-readable source-audit.json, conversion-report.json, generator-revision-changes.json and scenario-readiness.json for complete IDs and field-level evidence.

| Scenario | Incidents | Complaints | Bound assets / actual incident assets | Topology references | Historical inspections | Binding assets / clusters agree |
|---|---|---|---|---|---|---|
| S01 | INC-FLOOD-02 | 4 | INLET-I01, DRAIN-D12, DRAIN-D18 / DRAIN-D12 | 3 | None | False / True |
| S02 | INC-1000 | 3 | DRAIN-D12, DRAIN-D18 / DRAIN-D12 | 1 | None | False / False |
| S03 | INC-1001 | 3 | ROAD-R08, PIPE-P02 / ROAD-100 | 1 | INS-ROAD-PAST | False / False |
| S04 | INC-1004 | 3 | PIPE-103, ROAD-106 / ROAD-103 | 1 | None | False / False |
| S05 | INC-WASTE-01, INC-WASTE-02 | 8 | WASTE-W03, ROUTE-C03 / WASTE-W03, WASTE-W03 | 1 | None | False / True |
| S06 | INC-1005 | 3 | WASTE-102 / WASTE-104 | 1 | None | False / False |
| S07 | INC-FLOOD-02, INC-ROAD-01, INC-WASTE-01 | 12 | WASTE-W03, INLET-I01, DRAIN-D12, DRAIN-D18, ROAD-R08 / DRAIN-D12, ROAD-R08, WASTE-W03 | 4 | INS-ROAD-PAST | False / True |
| S08 | INC-1003, INC-1008 | 6 | DRAIN-100, WASTE-105 / DRAIN-101, WASTE-107 | 2 | None | False / False |
| S09 | INC-1006 | 3 | DRAIN-108 / DRAIN-104 | 1 | None | False / False |
| S10 | INC-1009 | 3 | DRAIN-D18 / DRAIN-107 | 0 | None | False / False |
| S11 | INC-1007 | 3 | ROAD-107 / ROAD-106 | 0 | None | False / False |
| S12 | INC-1012 | 3 | DRAIN-112 / DRAIN-110 | 1 | None | False / False |

All12 have opaque delayed-release stage/hash/references in release-manifest.json; no reveal payload or expected answer is imported. All lack historical WorkOrder/AgentDecision chains and complete case-specific dated physical proof. There are55 unlinked measurement records; case association needs evidence, not ID guessing. Municipal Markdown documents18/18 exist and hash-match; source ownership IDs, effective-version integration and PDF coverage are deferred to B11/B19. No GeoJSON supplied.

S07 lacks the recorded waste/drain/road SERVES chain. Physical associations lacking observed evidence remain CANDIDATE; geographic proximity is never substituted for a connection. Purpose-built integration fixtures prove path preservation only.

Later boundary: B05 algorithms; B08 issue/recurrence matching; B09 evidence/hypothesis semantics; B11 cited document ownership/version retrieval; B14 simulator outcomes; B19 authoritative scenario source authoring, missing histories, release permissions and runtime evaluator isolation; B20–B23 executed scenario proof. No behavior is claimed complete by this inventory.

Legacy expanded conversion quarantines342 records (109 pickup nodes,218 endpoint-dependent pickup links,15 chronologically invalid REPORTS). The corrected generator explicitly authors a new synthetic revision; it is not a recovery of the ambiguous legacy history.

Additional warnings:110 pickup scheduled local clocks differ from linked schedule
text; recurring-expression interpretation remains an explicit B08/B19 gap. Source
has5 synthetic OperatorAccounts, retained rather than silently changing the original
fixture to match older4-operator planning prose. Reconcile demo personas in the
later authentication/scenario milestones. License/right-to-use is not explicitly
specified per source; manifests say so rather than inventing a license.
