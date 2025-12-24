#!/usr/bin/env python3
"""
Test script to validate Datadog API connection.
Handles 403 errors gracefully and provides helpful diagnostics.
"""
import os
import sys

import requests


def test_datadog_connection():
    """Test Datadog API connection with helpful error messages."""
    api_key = os.getenv("DATADOG_API_KEY")
    app_key = os.getenv("DATADOG_APP_KEY")
    
    if not api_key:
        print("[ERROR] DATADOG_API_KEY not set")
        print("   Set it with: $env:DATADOG_API_KEY='your-api-key'")
        return False
    
    if not app_key:
        print("[ERROR] DATADOG_APP_KEY not set")
        print("   Set it with: $env:DATADOG_APP_KEY='your-app-key'")
        return False
    
    print(f"[OK] API Key: {api_key[:10]}...")
    print(f"[OK] App Key: {app_key[:10]}...")
    print()
    
    # Test 1: API Key validation endpoint
    print("[Test 1] Testing API key validation endpoint...")
    try:
        url = "https://api.datadoghq.com/api/v1/validate"
        headers = {"DD-API-KEY": api_key}
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            print(f"[SUCCESS] API key validation: HTTP {response.status_code}")
            print(f"  Response: {response.text}")
        elif response.status_code == 403:
            print(f"[WARNING] API key validation: HTTP 403 Forbidden")
            print(f"  This may indicate:")
            print(f"  - API key is invalid or expired")
            print(f"  - API key doesn't have validation endpoint permissions")
            print(f"  - Some Datadog accounts restrict this endpoint")
            print(f"  Note: Incident creation may still work even if validation fails")
        else:
            print(f"[WARNING] API key validation: HTTP {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as exc:
        print(f"[ERROR] API key validation failed: {exc}")
    
    print()
    
    # Test 2: Try incident creation endpoint (more reliable test)
    print("[Test 2] Testing incident creation endpoint permissions...")
    try:
        url = "https://api.datadoghq.com/api/v2/incidents"
        headers = {
            "DD-API-KEY": api_key,
            "DD-APPLICATION-KEY": app_key,
            "Content-Type": "application/json",
        }
        # Try a minimal test payload (will fail validation but shows if auth works)
        payload = {
            "data": {
                "type": "incidents",
                "attributes": {
                    "title": "Test Connection",
                    "severity": "SEV-4",
                }
            }
        }
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code in (200, 201):
            print(f"[SUCCESS] Incident creation endpoint: HTTP {response.status_code}")
            print(f"  Your credentials are valid and have incident creation permissions!")
            return True
        elif response.status_code == 403:
            print(f"[ERROR] Incident creation endpoint: HTTP 403 Forbidden")
            print(f"  Error: {response.text}")
            print(f"  This indicates:")
            print(f"  1. API key or Application key is invalid/expired")
            print(f"  2. Application key doesn't have 'Incident Management' permissions")
            print(f"  3. Keys may be revoked in Datadog settings")
            print(f"  Action: Check your Datadog account settings and key permissions")
            return False
        elif response.status_code == 400:
            print(f"[SUCCESS] Incident creation endpoint: HTTP 400 (expected - payload validation)")
            print(f"  This means authentication works! The 400 is due to incomplete payload.")
            print(f"  Your credentials are valid and have incident creation permissions!")
            return True
        else:
            print(f"[WARNING] Incident creation endpoint: HTTP {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as exc:
        print(f"[ERROR] Incident creation endpoint test failed: {exc}")
        return False


if __name__ == "__main__":
    success = test_datadog_connection()
    sys.exit(0 if success else 1)

