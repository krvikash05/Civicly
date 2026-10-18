# Separately invoked live investigation

Normal pytest explicitly excludes this directory and blocks external Gemini HTTP/DNS in the runner and Python children. Credentials do not opt in. No live run is authorized by B10-O.

After human approval for one specified case, the operator may use the genuine CLI:

```sh
PYTHONPATH=backend backend/.venv/bin/python -m app.agents --profile .runtime/b10-active.json --investigation INV_ID --thread THREAD_ID --live --max-cost-usd 0.15
```

For a resumed thread, `--resume` also requires its investigation ID for the live permit. The command is subject to the durable project ledger, per-case allowance, pricing version/expiry and one-live-investigation concurrency guard. It is not run during the ordinary suite. Do not set the test interlock off inside pytest. Do not run the outstanding contradiction/topology live acceptance tests during B10-O.
