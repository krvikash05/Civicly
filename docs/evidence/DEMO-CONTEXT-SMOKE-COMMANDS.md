# Exact commands/results

```sh
CIVICLY_TEST_REQUEST_LOG=/tmp/civicly-context-smoke-unit-provider.jsonl backend/.venv/bin/python -m pytest backend/tests/unit/test_context_smoke.py backend/tests/unit/test_context_wire.py backend/tests/unit/test_demo_host.py -q
make test-spec
```
33unitPASS1.85s;bothvalidatorsPASS. Ordinarytests noexternalproviderrequests;smokeguards reject nonREAD/write tools/unknown case/implicit live/replaymarkers. Official/domain response-envelope regression validates exactReadResult.

Paid command executed **once**, initialharnessresult failed after actualsuccessfulread:

```sh
PYTHONPATH=backend backend/.venv/bin/python -m app.demo_host --config .runtime/demo-presenter/run-01/host-rehearsal02.json context-smoke --live --case INV-B09-8b006fb97aa2b908fc69addcf7ecd037
```
Do NOT rerun; owner-only marker blocks automaticrepeat.1count+1generation and1MCPread, no workflowresume. Review RESULTS for preserved status-envelope defect.

Reusable **nonbillable verification**, exercised in a separate freshprocess:

```sh
PYTHONPATH=backend backend/.venv/bin/python -m app.demo_host --config .runtime/demo-presenter/run-01/host-rehearsal02.json context-smoke-verify
```
PASS_VERIFIED_FROM_DURABLE_READBACK. It verifies actual retainedBROKERtrace/hash/scope/success, originalcheckpointID+hash, unchangedsource627, noprobesavercheckpoint and originalrequest ledgerSETTLED. It sends0providerrequests, performs0MCPredispatches and mutates0case/receipt states. Sourcechangeslater intentionallyinvalidate currentstateverification.

Actualfrontendconnection diagnostic:POSTbackenddemo-login200;POSTfrontend/api/demo-session200;GETfrontend/api/v1/incidentswithtemporaryanalysttoken200; bothtemporarysessions loggedout. Credentialvalues neverexported; no frontend edits/restart. Private config matchedpresenter; userconfirmedrecovery.
