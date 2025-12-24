#!/usr/bin/env python3
"""
Report generator for scenario execution results.
Generates HTML, JSON, and Markdown reports with Datadog integration data.
"""
from __future__ import annotations

import json
import os
import webbrowser
from datetime import datetime, timezone
from pathlib import Path


def generate_html_report(
    scenario_id: str,
    scenario_data: dict,
    step_results: list[tuple[str, str]],
    overall_status: str,
    artifacts_dir: Path,
) -> Path:
    """Generate HTML report with visual status indicators and Datadog data."""
    
    # Load artifacts
    incidents = []
    observability_events = []
    
    incidents_file = artifacts_dir / "incidents.jsonl"
    if incidents_file.exists():
        with incidents_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        incidents.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    
    obs_file = artifacts_dir / "observability_events.jsonl"
    if obs_file.exists():
        with obs_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        observability_events.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    
    # Filter by scenario_id
    scenario_incidents = [i for i in incidents if i.get("scenario_id") == scenario_id]
    scenario_events = [e for e in observability_events if e.get("scenario_id") == scenario_id]
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scenario Report: {scenario_id}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .status-badge {{
            display: inline-block;
            padding: 10px 30px;
            border-radius: 25px;
            font-size: 1.2em;
            font-weight: bold;
            margin-top: 20px;
        }}
        .status-pass {{
            background: #10b981;
            color: white;
        }}
        .status-fail {{
            background: #ef4444;
            color: white;
        }}
        .content {{
            padding: 40px;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section-title {{
            font-size: 1.5em;
            color: #1f2937;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e5e7eb;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .info-card {{
            background: #f9fafb;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .info-label {{
            font-size: 0.9em;
            color: #6b7280;
            margin-bottom: 5px;
        }}
        .info-value {{
            font-size: 1.1em;
            color: #1f2937;
            font-weight: 600;
        }}
        .steps-list {{
            list-style: none;
        }}
        .step-item {{
            display: flex;
            align-items: center;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            background: #f9fafb;
        }}
        .step-icon {{
            font-size: 1.5em;
            margin-right: 15px;
        }}
        .step-pass {{ background: #d1fae5; }}
        .step-fail {{ background: #fee2e2; }}
        .step-skip {{ background: #fef3c7; }}
        .artifacts-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        .artifacts-table th,
        .artifacts-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }}
        .artifacts-table th {{
            background: #f9fafb;
            font-weight: 600;
            color: #374151;
        }}
        .artifacts-table tr:hover {{
            background: #f9fafb;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        .badge-high {{ background: #fee2e2; color: #991b1b; }}
        .badge-medium {{ background: #fef3c7; color: #92400e; }}
        .badge-low {{ background: #d1fae5; color: #065f46; }}
        .badge-critical {{ background: #fee2e2; color: #7f1d1d; }}
        .datadog-badge {{
            background: #632ca6;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            margin-left: 8px;
        }}
        .timestamp {{
            color: #6b7280;
            font-size: 0.9em;
            margin-top: 20px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Scenario Execution Report</h1>
            <p style="margin-top: 10px; opacity: 0.9;">{scenario_id}</p>
            <div class="status-badge status-{overall_status.lower()}">
                {overall_status}
            </div>
        </div>
        
        <div class="content">
            <div class="section">
                <h2 class="section-title">📋 Scenario Information</h2>
                <div class="info-grid">
                    <div class="info-card">
                        <div class="info-label">Scenario ID</div>
                        <div class="info-value">{scenario_id}</div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">Module</div>
                        <div class="info-value">{scenario_data.get('module', 'N/A')}</div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">Archetype</div>
                        <div class="info-value">{scenario_data.get('archetype', 'N/A')}</div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">Description</div>
                        <div class="info-value">{scenario_data.get('description', 'N/A')}</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">✅ Execution Steps</h2>
                <ul class="steps-list">
"""
    
    for step_name, step_result in step_results:
        if "PASS" in step_result:
            icon = "✅"
            css_class = "step-pass"
        elif "FAIL" in step_result:
            icon = "❌"
            css_class = "step-fail"
        else:
            icon = "⏭️"
            css_class = "step-skip"
        
        html += f"""
                    <li class="step-item {css_class}">
                        <span class="step-icon">{icon}</span>
                        <div>
                            <strong>{step_name}</strong>: {step_result}
                        </div>
                    </li>
"""
    
    html += """
                </ul>
            </div>
"""
    
    # Add incidents section with Datadog data
    if scenario_incidents:
        html += """
            <div class="section">
                <h2 class="section-title">🚨 Incidents</h2>
                <table class="artifacts-table">
                    <thead>
                        <tr>
                            <th>Severity</th>
                            <th>Title</th>
                            <th>Timestamp</th>
                            <th>Datadog Integration</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        for incident in scenario_incidents[-5:]:  # Show last 5
            severity = incident.get("severity", "unknown")
            severity_class = f"badge-{severity}" if severity in ["high", "medium", "low", "critical"] else ""
            datadog_id = incident.get("datadog_incident_id", "")
            oncall_triggered = incident.get("datadog_oncall_triggered", False)
            gmail_sent = incident.get("gmail_notification_sent", False)
            
            datadog_info = ""
            if datadog_id:
                datadog_info = f'<span class="datadog-badge">Incident: {datadog_id[:8]}...</span>'
            if oncall_triggered:
                datadog_info += '<span class="datadog-badge">On-Call Triggered</span>'
            if gmail_sent:
                datadog_info += '<span class="datadog-badge">Gmail Sent</span>'
            
            html += f"""
                        <tr>
                            <td><span class="badge {severity_class}">{severity.upper()}</span></td>
                            <td>{incident.get('title', 'N/A')}</td>
                            <td>{incident.get('timestamp', 'N/A')}</td>
                            <td>{datadog_info if datadog_info else 'N/A'}</td>
                        </tr>
"""
        html += """
                    </tbody>
                </table>
            </div>
"""
    
    # Add observability events section
    if scenario_events:
        html += """
            <div class="section">
                <h2 class="section-title">📡 Observability Events</h2>
                <table class="artifacts-table">
                    <thead>
                        <tr>
                            <th>Signal</th>
                            <th>Flag Action</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        for event in scenario_events[-10:]:  # Show last 10
            html += f"""
                        <tr>
                            <td>{event.get('signal', 'N/A')}</td>
                            <td>{event.get('flag_action', 'N/A')}</td>
                        </tr>
"""
        html += """
                    </tbody>
                </table>
            </div>
"""
    
    html += f"""
            <div class="timestamp">
                Generated: {datetime.now(timezone.utc).isoformat()}
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    report_file = artifacts_dir / f"{scenario_id}_report.html"
    with report_file.open("w", encoding="utf-8") as f:
        f.write(html)
    
    return report_file


def generate_json_summary(
    scenario_id: str,
    scenario_data: dict,
    step_results: list[tuple[str, str]],
    overall_status: str,
    artifacts_dir: Path,
) -> Path:
    """Generate JSON summary report with Datadog metadata."""
    
    # Load latest incident for this scenario
    latest_incident = None
    incidents_file = artifacts_dir / "incidents.jsonl"
    if incidents_file.exists():
        with incidents_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        incident = json.loads(line)
                        if incident.get("scenario_id") == scenario_id:
                            latest_incident = incident
                    except json.JSONDecodeError:
                        pass
    
    summary = {
        "scenario_id": scenario_id,
        "status": overall_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scenario_info": {
            "module": scenario_data.get("module"),
            "archetype": scenario_data.get("archetype"),
            "description": scenario_data.get("description"),
        },
        "execution_steps": [
            {"step": name, "result": result} for name, result in step_results
        ],
        "expected_zeroui_response": scenario_data.get("expected_zeroui_response", {}),
        "datadog_integration": {
            "incident_id": latest_incident.get("datadog_incident_id") if latest_incident else None,
            "oncall_triggered": latest_incident.get("datadog_oncall_triggered", False) if latest_incident else False,
            "gmail_notification_sent": latest_incident.get("gmail_notification_sent", False) if latest_incident else False,
        } if latest_incident else None,
    }
    
    report_file = artifacts_dir / f"{scenario_id}_summary.json"
    with report_file.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    
    return report_file


def open_report_in_browser(report_path: Path) -> None:
    """Open HTML report in default browser."""
    try:
        webbrowser.open(f"file://{report_path.resolve()}")
    except Exception:
        pass  # Silently fail if browser can't be opened

