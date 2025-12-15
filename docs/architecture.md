# ZeroUI Scenario Lab Architecture

This repo is a sandbox (not product code) with a consistent pattern:
- `apps/`: small target systems to mutate. Current: `shop-app` (Flask + pytest); placeholders for `legacy-monolith`, `data-pipeline`.
- `scenarios/FM1..FM15`: Scenario DSL YAMLs describing id, module, archetype, mutation_targets, signal_emitters, expected_zeroui_response, teardown_reset.
- `scenario_prompts/FM1..FM15`: Gold Prompts for Cursor; each prompt applies only the mutations in the corresponding YAML.
- `harness/`: `run_scenario.py` plus CI/observability/incident stubs, artifacts folder, optional Unleash check, reset logic.
- `docs/`: overview, DSL, run instructions, runbook (ops notes).
- `docker-compose.yml`: local OSS stack (Unleash, Grafana, OnCall) for optional manual validation.

Flow (gold loop):
Cursor applies prompt → harness runs tests and stubs → logs PASS/FAIL → resets repo (keeps ignored artifacts) → repeat.
