#!/usr/bin/env python3
"""
Deterministic incident stub.
- If should_create is true, append a record to harness/_artifacts/incidents.jsonl
- Record fields: scenario_id, severity, title, timestamp (ISO 8601 UTC).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ARTIFACTS_FILE = Path(__file__).resolve().parent.parent / "_artifacts" / "incidents.jsonl"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Incident stub emitter")
    parser.add_argument("--scenario-id", required=True, help="Scenario identifier")
    parser.add_argument("--should-create", action="store_true", help="Create an incident record when set")
    parser.add_argument("--severity", default="unknown", help="Incident severity label")
    parser.add_argument("--title", default="", help="Incident title/summary")
    parser.add_argument("--flag-action", default=None, help="Optional flag action reference")
    return parser.parse_args(argv)


def append_incident(scenario_id: str, severity: str, title: str, flag_action: str | None) -> Path:
    ARTIFACTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "scenario_id": scenario_id,
        "severity": severity,
        "title": title,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if flag_action:
        record["flag_action"] = flag_action
    with ARTIFACTS_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record))
        handle.write("\n")
    return ARTIFACTS_FILE


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if not args.should_create:
        print("[incident_stub] should_create=false; no incident recorded.")
        return 0

    artifact_path = append_incident(args.scenario_id, args.severity, args.title, args.flag_action)
    print(f"[incident_stub] Scenario: {args.scenario_id}")
    print(f"[incident_stub] Severity: {args.severity}")
    print(f"[incident_stub] Title: {args.title}")
    if args.flag_action:
        print(f"[incident_stub] Flag action: {args.flag_action}")
    print(f"[incident_stub] Artifact: {artifact_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

