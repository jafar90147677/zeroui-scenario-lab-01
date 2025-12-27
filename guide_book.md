# ZeroUI Scenario Lab - Implementation Guide Book

## Table of Contents
1. [Overview](#overview)
2. [Datadog Integration Summary](#datadog-integration-summary)
3. [GitHub Actions Workflow Changes](#github-actions-workflow-changes)
4. [Datadog Incident Response Integration](#datadog-incident-response-integration)
5. [Scenario Configuration Updates](#scenario-configuration-updates)
6. [Environment Variables and Configuration](#environment-variables-and-configuration)
7. [Testing and Validation](#testing-and-validation)
8. [Docker Datadog Agent Setup](#docker-datadog-agent-setup)
9. [Usage Examples](#usage-examples)
10. [Troubleshooting](#troubleshooting)

---

## Overview

This guide documents all Datadog integrations and implementations made to the `zeroui-scenario-lab-01` repository. The primary goal was to integrate Datadog for comprehensive scenario tracking, incident management, and observability.

### Key Integrations Implemented

1. **GitHub Actions - Datadog Test Optimization**: Automatic test visibility and tracking
2. **GitHub Actions - Automatic Incident Creation**: Creates Datadog incidents on CI test failures
3. **Scenario Incident Stub - Datadog Integration**: Direct integration with Datadog Incident Response API
4. **Datadog Connection Testing**: Validation script for API credentials
5. **Docker Datadog Agent**: Containerized agent for local monitoring

---

## Datadog Integration Summary

### What Was Implemented

| Component | Status | Description |
|-----------|--------|-------------|
| GitHub Actions Test Optimization | ✅ Complete | Datadog test visibility integration |
| CI Failure Incident Creation | ✅ Complete | Automatic incident creation on test failures |
| Scenario Incident Integration | ✅ Complete | Direct API integration in incident stub |
| Datadog Connection Testing | ✅ Complete | Validation script for credentials |
| Docker Datadog Agent | ✅ Documented | Setup instructions for containerized agent |

### Datadog Site Configuration
- **Site**: `us5.datadoghq.com`
- **API Endpoint**: `https://api.datadoghq.com`
- **Trace Endpoint**: `https://trace-intake.us5.datadoghq.com`

---

## GitHub Actions Workflow Changes

### File Modified
- `.github/workflows/python-tests.yml`

### Changes Made

#### 1. Datadog Test Optimization Step

Added a new step to configure Datadog Test Visibility for Python tests:

```yaml
- name: Configure Datadog Test Optimization
  uses: datadog/test-visibility-github-action@v2
  with:
    languages: python
    api_key: ${{secrets.DD_API_KEY}}
    site: us5.datadoghq.com
```

**Location**: After "Set up Python" step, before "Install deps" step

**Purpose**: 
- Enables test visibility in Datadog
- Tracks test execution, failures, and performance
- Provides insights into test reliability

**Required Secret**: `DD_API_KEY` must be configured in GitHub repository settings

#### 2. Automatic Incident Creation on Test Failure

Added a step that automatically creates a Datadog incident when tests fail:

```yaml
- name: Create Datadog Incident on Test Failure
  if: failure() && steps.pytest.outcome == 'failure'
  env:
    DATADOG_API_KEY: ${{secrets.DATADOG_API_KEY}}
    DATADOG_APP_KEY: ${{secrets.DATADOG_APP_KEY}}
  run: |
    python -c "
    # ... incident creation logic ...
    "
```

**Location**: After "Run pytest (shop-app)" step

**Purpose**:
- Automatically creates SEV-2 incidents in Datadog when CI tests fail
- Includes workflow context (run ID, commit SHA, branch, actor)
- Links to GitHub Actions run URL

**Required Secrets**:
- `DATADOG_API_KEY`: Datadog API key
- `DATADOG_APP_KEY`: Datadog Application key with "Incident Management" permissions

**Incident Details**:
- **Severity**: SEV-2 (High)
- **Title**: `CI Test Failure: {workflow_name} (Run #{run_number})`
- **Includes**: Repository, branch, commit SHA, trigger actor, workflow run URL

---

## Datadog Incident Response Integration

### File Modified
- `harness/incident_stub/emit.py`

### Key Changes

#### 1. Datadog Incident Creation Function

Added `trigger_datadog_incident()` function that:
- Creates incidents via Datadog Incident Response API v2
- Maps scenario severity to Datadog severity format (SEV-1 through SEV-4)
- Includes scenario context in incident title
- Returns incident ID and success status

**Severity Mapping**:
```python
severity_map = {
    "low": "SEV-4",
    "medium": "SEV-3",
    "high": "SEV-2",
    "critical": "SEV-1",
    "unknown": "SEV-4"
}
```

#### 2. Credential Validation

Added `validate_datadog_credentials()` function that:
- Validates API key before making incident creation calls
- Provides helpful error messages for common issues
- Non-blocking (continues even if validation fails)

#### 3. Enhanced Incident Record

Updated `append_incident()` to include:
- `datadog_incident_id`: The Datadog incident ID
- `datadog_oncall_triggered`: Boolean indicating if On-Call was triggered
- `gmail_notification_sent`: Boolean (automatically true when Datadog incident is created)

#### 4. Command-Line Flag

Added `--trigger-datadog` flag to enable Datadog incident creation:
```bash
python harness/incident_stub/emit.py \
  --scenario-id FM1-canary-rollback \
  --should-create \
  --severity high \
  --title "canary rollback triggered" \
  --trigger-datadog
```

### Integration Flow

1. Scenario runs and determines an incident should be created
2. `incident_stub/emit.py` is called with `--trigger-datadog` flag
3. Function validates credentials (non-blocking)
4. Incident is created via Datadog API
5. Datadog automatically:
   - Triggers On-Call page (if routing rules configured)
   - Sends Gmail notifications (if notification rules configured)
6. Incident ID is stored in `harness/_artifacts/incidents.jsonl`

---

## Scenario Configuration Updates

### File Modified
- `scenarios/FM1/canary-rollback.yaml` (example)

### New Configuration Option

Added `trigger_datadog` flag to incident configuration:

```yaml
incident:
  should_create: true
  severity: high
  title: "canary rollback triggered"
  trigger_datadog: true  # NEW: Enable Datadog integration
```

### How It Works

1. Scenario YAML includes `trigger_datadog: true` in incident config
2. `run_scenario.py` extracts this flag via `extract_incident_config()`
3. Flag is passed to `incident_stub/emit.py` as `--trigger-datadog`
4. Incident stub creates Datadog incident if flag is set

### Updated Code in `run_scenario.py`

```python
# Extract Datadog trigger flag
trigger_datadog = bool(cfg.get("trigger_datadog", False)) if isinstance(cfg, dict) else False

return {
    "should_create": should_create,
    "severity": severity,
    "title": title,
    "flag_action": flag_action,
    "trigger_datadog": trigger_datadog,  # NEW
}
```

---

## Environment Variables and Configuration

### Required Environment Variables

#### For GitHub Actions

Configure these secrets in GitHub repository settings (`Settings > Secrets and variables > Actions`):

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `DD_API_KEY` | Datadog API key for test optimization | `232e10e8a5ecac4d856de7ec5e93e671` |
| `DATADOG_API_KEY` | Datadog API key for incident creation | `232e10e8a5ecac4d856de7ec5e93e671` |
| `DATADOG_APP_KEY` | Datadog Application key (requires Incident Management permissions) | `b087cc2635b598dea501d6f647c1c6354c9b7609` |

#### For Local Development

Set these environment variables in your shell:

**PowerShell (Windows)**:
```powershell
$env:DATADOG_API_KEY="232e10e8a5ecac4d856de7ec5e93e671"
$env:DATADOG_APP_KEY="b087cc2635b598dea501d6f647c1c6354c9b7609"
$env:GMAIL_NOTIFICATION_ADDRESS="your-email@gmail.com"  # Optional
```

**Bash (Linux/Mac)**:
```bash
export DATADOG_API_KEY="232e10e8a5ecac4d856de7ec5e93e671"
export DATADOG_APP_KEY="b087cc2635b598dea501d6f647c1c6354c9b7609"
export GMAIL_NOTIFICATION_ADDRESS="your-email@gmail.com"  # Optional
```

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GMAIL_NOTIFICATION_ADDRESS` | Email address for Datadog notifications | None |
| `DD_SITE` | Datadog site (if different from us5) | `us5.datadoghq.com` |

---

## Testing and Validation

### Datadog Connection Test Script

**File**: `test_datadog_connection.py`

**Purpose**: Validates Datadog API credentials and permissions before running scenarios.

**Usage**:
```bash
# Set environment variables first
$env:DATADOG_API_KEY="your-api-key"
$env:DATADOG_APP_KEY="your-app-key"

# Run test
python test_datadog_connection.py
```

**What It Tests**:
1. **API Key Validation**: Tests `/api/v1/validate` endpoint
2. **Incident Creation Permissions**: Tests `/api/v2/incidents` endpoint
3. **Helpful Error Messages**: Provides diagnostics for common issues

**Expected Output**:
```
[OK] API Key: 232e10e8a5...
[OK] App Key: b087cc2635...

[Test 1] Testing API key validation endpoint...
[SUCCESS] API key validation: HTTP 200

[Test 2] Testing incident creation endpoint permissions...
[SUCCESS] Incident creation endpoint: HTTP 400 (expected - payload validation)
  This means authentication works! The 400 is due to incomplete payload.
  Your credentials are valid and have incident creation permissions!
```

### Testing Scenario with Datadog Integration

1. **Configure scenario YAML**:
   ```yaml
   incident:
     should_create: true
     severity: high
     title: "Test incident"
     trigger_datadog: true
   ```

2. **Set environment variables**:
   ```powershell
   $env:DATADOG_API_KEY="your-api-key"
   $env:DATADOG_APP_KEY="your-app-key"
   ```

3. **Run scenario**:
   ```bash
   python harness/run_scenario.py FM1-canary-rollback
   ```

4. **Verify**:
   - Check console output for `[datadog] Incident created: {incident_id}`
   - Check `harness/_artifacts/incidents.jsonl` for incident record
   - Check Datadog UI for the incident

---

## Docker Datadog Agent Setup

### Overview

The Datadog Agent can be run as a Docker container for local monitoring and APM.

### Docker Run Command

**Full Command**:
```powershell
docker run -d --name datadog-agent --restart=unless-stopped `
  --cgroupns=host `
  -v /var/run/docker.sock:/var/run/docker.sock:ro `
  -v /proc/:/host/proc/:ro `
  -v /sys/fs/cgroup/:/host/sys/fs/cgroup:ro `
  -v /etc/passwd:/etc/passwd:ro `
  -e DD_API_KEY=232e10e8a5ecac4d856de7ec5e93e671 `
  -e DD_SITE=us5.datadoghq.com `
  -e DD_PROCESS_CONFIG_PROCESS_COLLECTION_ENABLED=true `
  -e DD_APM_ENABLED=true `
  -e DD_LOGS_ENABLED=true `
  -e DD_LOGS_CONFIG_CONTAINER_COLLECT_ALL=true `
  -e DD_CONTAINER_EXCLUDE="name:datadog-agent" `
  -p 8126:8126 `
  gcr.io/datadoghq/agent:7
```

### Configuration Breakdown

| Parameter | Purpose |
|-----------|---------|
| `--cgroupns=host` | Access to host cgroup namespace |
| `-v /var/run/docker.sock:ro` | Access to Docker daemon |
| `-v /proc/:/host/proc/:ro` | Process information |
| `-v /sys/fs/cgroup/:/host/sys/fs/cgroup:ro` | Container metrics |
| `-v /etc/passwd:/etc/passwd:ro` | User information (Linux only) |
| `-e DD_API_KEY` | Datadog API key |
| `-e DD_SITE` | Datadog site |
| `-e DD_PROCESS_CONFIG_PROCESS_COLLECTION_ENABLED=true` | Enable process collection |
| `-e DD_APM_ENABLED=true` | Enable APM (tracing) |
| `-e DD_LOGS_ENABLED=true` | Enable log collection |
| `-e DD_LOGS_CONFIG_CONTAINER_COLLECT_ALL=true` | Collect logs from all containers |
| `-e DD_CONTAINER_EXCLUDE="name:datadog-agent"` | Exclude agent's own logs |
| `-p 8126:8126` | APM trace intake port |

### Managing the Agent

**Check Status**:
```bash
docker ps --filter "name=datadog-agent"
```

**View Logs**:
```bash
docker logs datadog-agent --tail 50
```

**Stop Agent**:
```bash
docker stop datadog-agent
```

**Remove Agent**:
```bash
docker stop datadog-agent
docker rm datadog-agent
```

**Restart Agent**:
```bash
docker restart datadog-agent
```

### Note on Windows

The `/etc/passwd` mount is for Linux containers. On Windows, this mount may not be necessary or may need adjustment depending on your Docker setup (WSL2, Docker Desktop, etc.).

---

## Usage Examples

### Example 1: Run Scenario with Datadog Integration

```bash
# 1. Set environment variables
$env:DATADOG_API_KEY="232e10e8a5ecac4d856de7ec5e93e671"
$env:DATADOG_APP_KEY="b087cc2635b598dea501d6f647c1c6354c9b7609"

# 2. Run scenario
python harness/run_scenario.py FM1-canary-rollback

# 3. Check output for Datadog incident creation
# Expected: [datadog] Incident created: {incident_id}
```

### Example 2: Test Datadog Connection

```bash
# Set credentials
$env:DATADOG_API_KEY="your-api-key"
$env:DATADOG_APP_KEY="your-app-key"

# Run test
python test_datadog_connection.py
```

### Example 3: Manual Incident Creation

```bash
# Set credentials
$env:DATADOG_API_KEY="your-api-key"
$env:DATADOG_APP_KEY="your-app-key"

# Create incident manually
python harness/incident_stub/emit.py `
  --scenario-id FM1-test `
  --should-create `
  --severity high `
  --title "Manual test incident" `
  --trigger-datadog
```

### Example 4: GitHub Actions Workflow

The workflow automatically:
1. Configures Datadog Test Optimization
2. Runs tests
3. Creates Datadog incident if tests fail

No manual intervention required - just ensure secrets are configured.

---

## Troubleshooting

### Common Issues and Solutions

#### 1. HTTP 403 Forbidden When Creating Incidents

**Symptoms**:
```
[datadog] Failed: HTTP 403 Forbidden
```

**Causes**:
- Invalid or expired API key
- Invalid or expired Application key
- Application key missing "Incident Management" permissions
- Keys revoked in Datadog settings

**Solutions**:
1. Verify API key is correct: Check in Datadog UI (`Organization Settings > API Keys`)
2. Verify Application key is correct: Check in Datadog UI (`Organization Settings > Application Keys`)
3. Ensure Application key has "Incident Management" permission enabled
4. Regenerate keys if necessary

#### 2. Module Not Found Errors

**Symptoms**:
```
ModuleNotFoundError: No module named 'harness'
```

**Solutions**:
- Run from repository root: `python harness/run_scenario.py`
- Or use module syntax: `python -m harness.run_scenario`

#### 3. Datadog Test Optimization Not Working

**Symptoms**:
- No test data appearing in Datadog

**Solutions**:
1. Verify `DD_API_KEY` secret is set in GitHub repository settings
2. Check workflow logs for Datadog action errors
3. Ensure site is correct: `us5.datadoghq.com`

#### 4. Docker Agent Not Collecting Data

**Symptoms**:
- No traces/logs/metrics in Datadog

**Solutions**:
1. Check agent logs: `docker logs datadog-agent`
2. Verify API key is correct in environment variables
3. Ensure site matches your Datadog account: `DD_SITE=us5.datadoghq.com`
4. Check network connectivity: Agent needs outbound HTTPS access

#### 5. Incident Created But No Notifications

**Symptoms**:
- Incident appears in Datadog but no email/On-Call trigger

**Solutions**:
1. Configure Datadog notification rules in UI:
   - Go to `Monitors > Notifications`
   - Set up email notifications for incidents
2. Configure Datadog On-Call routing rules:
   - Go to `On-Call > Routing Rules`
   - Set up rules to trigger On-Call page for incidents
3. Verify `GMAIL_NOTIFICATION_ADDRESS` is set (optional, for logging)

### Getting Help

1. **Check Logs**: Review console output and Datadog agent logs
2. **Test Connection**: Run `test_datadog_connection.py` to validate credentials
3. **Datadog Documentation**: 
   - [Incident Management API](https://docs.datadoghq.com/api/latest/incidents/)
   - [Test Visibility](https://docs.datadoghq.com/continuous_integration/)
4. **GitHub Issues**: Check repository issues for known problems

---

## Summary of Files Changed

### Modified Files

| File | Changes |
|------|---------|
| `.github/workflows/python-tests.yml` | Added Datadog Test Optimization step and automatic incident creation |
| `harness/incident_stub/emit.py` | Added Datadog incident creation, credential validation, and enhanced record keeping |
| `harness/run_scenario.py` | Added `trigger_datadog` flag extraction and passing |
| `scenarios/FM1/canary-rollback.yaml` | Added `trigger_datadog: true` to incident configuration |

### New Files

| File | Purpose |
|------|---------|
| `test_datadog_connection.py` | Validates Datadog API credentials and permissions |

### Files Referenced (Not Created)

- `harness/report_generator.py`: Includes Datadog integration data in reports (if present)
- `harness/_artifacts/incidents.jsonl`: Stores incident records with Datadog metadata

---

## Next Steps

### Recommended Enhancements

1. **APM Integration**: Add `ddtrace` instrumentation to Python applications
2. **Custom Metrics**: Send custom metrics for scenario execution
3. **Dashboards**: Create Datadog dashboards for scenario monitoring
4. **SLOs**: Define Service Level Objectives for scenario reliability
5. **Monitors**: Set up Datadog monitors for incident rates

### Configuration Checklist

- [ ] GitHub repository secrets configured (`DD_API_KEY`, `DATADOG_API_KEY`, `DATADOG_APP_KEY`)
- [ ] Local environment variables set for development
- [ ] Datadog notification rules configured in UI
- [ ] Datadog On-Call routing rules configured in UI
- [ ] Test connection script passes validation
- [ ] At least one scenario configured with `trigger_datadog: true`
- [ ] Docker Datadog Agent running (if using local monitoring)

---

## Conclusion

This guide documents all Datadog integrations implemented in the `zeroui-scenario-lab-01` repository. The integration provides:

- **Automatic Test Visibility**: Track test execution in Datadog
- **Automatic Incident Creation**: CI failures and scenario incidents automatically create Datadog incidents
- **On-Call Integration**: Automatic On-Call page triggering via routing rules
- **Email Notifications**: Automatic Gmail notifications via notification rules
- **Comprehensive Tracking**: All incidents tracked with Datadog metadata

For questions or issues, refer to the Troubleshooting section or check Datadog documentation.

---

**Last Updated**: 2025-01-23  
**Repository**: `zeroui-scenario-lab-01`  
**Datadog Site**: `us5.datadoghq.com`

