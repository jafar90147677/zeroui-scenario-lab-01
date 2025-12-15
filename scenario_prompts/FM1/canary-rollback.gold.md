# Gold Prompt: FM1 Canary Rollback

- Read the scenario spec at `scenarios/FM1/canary-rollback.yaml`.
- Apply only the required mutation targets described there; do not edit anything else by hand.

Files to read
- `scenarios/FM1/canary-rollback.yaml`
- `apps/shop-app/app.py`

Files to modify
- `apps/shop-app/app.py` only.

Required mutation (simulate canary failure signal)
- Add a dedicated endpoint (e.g., `/canary`) that returns a 500 response with JSON payload indicating `{"status": "failed", "reason": "canary"}`.
- Keep existing `/health` endpoint unchanged.
- Keep changes minimal and easily reverted by reset; no external calls.

Do not change
- Do not modify tests here; harness CI stub will report failure per scenario YAML.
- Do not add dependencies or services.

Reset instructions
- After harness validation, rely on the harness reset (git restore . && git clean -fd) to return to a clean state.

