#!/usr/bin/env python3
"""
Deterministic CI stub driven by scenario YAML.
- Exits with the exit_code provided.
- Prints a short message for visibility.
"""
from __future__ import annotations

import argparse
import sys


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CI stub runner")
    parser.add_argument("--scenario-id", required=True, help="Scenario identifier")
    parser.add_argument("--exit-code", type=int, required=True, help="Exit code to return")
    parser.add_argument("--message", default="", help="Optional message to print")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    print(f"[ci_stub] Scenario: {args.scenario_id}")
    print(f"[ci_stub] Exit code: {args.exit_code}")
    if args.message:
        print(f"[ci_stub] Message: {args.message}")
    return args.exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

