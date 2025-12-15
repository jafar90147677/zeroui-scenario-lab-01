# ZeroUI Scenario Lab Runbook (Ops)

Objectives
- Keep the lab reproducible: mutate via prompts, validate via harness, reset to clean.
- Use OSS local stack for manual validation; stubs for automated harness runs.

Daily checks
- `docker compose ps` (expect Grafana 3300, Unleash 42420, OnCall 18080; oncall-migrate may exit after applying migrations).
- `python harness/run_scenario.py FM1-flaky-tests` (sanity).

Env vars (optional)
- `ZEROUI_API_URL` — placeholder GET to your ZeroUI endpoint.
- `UNLEASH_URL`, `UNLEASH_TOKEN`, `UNLEASH_FEATURE` — logs feature enabled state; no effect on PASS/FAIL.

Running scenarios
1) Apply the Gold Prompt in Cursor (matching the scenario YAML).
2) Run harness: `python harness/run_scenario.py <scenario_id>`.
3) Inspect artifacts: `harness/_artifacts/observability_events.jsonl`, `harness/_artifacts/incidents.jsonl`.
4) Harness resets repo via git (keeps ignored artifacts). If no git, reset is skipped (assumes clean workspace).

Local stack
- Start: `docker compose up -d`
- Stop: `docker compose down`

Troubleshooting
- Port conflicts: adjust `docker-compose.yml` (Grafana 3300, Unleash 42420, OnCall 18080).
- OnCall migrate restarts: expected to run then exit.
- Tests failing: run `pytest apps/shop-app` to reproduce.
