# Gold Prompt: FM1 Flaky Tests

- Read the scenario spec at `scenarios/FM1/flaky-tests.yaml`.
- Apply only the required mutation targets described there; do not edit anything else by hand.

Files to read
- `scenarios/FM1/flaky-tests.yaml`
- `apps/shop-app/tests/test_basic.py`

Files to modify
- `apps/shop-app/tests/test_basic.py` only.

Required mutation (introduce controlled flakiness)
- In the health test, add a small random failure branch (e.g., `random.random() < 0.3` raising an assertion with message like "simulated flaky failure").
- Import `random` if needed. Keep the existing assertions unchanged.
- Flakiness must be deterministic in implementation (probabilistic but limited to the single test) and easy to remove via reset.

Do not change
- Do not modify app code, other tests, requirements, or harness files.

Reset instructions
- After harness validation, rely on the harness reset (git restore . && git clean -fd) to return to a clean state.

