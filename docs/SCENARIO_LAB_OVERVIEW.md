# Scenario Lab Overview

Purpose: provide a safe, repeatable sandbox to exercise FM1–FM15 scenarios with the gold loop: Cursor mutates code → harness checks behavior → validate → reset to a clean baseline.

Repo shape (keep aligned with PRD):
- `apps/` — target surfaces (`shop-app`, `legacy-monolith`, `data-pipeline`).
- `scenarios/FM1..FM15` — scenario briefs and expected outcomes.
- `scenario_prompts/FM1..FM15` — prompts or guidance used inside Cursor.
- `harness/` — CI, observability, and incident stubs that validate runs.
- `docs/` — operator notes (this file, run instructions, architecture, runbook).

Why a separate repo: isolates scenario content and harness logic from product repos; integration to real services happens later via env vars rather than in-repo dependencies.

No-divergence checklist (must hold)
- Dedicated repo only; do not merge scenario work into product repos.
- DSL must be reused; no scenario without the DSL keys.
- Prompt pack is mandatory; scenarios must ship with prompts in `scenario_prompts/`.
- Harness is mandatory; runs go through `harness/run_scenario.py` (and stubs).
- No scenario coding in product repos; keep mutations and validation here.

