#!/usr/bin/env python3
"""
setup_wxo.py — One-shot watsonx Orchestrate deployment script.

Sets up the complete fraud detection solution:
  1. Creates the confluent_kafka_fraud_detection connection (key-value)
  2. Configures it with team/draft credentials from .env
  3. Imports check_lab_fraud_pattern tool
  4. Imports check_doctor_referral_pattern tool
  5. Imports diagnostic_fraud_detector agent

Run AFTER:
  - orchestrate env activate <env-name> --api-key <key>
  - python push_to_confluent.py  (data already in Kafka)
  - Flink INSERT jobs are Running in Confluent Cloud

Usage:
  python setup_wxo.py
"""

import os
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv

# Resolve paths relative to THIS script's location — works regardless of
# where the participant runs the script from.
SCRIPT_DIR = Path(__file__).parent.resolve()

load_dotenv(dotenv_path=SCRIPT_DIR / '.env')


def _require(key: str) -> str:
    val = os.getenv(key)
    if not val:
        print(f'❌ Missing .env variable: {key}')
        sys.exit(1)
    return val


def run(cmd: list[str], label: str) -> bool:
    """Run a CLI command, print output, return True on success."""
    print(f'\n▶  {label}')
    print(f'   $ {" ".join(cmd)}')
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout.strip():
        for line in result.stdout.strip().splitlines():
            print(f'   {line}')
    if result.returncode != 0:
        err = result.stderr.strip() or result.stdout.strip()
        # Treat "already exists" as success
        if 'already exists' in err.lower() or 'already exists' in result.stdout.lower():
            print(f'   ℹ️  Already exists — skipping')
            return True
        print(f'   ❌ Failed: {err}')
        return False
    print(f'   ✅ Done')
    return True


def main():
    print('=' * 60)
    print('  watsonx Orchestrate — Fraud Detection Setup')
    print('=' * 60)

    # ── Read credentials from .env ───────────────────────────────────────────
    bootstrap   = _require('BOOTSTRAP_SERVERS')
    sasl_user   = _require('SASL_USERNAME')
    sasl_pass   = _require('SASL_PASSWORD')
    sr_url      = _require('SCHEMA_REGISTRY_URL')
    sr_key      = _require('SCHEMA_REGISTRY_KEY')
    sr_secret   = _require('SCHEMA_REGISTRY_SECRET')

    app_id       = 'confluent_kafka_fraud_detection'
    tools_dir    = str(SCRIPT_DIR / 'tools')
    agents_dir   = str(SCRIPT_DIR / 'agents')
    conn_yaml    = str(SCRIPT_DIR / 'connections' / 'confluent_kafka_connection.yaml')
    requirements = str(SCRIPT_DIR / 'tools' / 'requirements.txt')

    # ── Step 1: Import connection from YAML ──────────────────────────────────
    # connections/confluent_kafka_connection.yaml defines app_id, kind=key_value,
    # type=team for both draft and live. Credentials are set separately (Step 2)
    # because the YAML must never contain secrets.
    ok = run(
        ['orchestrate', 'connections', 'import', '-f', conn_yaml],
        'Step 1/5 — Import connection: confluent_kafka_fraud_detection'
    )
    if not ok:
        print('\n❌ Aborting.')
        sys.exit(1)

    # ── Step 2: Set credentials ──────────────────────────────────────────────
    ok = run(
        [
            'orchestrate', 'connections', 'set-credentials',
            '--app-id', app_id,
            '--environment', 'draft',
            '-e', f'BOOTSTRAP_SERVERS={bootstrap}',
            '-e', f'SASL_USERNAME={sasl_user}',
            '-e', f'SASL_PASSWORD={sasl_pass}',
            '-e', f'SCHEMA_REGISTRY_URL={sr_url}',
            '-e', f'SCHEMA_REGISTRY_KEY={sr_key}',
            '-e', f'SCHEMA_REGISTRY_SECRET={sr_secret}',
        ],
        'Step 2/5 — Set Confluent credentials on connection'
    )
    if not ok:
        print('\n❌ Aborting.')
        sys.exit(1)

    # ── Step 3a: Import check_lab_fraud_pattern tool ─────────────────────────
    ok = run(
        [
            'orchestrate', 'tools', 'import',
            '-k', 'python',
            '-f', f'{tools_dir}/check_lab_fraud_pattern.py',
            '--requirements-file', requirements,
            '--app-id', app_id,
        ],
        'Step 3a/5 — Import tool: check_lab_fraud_pattern'
    )
    if not ok:
        print('\n❌ Aborting.')
        sys.exit(1)

    # ── Step 3b: Import check_doctor_referral_pattern tool ───────────────────
    ok = run(
        [
            'orchestrate', 'tools', 'import',
            '-k', 'python',
            '-f', f'{tools_dir}/check_doctor_referral_pattern.py',
            '--requirements-file', requirements,
            '--app-id', app_id,
        ],
        'Step 3b/5 — Import tool: check_doctor_referral_pattern'
    )
    if not ok:
        print('\n❌ Aborting.')
        sys.exit(1)

    # ── Step 3c: Import analyze_test_necessity tool ───────────────────────────
    ok = run(
        [
            'orchestrate', 'tools', 'import',
            '-k', 'python',
            '-f', f'{tools_dir}/analyze_test_necessity.py',
            '--requirements-file', requirements,
            '--app-id', app_id,
        ],
        'Step 3c/5 — Import tool: analyze_test_necessity'
    )
    if not ok:
        print('\n❌ Aborting.')
        sys.exit(1)

    # ── Step 4: Import agent ─────────────────────────────────────────────────
    ok = run(
        [
            'orchestrate', 'agents', 'import',
            '-f', f'{agents_dir}/diagnostic_fraud_detector.yaml',
        ],
        'Step 4/5 — Import agent: diagnostic_fraud_detector'
    )
    if not ok:
        print('\n❌ Aborting.')
        sys.exit(1)

    # ── Summary ──────────────────────────────────────────────────────────────
    print('\n' + '=' * 60)
    print('  ✅ Setup complete!')
    print('=' * 60)
    print("""
Next steps:
  1. Open watsonx Orchestrate UI
  2. Find agent: diagnostic_fraud_detector
  3. Test with: "Is Quick Lab Diagnostics trustworthy?"
  4. Test with: "Check Dr. Vinod Mehta's referral pattern"

Or verify from CLI:
  orchestrate connections list
  orchestrate tools list
  orchestrate agents list
""")


if __name__ == '__main__':
    main()
