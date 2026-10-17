# B05 real execution/performance and scenario inventory

Measured on accepted local Python3.12.1 / official falkordb1.8.0 / Redis client8.1.0 / FalkorDB6.0.2(module60002), same pinned Docker/AOF runtime.26 workloads ×10 calls =260 actual read-only analyses. No mocked success, no live MCP/LLM/GraphRAG claim.

| Workload | p50 ms | p95 ms | Queries/run | Truncated in any sample |
|---|---|---|---|---|
| controlled/reachability | 4.879 | 8.891 | [5, 5] | False |
| controlled/shared_downstream | 8.106 | 10.405 | [7, 7] | False |
| controlled/impacted_assets | 3.784 | 5.440 | [5, 5] | False |
| controlled/criticality | 9.407 | 11.801 | [7, 7] | False |
| controlled/components | 6.962 | 7.746 | [7, 7] | False |
| controlled/dependencies | 4.689 | 6.438 | [7, 7] | False |
| controlled/task_dag | 3.327 | 3.746 | [5, 5] | False |
| controlled/cases | 23.084 | 37.283 | [18, 18] | False |
| city/verified_only/reachability | 2.976 | 3.277 | [4, 4] | False |
| city/verified_only/shared_downstream | 7.306 | 7.956 | [8, 8] | False |
| city/verified_only/impacted_assets | 2.743 | 3.442 | [4, 4] | False |
| city/verified_only/criticality | 6.151 | 6.812 | [8, 8] | False |
| city/verified_only/components | 2.757 | 2.846 | [4, 4] | False |
| city/verified_only/dependencies | 2.815 | 3.076 | [4, 4] | False |
| city/verified_only/cases/WATERLOGGING | 27.303 | 28.337 | [6, 6] | True |
| city/verified_only/cases/ROAD_DAMAGE | 27.628 | 31.536 | [6, 6] | True |
| city/verified_only/cases/WASTE_ACCUMULATION | 24.737 | 30.286 | [6, 6] | True |
| city/exploratory/reachability | 3.282 | 3.590 | [5, 5] | False |
| city/exploratory/shared_downstream | 6.842 | 7.173 | [10, 10] | False |
| city/exploratory/impacted_assets | 2.942 | 3.049 | [5, 5] | False |
| city/exploratory/criticality | 5.388 | 5.433 | [7, 7] | False |
| city/exploratory/components | 3.145 | 3.241 | [5, 5] | False |
| city/exploratory/dependencies | 2.891 | 3.040 | [5, 5] | False |
| city/exploratory/cases/WATERLOGGING | 24.683 | 27.070 | [5, 5] | True |
| city/exploratory/cases/ROAD_DAMAGE | 23.254 | 23.904 | [5, 5] | True |
| city/exploratory/cases/WASTE_ACCUMULATION | 23.351 | 23.830 | [5, 5] | True |

These are internal metered analysis wall times, recorded immediately before constructing the final response object. They include DB reads, revision/evidence/record validation and aggregation; exclude repository/client setup, administrative source verification and JSON/file serialization. Ten warm-runtime samples/order statistics are descriptive, not an SLA or statistically reliable tail estimate. No peak-process/native-memory benchmark claimed in B05.

Complete owned clone creation (29nodes/28edges, operational migration + ordinary fenced creates + full hash checks):2.318s. Source revision/audit57 unchanged; clone57→58 after CUT removal→59 after candidate insertion.

Counterfactual actual evidence: D1 downstream D2/D3/D5 becomes D2; D2 impacted D3/D5 becomes none; criticality D1(3),D4(2) becomes D4(2),D1(1); shared SEED/DEPENDENT-CASE D2/D3/D5 becomes D2. Candidate replacement changes exploratory coverage only. Expired link and nearby-but-disconnected control excluded. Public path IDs/edges/provenance and exact before/after/change ledger in controlled-results JSON.

Retained controlled source:`civicly_b05_test_a90264ea8d264ddd927de485bb88fc2e`; owned clone:`civicly_b05_test_8116f39cb7534758a94afbceed39fcee`.

City hashes/counts/revision/audit/writer-state hashes exactly unchanged before/after all measurements. Verified-only drainage has no qualifying paths; all42 DRAINS_TO CANDIDATE. Exploratory D12→D18 found. One ROAD-R08 historical inspection is retrievable in exploratory asset context; no historical work-order/outcome chain. Full city clone refused above120node/200edge cap; controlled fixture is the counterfactual proof.

| Scenario | Exploratory paths | Historical candidates | Case cap hit | Binding context usable | Verified causal readiness |
|---|---|---|---|---|---|
| S01 | 2 | 39 | True | True | False |
| S02 | 2 | 0 | False | True | False |
| S03 | 0 | 1 | False | False | False |
| S04 | 1 | 3 | False | False | False |
| S05 | 4 | 40 | True | True | False |
| S06 | 2 | 3 | False | False | False |
| S07 | 7 | 39 | True | True | False |
| S08 | 10 | 2 | False | False | False |
| S09 | 8 | 5 | False | False | False |
| S10 | 6 | 8 | False | False | False |
| S11 | 1 | 6 | False | False | False |
| S12 | 8 | 4 | False | False | False |

Four broader candidate asset sets S01/S02/S05/S07 are supported by explicit exploratory paths; eight starting sets require source-author correction/confirmation. Six primary-cluster conflicts and three unspecified contexts remain. Budget-unproven extra paths are qualified rather than declared nonexistent. Truncated counts/ranks are partial lower bounds; schema ingestion and these exploratory diagnostics complete no end-to-end product scenario.

B08/B09/B11/B19 remediation is enumerated in B05-scenario-dependencies.json. No source rewriting, verification promotion, fabricated measurement date/history, hidden expected answer or delayed reveal import.
