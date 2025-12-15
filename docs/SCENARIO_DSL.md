# Scenario DSL Minimum Contract

This DSL defines the smallest required fields for FM scenarios. Keep each entry lean and focused on the gold loop (Cursor mutation → harness validation → reset). Do not add module-specific fields here.

Required keys
- `id`: unique scenario identifier (e.g., `FM1`).
- `module`: owning surface or app (e.g., `shop-app`, `legacy-monolith`, `data-pipeline`).
- `archetype`: scenario type/category (e.g., regression, perf, incident).
- `description`: concise intent of the scenario.
- `mutation_targets`: code areas the Cursor edits should touch (paths or components).
- `signal_emitters`: which harness signals are exercised. Must include one or more of `ci`, `observability`, `incident`. Emitters may include configuration, e.g. `ci` can provide `exit_code` and an optional `message`, `observability` provides a list of signals to emit deterministically, and `incident` can request a synthetic incident record.
- `expected_zeroui_response`: what ZeroUI should return when signals are emitted (e.g., pills, gates, classification, links). Describe outcome, not endpoints.
- `teardown_reset`: how to return to a clean baseline after validation (e.g., revert changes, reset data).

Archetypes (required: pick one)
- A (quality): flakiness and correctness signals.
- B (release): canary/rollback gating and promotion blocking.
- C (resilience): kill switches and degradation handling.
- D (observability): signal coverage and telemetry confidence.
- E (incident): incident flow readiness and response signals.

Minimal YAML example (structure only)
```yaml
id: FM1
module: shop-app
archetype: regression
description: Ensure checkout error path is guarded and observable.
mutation_targets:
  - apps/shop-app/checkout/
signal_emitters:
  ci:
    exit_code: 0
    message: "expected green build"
  observability:
    signals:
      - "checkout-error-rate"
  incident:
    should_create: true
    severity: "high"
    title: "checkout degraded"
expected_zeroui_response:
  pills: ["ci-pass", "obs-signal"]
  gates: ["checkout-guarded"]
  classification: "regression"
  links: ["runbook://checkout"]
teardown_reset: restore working tree and reset checkout test data
```

