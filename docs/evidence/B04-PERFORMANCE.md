# B04 measured benchmark — real FalkorDB6.0.2

Python3.12.1 arm64; macOS26.5;8 physical cores,8GiB RAM. Dependencies remain pinned: falkordb1.8.0, redis8.1.0, Pydantic2.14.1; migration0001 and registry unchanged. See runtime/images/hardware evidence. AOF enabled, appendfsync always (verified by persistence regression). No canonical import or raw bulk loader.

| Trial | Initial seconds | Records/sec | p50 / p95 / p99 sec | Peak traced MiB | Repeat1 / repeat2 sec | AOF net bytes | Server memory net bytes |
|---|---|---|---|---|---|---|---|
| Pilot | 4.809 | 42.835 | 0.018038 / 0.049333 / 0.057310 | 0.580 | 0.294 / 0.335 | 5658912 | 1207504 |
| 1 | 172.941 | 12.166 | 0.063162 / 0.213637 / 0.283179 | 4.330 | 12.092 / 12.063 | -26543211 | 2073752 |
| 2 | 171.731 | 12.252 | 0.062930 / 0.212515 / 0.282773 | 4.330 | 11.864 / 11.590 | 39671379 | 2102560 |
| 3 | 172.195 | 12.219 | 0.061588 / 0.215496 / 0.283059 | 4.330 | 11.848 / 11.929 | -26070251 | 2156096 |

Median full initial import: **172.195s**. Pilot106nodes/100edges; each full trial858nodes/1246relationships. Every repeated import created0/matched2104; content hashes, revision2104 and audit2104 unchanged. All three full trials met proposed <=300s initial, <=120s repeat and <=256MiB traced-memory targets.

Each full trial ends with560,586 audit bytes (21.04% of10,000-entry cap). Actual largest policy scan:259 prior REPORTS (260 final); other populations and checkpoints are in B04-benchmarks.json. At first/25/50/75/100% checkpoints audit bytes245/128922/264996/412802/560586. All proven writes use lock/fence/intent/audit and unchanged caps. Largest per-kind population is far below2,000 but this is not a scale guarantee.

Graph-query command/parameter totals cover initial plus both repeats. Each full trial:6315 GRAPH.QUERY calls and24134 GRAPH.RO_QUERY calls; parameter traffic approximately635.6MB (not a network packet or cumulative disk-I/O measurement). The audit is repeatedly serialized/transmitted; aggregate cost and policy scans remain quadratic. Only initial wall/latency/peak/storage fields cover initial import; they include preflight and final verification. Migration time recorded separately. Tracemalloc/counting instrumentation adds overhead.

AOF byte deltas are net server-wide snapshots, affected by successful background rewrites confirmed in B04-aof-activity.txt. Negative deltas do not represent negative writes. Exact cumulative bytes written, cycle/schedule comparison totals and lock-wait distribution were not instrumented; report these limitations rather than treating another metric as equivalent.

Retained final review graph: `civicly_b04_test_a84beda80da64aacbc367a9399e07a97`. Successful pilot/trial1/trial2 graphs individually cleaned; failed precision graph retained. Original graphs/volumes were not reset. All full imports compare every record hash and counts against bundle content hash `c84b9dea1f136640ae3d5acfc25f13078a833311aac63d914366ff589b5decae`.

Fault/recovery/concurrency workloads are separate real integration tests, not included in these timing targets. No new batching, audit-journal, identity-index or performance migration is implemented. Any future optimization requires separate review and full write-guarantee regression.

Memory scope:tracemalloc measures traced Python allocations, excluding native
allocations/process RSS. Server INFO used_memory is a net snapshot, not a peak
container-memory measurement. Host hardware numbers do not assert a Docker VM
resource limit. The successful timing trials precede final malformed-envelope/
verification-report hardening; the domain write path and dataset are unchanged,
and final-code integrity tests are recorded separately.
