# How to Run in Cursor

This follows the gold loop: Cursor mutates → harness validates → you reset.

1) Open in Cursor: clone or open this repo; start from a clean working tree.
2) Pick a scenario: choose `FMx` in `scenarios/FM*` and read the matching prompt in `scenario_prompts/FM*`.
3) Apply the prompt: use Cursor to generate or edit code in `apps/` per the scenario intent.
4) Run harness: from Cursor, execute the relevant harness stub (`ci_stub`, `observability_stub`, or `incident_stub`) once scripts are wired; use the scenario’s guidance to select the right entry point.
5) Validate: confirm harness output meets the scenario’s acceptance notes; adjust code if not.
6) Reset: the harness runner automatically restores tracked files and cleans untracked files (`git restore .` + `git clean -fd`) while keeping ignored artifacts in `harness/_artifacts/`. If no git repo or git binary is present, it skips reset and assumes the workspace is already clean before the next scenario.
7) Local tools (optional): start Unleash/Grafana/OnCall with `docker compose up -d` when needed; these use dev-only defaults and local ports.

Product repo integration is deferred; when needed, configure external connections via env vars rather than baking endpoints here.

## Start Tool Stack (PowerShell)
- Start: `docker compose up -d`
- Status: `docker compose ps`
- Stop: `docker compose down`

## Run shop-app tests (PowerShell)
- Create venv: `python -m venv .venv`
- Activate: `.\\.venv\\Scripts\\activate`
- Install deps: `pip install -r apps/shop-app/requirements.txt`
- Run tests: `pytest apps/shop-app`

## Run FM1 Scenarios (PowerShell)
- Apply prompt and run harness for flaky tests:
  - Prompt: `scenario_prompts/FM1/flaky-tests.gold.md`
  - Harness: `python harness/run_scenario.py FM1-flaky-tests`
- Apply prompt and run harness for canary rollback:
  - Prompt: `scenario_prompts/FM1/canary-rollback.gold.md`
  - Harness: `python harness/run_scenario.py FM1-canary-rollback`
- Apply prompt and run harness for flag kill switch:
  - Prompt: `scenario_prompts/FM1/flag-kill-switch.gold.md`
  - Harness: `python harness/run_scenario.py FM1-flag-kill-switch`

## Optional envs
- ZeroUI placeholder call: set `ZEROUI_API_URL` to a reachable endpoint.
- Unleash feature check: set `UNLEASH_URL`, `UNLEASH_TOKEN`, and `UNLEASH_FEATURE` to log enabled status (no effect on PASS/FAIL).
- ZeroUI validation: set `ZEROUI_VALIDATE_URL` (and optional `ZEROUI_VALIDATE_TOKEN`); payload is `expected_zeroui_response`. Set `ZEROUI_VALIDATE_STRICT=true` to mark FAIL on non-2xx.
- Outbound hooks (optional): `CI_WEBHOOK_URL`/`CI_WEBHOOK_TOKEN`, `OBS_WEBHOOK_URL`/`OBS_WEBHOOK_TOKEN`, `INCIDENT_WEBHOOK_URL`/`INCIDENT_WEBHOOK_TOKEN` to receive stub resultsnn.

