#!/usr/bin/env python3
"""
Minimal harness runner for scenarios.
- Resolves scenario_id to a YAML under scenarios/FM*/.
- Loads YAML (PyYAML) and prints planned steps; no external calls.
Mapping: scenario_id of the form FM<number>-<slug> maps to scenarios/FM<number>/<slug>.yaml.
Falls back to searching for a YAML whose stem matches scenario_id.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

import requests
import zeroui_assert

try:
    import yaml  # type: ignore
except ImportError as exc:
    sys.stderr.write("PyYAML not installed. Run: pip install -r harness/requirements.txt\n")
    raise SystemExit(1) from exc


REPO_ROOT = Path(__file__).resolve().parent.parent
HARNESS_DIR = Path(__file__).resolve().parent
SCENARIOS_DIR = REPO_ROOT / "scenarios"
ARTIFACTS_DIR = HARNESS_DIR / "_artifacts"
CI_STUB_PATH = HARNESS_DIR / "ci_stub" / "run_ci_stub.py"
OBS_STUB_PATH = HARNESS_DIR / "observability_stub" / "emit.py"
INCIDENT_STUB_PATH = HARNESS_DIR / "incident_stub" / "emit.py"


def resolve_scenario_path(scenario_id: str) -> Path:
    """Map scenario_id to a YAML file using the stable FMn-<slug> convention."""
    if "-" in scenario_id:
        fm_prefix, slug = scenario_id.split("-", 1)
        candidate = SCENARIOS_DIR / fm_prefix / f"{slug}.yaml"
        if candidate.is_file():
            return candidate

    # Fallback: search by filename stem across scenarios.
    matches = [p for p in SCENARIOS_DIR.rglob("*.yaml") if p.stem == scenario_id]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise FileExistsError(f"Scenario id '{scenario_id}' is ambiguous: {matches}")
    raise FileNotFoundError(f"Scenario YAML not found for id '{scenario_id}'")


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def ensure_artifacts_dir() -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


def format_signal_emitters(signal_emitters: object) -> str:
    if isinstance(signal_emitters, dict):
        return ", ".join(sorted(signal_emitters.keys()))
    if isinstance(signal_emitters, list):
        return ", ".join(signal_emitters)
    return str(signal_emitters)


def print_plan(scenario_id: str, path: Path, data: dict) -> None:
    rel_path = path.relative_to(REPO_ROOT)
    mutation_targets = data.get("mutation_targets") or []
    signal_emitters = data.get("signal_emitters") or []
    print(f"Resolved scenario: {scenario_id}")
    print(f"YAML path: {rel_path}")
    print(f"Module: {data.get('module', '(missing)')}")
    print(f"Archetype: {data.get('archetype', '(missing)')}")
    print(f"Description: {data.get('description', '(missing)')}")
    print(f"Mutation targets: {mutation_targets}")
    print(f"Signal emitters: {format_signal_emitters(signal_emitters)}")
    print("Planned steps: load scenario → run harness stubs → report → reset.")


def extract_ci_config(signal_emitters: object) -> dict | None:
    if not signal_emitters:
        return None
    cfg = None
    if isinstance(signal_emitters, dict) and "ci" in signal_emitters:
        raw = signal_emitters.get("ci") or {}
        if isinstance(raw, dict):
            cfg = raw
        else:
            cfg = {}
    elif isinstance(signal_emitters, list) and "ci" in signal_emitters:
        cfg = {}

    if cfg is None:
        return None

    exit_code_raw = cfg.get("exit_code", 0) if isinstance(cfg, dict) else 0
    try:
        exit_code = int(exit_code_raw)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid ci.exit_code value: {exit_code_raw}")

    message = ""
    if isinstance(cfg, dict):
        msg_raw = cfg.get("message", "")
        message = "" if msg_raw is None else str(msg_raw)

    return {"exit_code": exit_code, "message": message}


def extract_observability_config(signal_emitters: object) -> dict | None:
    if not signal_emitters:
        return None
    cfg = None
    if isinstance(signal_emitters, dict) and "observability" in signal_emitters:
        raw = signal_emitters.get("observability") or {}
        if isinstance(raw, dict):
            cfg = raw
        else:
            cfg = {}
    elif isinstance(signal_emitters, list) and "observability" in signal_emitters:
        return {"signals": [], "flag_action": None}

    if cfg is None:
        return None

    signals = cfg.get("signals", [])
    if signals is None:
        signals = []
    if not isinstance(signals, list):
        raise ValueError("observability.signals must be a list")
    normalized = [str(s) for s in signals]
    flag_action = cfg.get("flag_action")
    if flag_action is not None:
        flag_action = str(flag_action)
    return {"signals": normalized, "flag_action": flag_action}


def extract_incident_config(signal_emitters: object) -> dict | None:
    if not signal_emitters:
        return None
    cfg = None
    if isinstance(signal_emitters, dict) and "incident" in signal_emitters:
        raw = signal_emitters.get("incident") or {}
        if isinstance(raw, dict):
            cfg = raw
        else:
            cfg = {}
    elif isinstance(signal_emitters, list) and "incident" in signal_emitters:
        cfg = {}

    if cfg is None:
        return None

    should_create = bool(cfg.get("should_create", False)) if isinstance(cfg, dict) else False
    severity = ""
    title = ""
    if isinstance(cfg, dict):
        severity = str(cfg.get("severity", "unknown"))
        title = str(cfg.get("title", ""))

    flag_action = None
    if isinstance(cfg, dict) and "flag_action" in cfg:
        flag_action = cfg.get("flag_action")
        if flag_action is not None:
            flag_action = str(flag_action)

    return {"should_create": should_create, "severity": severity, "title": title, "flag_action": flag_action}


def run_ci_stub(scenario_id: str, ci_config: dict) -> int:
    cmd = [
        sys.executable,
        str(CI_STUB_PATH),
        "--scenario-id",
        scenario_id,
        "--exit-code",
        str(ci_config.get("exit_code", 0)),
    ]
    message = ci_config.get("message")
    if message:
        cmd += ["--message", str(message)]

    proc = subprocess.run(cmd, cwd=REPO_ROOT)
    return proc.returncode


def run_observability_stub(scenario_id: str, cfg: dict) -> int:
    signals = cfg.get("signals", [])
    flag_action = cfg.get("flag_action")
    if not signals:
        print("[observability_stub] No signals provided; skipping emission.")
        return 0
    cmd = [
        sys.executable,
        str(OBS_STUB_PATH),
        "--scenario-id",
        scenario_id,
    ]
    for sig in signals:
        cmd += ["--signal", sig]
    if flag_action:
        cmd += ["--flag-action", flag_action]

    proc = subprocess.run(cmd, cwd=REPO_ROOT)
    return proc.returncode


def run_incident_stub(scenario_id: str, cfg: dict) -> int:
    cmd = [
        sys.executable,
        str(INCIDENT_STUB_PATH),
        "--scenario-id",
        scenario_id,
    ]
    if cfg.get("should_create"):
        cmd.append("--should-create")
    if cfg.get("severity"):
        cmd += ["--severity", str(cfg.get("severity"))]
    if cfg.get("title"):
        cmd += ["--title", str(cfg.get("title"))]
    if cfg.get("flag_action"):
        cmd += ["--flag-action", str(cfg.get("flag_action"))]

    proc = subprocess.run(cmd, cwd=REPO_ROOT)
    return proc.returncode


def reset_repo_state() -> bool:
    """Restore tracked changes and clean untracked files/dirs, preserving ignored artifacts."""
    if not (REPO_ROOT / ".git").exists():
        print("Reset skipped: no .git directory detected (workspace assumed clean).")
        return True
    if shutil.which("git") is None:
        print("Reset skipped: git executable not found in PATH.")
        return True

    print("Resetting repository state (keeps ignored artifacts)...")
    commands = [
        ["git", "restore", "."],
        ["git", "clean", "-fd"],
    ]
    for cmd in commands:
        proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        if proc.returncode != 0:
            sys.stderr.write(f"Command failed: {' '.join(cmd)}\n")
            if proc.stderr:
                sys.stderr.write(proc.stderr)
            return False
    return True


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a Scenario Lab harness stub.")
    parser.add_argument("scenario_id", help="Scenario id, e.g., FM1-flaky-tests")
    return parser.parse_args(argv)


def run_tests() -> int:
    """Run pytest for shop-app; return exit code."""
    cmd = [sys.executable, "-m", "pytest", "apps/shop-app"]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT)
    proc = subprocess.run(cmd, cwd=REPO_ROOT, env=env)
    return proc.returncode


def try_unleash_feature(base_url: str | None, token: str | None, feature_key: str | None) -> str:
    if not (base_url and token and feature_key):
        return "Unleash check skipped (UNLEASH_URL, UNLEASH_TOKEN, UNLEASH_FEATURE not all set)"
    url = base_url.rstrip("/") + f"/api/client/features/{feature_key}"
    headers = {"Authorization": token, "Accept": "application/json"}
    try:
        resp = requests.get(url, headers=headers, timeout=3)
    except Exception as exc:  # noqa: BLE001
        return f"Unleash check error: {exc}"
    if resp.status_code != 200:
        return f"Unleash check HTTP {resp.status_code}"
    try:
        data = resp.json()
    except Exception as exc:  # noqa: BLE001
        return f"Unleash check JSON error: {exc}"
    enabled = data.get("enabled")
    return f"Unleash feature {feature_key}: enabled={enabled}"


def post_hook(url: str | None, token: str | None, payload: dict, name: str) -> str:
    if not url:
        return f"{name} webhook skipped (no URL set)"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if token:
        headers["Authorization"] = token
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=5)
    except Exception as exc:  # noqa: BLE001
        return f"{name} webhook error: {exc}"
    return f"{name} webhook HTTP {resp.status_code}"


def validate_zero_ui(expected_resp: object, url: str | None, token: str | None, strict: bool) -> tuple[bool, str]:
    if not url:
        return True, "ZeroUI validation skipped (ZEROUI_VALIDATE_URL not set)"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if token:
        headers["Authorization"] = token
    try:
        resp = requests.post(url, headers=headers, json={"expected": expected_resp}, timeout=5)
    except Exception as exc:  # noqa: BLE001
        msg = f"ZeroUI validation error: {exc}"
        return (False if strict else True), msg
    if 200 <= resp.status_code < 300:
        return True, f"ZeroUI validation HTTP {resp.status_code}"
    msg = f"ZeroUI validation HTTP {resp.status_code}"
    return (False if strict else True), msg


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    ensure_artifacts_dir()
    zeroui_api_url = os.getenv("ZEROUI_API_URL")
    if zeroui_api_url:
        print(f"ZEROUI_API_URL = {zeroui_api_url}")
    else:
        print("ZEROUI_API_URL not set")
    try:
        scenario_path = resolve_scenario_path(args.scenario_id)
    except (FileNotFoundError, FileExistsError) as err:
        sys.stderr.write(f"{err}\n")
        return 1

    data = load_yaml(scenario_path)
    print_plan(args.scenario_id, scenario_path, data)

    overall_ok = True
    step_results: list[tuple[str, str]] = []

    tests_rc = run_tests()
    if tests_rc != 0:
        overall_ok = False
        step_results.append(("tests", f"FAIL (exit {tests_rc})"))
    else:
        step_results.append(("tests", "PASS"))

    try:
        ci_cfg = extract_ci_config(data.get("signal_emitters"))
    except ValueError as err:
        sys.stderr.write(f"{err}\n")
        return 1
    if ci_cfg:
        ci_rc = run_ci_stub(args.scenario_id, ci_cfg)
        if ci_rc != 0:
            sys.stderr.write(f"CI stub failed with exit code {ci_rc}\n")
            overall_ok = False
            step_results.append(("ci_stub", f"FAIL (exit {ci_rc})"))
        else:
            step_results.append(("ci_stub", "PASS"))
    else:
        step_results.append(("ci_stub", "SKIPPED (not configured)"))

    try:
        obs_cfg = extract_observability_config(data.get("signal_emitters"))
    except ValueError as err:
        sys.stderr.write(f"{err}\n")
        return 1
    if obs_cfg is not None:
        obs_rc = run_observability_stub(args.scenario_id, obs_cfg)
        if obs_rc != 0:
            sys.stderr.write(f"Observability stub failed with exit code {obs_rc}\n")
            overall_ok = False
            step_results.append(("observability_stub", f"FAIL (exit {obs_rc})"))
        else:
            step_results.append(("observability_stub", "PASS"))
    else:
        step_results.append(("observability_stub", "SKIPPED (not configured)"))

    try:
        incident_cfg = extract_incident_config(data.get("signal_emitters"))
    except ValueError as err:
        sys.stderr.write(f"{err}\n")
        return 1
    if incident_cfg is not None:
        incident_rc = run_incident_stub(args.scenario_id, incident_cfg)
        if incident_rc != 0:
            sys.stderr.write(f"Incident stub failed with exit code {incident_rc}\n")
            overall_ok = False
            step_results.append(("incident_stub", f"FAIL (exit {incident_rc})"))
        else:
            step_results.append(("incident_stub", "PASS"))
    else:
        step_results.append(("incident_stub", "SKIPPED (not configured)"))

    # Placeholder ZeroUI contact (does not affect PASS/FAIL)
    expected_resp = data.get("expected_zeroui_response")
    print(zeroui_assert.summarize_expected(expected_resp))
    print(zeroui_assert.attempt_zeroui_contact(zeroui_api_url))

    unleash_result = try_unleash_feature(
        base_url=os.getenv("UNLEASH_URL"),
        token=os.getenv("UNLEASH_TOKEN"),
        feature_key=os.getenv("UNLEASH_FEATURE"),
    )
    print(unleash_result)

    # Optional ZeroUI validation (payload is expected_zeroui_response)
    strict_zeroui = os.getenv("ZEROUI_VALIDATE_STRICT", "").lower() in {"1", "true", "yes"}
    zeroui_ok, zeroui_msg = validate_zero_ui(
        expected_resp,
        url=os.getenv("ZEROUI_VALIDATE_URL"),
        token=os.getenv("ZEROUI_VALIDATE_TOKEN"),
        strict=strict_zeroui,
    )
    print(zeroui_msg)
    if not zeroui_ok:
        overall_ok = False
        step_results.append(("zeroui_validation", "FAIL"))
    else:
        step_results.append(("zeroui_validation", "PASS" if zeroui_api_url else "SKIPPED/INFO"))

    # Optional outbound hooks
    ci_hook_msg = post_hook(
        url=os.getenv("CI_WEBHOOK_URL"),
        token=os.getenv("CI_WEBHOOK_TOKEN"),
        payload={"scenario_id": args.scenario_id, "ci_exit": ci_cfg["exit_code"] if ci_cfg else None},
        name="CI",
    )
    obs_hook_msg = post_hook(
        url=os.getenv("OBS_WEBHOOK_URL"),
        token=os.getenv("OBS_WEBHOOK_TOKEN"),
        payload={"scenario_id": args.scenario_id, "signals": obs_cfg.get("signals") if "obs_cfg" in locals() and obs_cfg else None},
        name="OBS",
    )
    incident_hook_msg = post_hook(
        url=os.getenv("INCIDENT_WEBHOOK_URL"),
        token=os.getenv("INCIDENT_WEBHOOK_TOKEN"),
        payload={
            "scenario_id": args.scenario_id,
            "should_create": incident_cfg.get("should_create") if incident_cfg else None,
            "severity": incident_cfg.get("severity") if incident_cfg else None,
            "title": incident_cfg.get("title") if incident_cfg else None,
        },
        name="INCIDENT",
    )
    print(ci_hook_msg)
    print(obs_hook_msg)
    print(incident_hook_msg)

    reset_ok = reset_repo_state()
    overall_ok = overall_ok and reset_ok
    step_results.append(("reset", "PASS" if reset_ok else "FAIL"))

    status = "PASS" if overall_ok else "FAIL"
    print("\n=== Scenario Result ===")
    print(f"Scenario: {args.scenario_id}")
    print(f"Status: {status}")
    for name, result in step_results:
        print(f"- {name}: {result}")

    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

