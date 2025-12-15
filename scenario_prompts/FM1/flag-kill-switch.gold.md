# Gold Prompt: FM1 Flag Kill Switch

- Read the scenario spec at `scenarios/FM1/flag-kill-switch.yaml`.
- Apply only the required mutation targets described there; do not edit anything else by hand.

Files to read
- `scenarios/FM1/flag-kill-switch.yaml`
- `apps/shop-app/app.py`

Files to modify
- `apps/shop-app/app.py` only.

Required mutation (feature-flag kill switch, no external calls)
- Add a dedicated endpoint (e.g., `/flag-action`) that returns 200 JSON: `{"flag_action": "kill-switch:checkout", "status": "disabled"}`.
- Keep `/health` and any other existing endpoints unchanged.
- Do not add dependencies or connect to Unleash; this is a stubbed kill switch record.

Do not change
- Do not modify tests in this scenario; harness observability/incident stubs will record the flag action per YAML.

Reset instructions
- After harness validation, rely on the harness reset (git restore . && git clean -fd) to return to a clean state.

