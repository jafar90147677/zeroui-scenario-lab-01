#!/usr/bin/env python3
"""
Deterministic observability stub.
- Writes provided signals to harness/_artifacts/observability_events.jsonl
- One JSON line per signal: { "scenario_id": ..., "signal": ... }
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ARTIFACTS_FILE = Path(__file__).resolve().parent.parent / "_artifacts" / "observability_events.jsonl"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Observability stub emitter")
    parser.add_argument("--scenario-id", required=True, help="Scenario identifier")
    parser.add_argument("--signal", action="append", required=True, help="Signal name to emit (repeatable)")
    parser.add_argument("--flag-action", default=None, help="Optional flag action description")
    return parser.parse_args(argv)


def emit_signals(scenario_id: str, signals: list[str], flag_action: str | None) -> Path:
    ARTIFACTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACTS_FILE.open("a", encoding="utf-8") as handle:
        for sig in signals:
            line = {"scenario_id": scenario_id, "signal": sig}
            if flag_action:
                line["flag_action"] = flag_action
            handle.write(json.dumps(line))
            handle.write("\n")
    return ARTIFACTS_FILE


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    artifacts_path = emit_signals(args.scenario_id, args.signal, args.flag_action)
    print(f"[observability_stub] Scenario: {args.scenario_id}")
    print(f"[observability_stub] Signals: {args.signal}")
    if args.flag_action:
        print(f"[observability_stub] Flag action: {args.flag_action}")
    print(f"[observability_stub] Artifact: {artifacts_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

