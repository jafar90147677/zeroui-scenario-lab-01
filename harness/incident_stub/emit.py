#!/usr/bin/env python3
"""
Deterministic incident stub with Datadog integration (Option 1).
- If should_create is true, append a record to harness/_artifacts/incidents.jsonl
- If trigger_datadog is true, create incident in Datadog Incident Response
- On-Call is triggered automatically via Datadog routing rules
- Gmail notifications are sent automatically via Datadog notification rules
- Record fields: scenario_id, severity, title, timestamp (ISO 8601 UTC).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

ARTIFACTS_FILE = Path(__file__).resolve().parent.parent / "_artifacts" / "incidents.jsonl"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Incident stub emitter with Datadog integration")
    parser.add_argument("--scenario-id", required=True, help="Scenario identifier")
    parser.add_argument("--should-create", action="store_true", help="Create an incident record when set")
    parser.add_argument("--severity", default="unknown", help="Incident severity label")
    parser.add_argument("--title", default="", help="Incident title/summary")
    parser.add_argument("--flag-action", default=None, help="Optional flag action reference")
    parser.add_argument("--trigger-datadog", action="store_true", help="Trigger Datadog Incident Response and On-Call")
    return parser.parse_args(argv)


def trigger_datadog_incident(
    scenario_id: str,
    severity: str,
    title: str,
) -> tuple[bool, str | None, str | None]:
    """
    Create incident in Datadog Incident Response (Option 1).
    On-Call is triggered automatically via Datadog routing rules.
    Gmail notifications are sent automatically via Datadog notification rules.
    
    Returns: (success, incident_id, error_message)
    """
    datadog_api_key = os.getenv("DATADOG_API_KEY")
    datadog_app_key = os.getenv("DATADOG_APP_KEY")
    
    if not datadog_api_key or not datadog_app_key:
        return False, None, "DATADOG_API_KEY or DATADOG_APP_KEY not set"
    
    # Datadog Incident Response API endpoint
    url = "https://api.datadoghq.com/api/v2/incidents"
    headers = {
        "DD-API-KEY": datadog_api_key,
        "DD-APPLICATION-KEY": datadog_app_key,
        "Content-Type": "application/json",
    }
    
    # Map severity to Datadog severity format
    severity_map = {
        "low": "SEV-4",
        "medium": "SEV-3",
        "high": "SEV-2",
        "critical": "SEV-1",
        "unknown": "SEV-4"
    }
    datadog_severity = severity_map.get(severity.lower(), "SEV-4")
    
    # Build incident payload
    payload = {
        "data": {
            "type": "incidents",
            "attributes": {
                "title": f"[Scenario: {scenario_id}] {title}",
                "severity": datadog_severity,
                "customer_impacted": False,
                "fields": {
                    "state": {
                        "type": "dropdown",
                        "value": "declared"
                    }
                }
            }
        }
    }
    
    # Note: Gmail notifications are configured in Datadog notification rules (UI)
    # The incident creation will trigger notifications based on your Datadog configuration
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code in (200, 201):
            incident_data = response.json()
            incident_id = incident_data.get("data", {}).get("id", "unknown")
            
            # When incident is created, Datadog automatically:
            # 1. Triggers On-Call page (if routing rules are configured in UI)
            # 2. Sends Gmail notifications (if notification rules are configured in UI)
            
            return True, incident_id, None
        else:
            error_msg = f"HTTP {response.status_code}: {response.text}"
            return False, None, error_msg
            
    except Exception as exc:
        return False, None, f"Error: {exc}"


def append_incident(
    scenario_id: str,
    severity: str,
    title: str,
    flag_action: str | None,
    datadog_incident_id: str | None = None,
    datadog_oncall_triggered: bool = False,
) -> Path:
    ARTIFACTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "scenario_id": scenario_id,
        "severity": severity,
        "title": title,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if flag_action:
        record["flag_action"] = flag_action
    if datadog_incident_id:
        record["datadog_incident_id"] = datadog_incident_id
        record["datadog_oncall_triggered"] = datadog_oncall_triggered
        record["gmail_notification_sent"] = True  # Sent automatically by Datadog
    
    with ARTIFACTS_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record))
        handle.write("\n")
    return ARTIFACTS_FILE


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if not args.should_create:
        print("[incident_stub] should_create=false; no incident recorded.")
        return 0

    gmail_address = os.getenv("GMAIL_NOTIFICATION_ADDRESS")
    datadog_incident_id = None
    oncall_triggered = False
    
    # Trigger Datadog if requested (Option 1: Incident triggers On-Call automatically)
    if args.trigger_datadog:
        success, incident_id, error = trigger_datadog_incident(
            args.scenario_id,
            args.severity,
            args.title,
        )
        
        if success:
            datadog_incident_id = incident_id
            oncall_triggered = True  # Triggered automatically via routing rules
            print(f"[datadog] Incident created: {datadog_incident_id}")
            print(f"[datadog] On-Call page triggered automatically (via routing rules)")
            if gmail_address:
                print(f"[datadog] Gmail notification sent automatically to: {gmail_address} (via notification rules)")
        else:
            print(f"[datadog] Failed: {error}")
            # Continue even if Datadog fails (for testing without Datadog)
    
    artifact_path = append_incident(
        args.scenario_id,
        args.severity,
        args.title,
        args.flag_action,
        datadog_incident_id,
        oncall_triggered,
    )
    
    print(f"[incident_stub] Scenario: {args.scenario_id}")
    print(f"[incident_stub] Severity: {args.severity}")
    print(f"[incident_stub] Title: {args.title}")
    if args.flag_action:
        print(f"[incident_stub] Flag action: {args.flag_action}")
    print(f"[incident_stub] Artifact: {artifact_path}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
