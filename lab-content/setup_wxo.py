#!/usr/bin/env python3
"""
setup_wxo.py — One-shot watsonx Orchestrate deployment script.

Sets up the complete fraud detection solution:
  1. Creates the confluent_kafka_fraud_detection connection (key-value)
  2. Configures it with team/draft credentials from .env
  3. Imports check_lab_fraud_pattern tool        (suffixed with your initials)
  4. Imports check_doctor_referral_pattern tool  (suffixed with your initials)
  5. Imports analyze_test_necessity tool         (suffixed with your initials)
  6. Imports diagnostic_fraud_detector agent     (suffixed with your initials)

Run AFTER:
  - orchestrate env activate <env-name> --api-key <key>
  - python push_to_confluent.py  (data already in Kafka)
  - Flink INSERT jobs are Running in Confluent Cloud

Usage:
  python setup_wxo.py
"""

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from dotenv import load_dotenv
import yaml

# Resolve paths relative to THIS script's location — works regardless of
# where the participant runs the script from.
SCRIPT_DIR = Path(__file__).parent.resolve()

load_dotenv(dotenv_path=SCRIPT_DIR / '.env')


def _get_initials() -> str:
    """Prompt the participant for their initials and return a sanitised suffix."""
    print('\n' + '=' * 60)
    print('  Personalise your deployment')
    print('=' * 60)
    print('  Each participant deploys their own named agent and tools.')
    print('  Enter your initials so your artifacts are unique in the')
    print('  shared watsonx Orchestrate environment.')
    print()
    while True:
        raw = input('  Enter your initials (e.g. poojah): ').strip()
        if not raw:
            print('  ⚠️  Initials cannot be empty. Please try again.')
            continue
        # Allow only letters, digits, and underscores
        sanitised = re.sub(r'[^a-zA-Z0-9]', '', raw).lower()
        if not sanitised:
            print('  ⚠️  Initials must contain at least one letter or digit.')
            continue
        confirm = input(f'  Your artifacts will be named with suffix "_{sanitised}" — confirm? [Y/n]: ').strip().lower()
        if confirm in ('', 'y', 'yes'):
            return sanitised
        print('  Re-entering initials...')


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


def cleanup_previous(agent_name: str, tool_names: list[str]) -> None:
    """Remove previously deployed artifacts for these initials (best-effort, ignore errors)."""
    print(f'\n  🧹 Cleaning up any previous deployment for these initials...')
    for tool in tool_names:
        result = subprocess.run(
            ['orchestrate', 'tools', 'remove', '-n', tool],
            capture_output=True, text=True
        )
        combined = (result.stdout + result.stderr).lower()
        if 'not found' in combined or 'does not exist' in combined or 'no tool' in combined:
            print(f'   ℹ️  Tool not found (skipping): {tool}')
        else:
            print(f'   🗑️  Removed tool: {tool}')

    result = subprocess.run(
        ['orchestrate', 'agents', 'remove', '-n', agent_name, '-k', 'native'],
        capture_output=True, text=True
    )
    combined = (result.stdout + result.stderr).lower()
    if 'not found' in combined or 'does not exist' in combined or 'no agent' in combined:
        print(f'   ℹ️  Agent not found (skipping): {agent_name}')
    else:
        print(f'   🗑️  Removed agent: {agent_name}')


def _build_tool_py(source_py: str, original_name: str, suffixed_name: str) -> str:
    """
    Copy a tool .py file, replacing the @tool(name="<original>") decorator
    value with <suffixed_name>. Returns the temp file path.
    The caller is responsible for deleting the file after use.
    """
    src = Path(source_py).read_text()
    # Replace the name= value inside @tool(...) — handles single or double quotes
    patched = re.sub(
        rf'(name\s*=\s*["\']){re.escape(original_name)}(["\'])',
        rf'\g<1>{suffixed_name}\2',
        src,
        count=1,
    )
    tmp = tempfile.NamedTemporaryFile(
        mode='w', suffix='.py', delete=False, prefix=f'{suffixed_name}_'
    )
    tmp.write(patched)
    tmp.flush()
    tmp.close()
    return tmp.name


def _build_agent_yaml(source_yaml: str, initials: str) -> str:
    """
    Load the agent YAML, prefix the agent name with initials and suffix
    all tool references, write to a named temp file, return the temp path.
    The caller is responsible for deleting the file after use.
    """
    with open(source_yaml) as fh:
        data = yaml.safe_load(fh)

    data['name'] = f"{initials}_{data['name']}"          # prefix for agent
    data['tools'] = [f"{t}_{initials}" for t in data.get('tools', [])]  # suffix for tools

    tmp = tempfile.NamedTemporaryFile(
        mode='w', suffix='.yaml', delete=False, prefix='diag_fraud_agent_'
    )
    yaml.dump(data, tmp, allow_unicode=True, sort_keys=False)
    tmp.flush()
    tmp.close()
    return tmp.name


def main():
    print('=' * 60)
    print('  watsonx Orchestrate — Fraud Detection Setup')
    print('=' * 60)

    # ── Ask participant for their initials ───────────────────────────────────
    initials = _get_initials()

    # ── Derive artifact names (agent: prefix, tools: suffix) ─────────────────
    agent_name   = f'{initials}_diagnostic_fraud_detector'
    tool_lab     = f'check_lab_fraud_pattern_{initials}'
    tool_doctor  = f'check_doctor_referral_pattern_{initials}'
    tool_test    = f'analyze_test_necessity_{initials}'

    print(f'\n  🏷️  Deploying as:')
    print(f'     Agent : {agent_name}')
    print(f'     Tools : {tool_lab}')
    print(f'             {tool_doctor}')
    print(f'             {tool_test}')

    # ── Clean up any previous deployment for these initials ──────────────────
    cleanup_previous(agent_name, [tool_lab, tool_doctor, tool_test])

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
    tmp_lab = _build_tool_py(
        f'{tools_dir}/check_lab_fraud_pattern.py',
        'check_lab_fraud_pattern', tool_lab
    )
    try:
        ok = run(
            [
                'orchestrate', 'tools', 'import',
                '-k', 'python',
                '-f', tmp_lab,
                '--requirements-file', requirements,
                '--app-id', app_id,
            ],
            f'Step 3a/5 — Import tool: {tool_lab}'
        )
    finally:
        Path(tmp_lab).unlink(missing_ok=True)
    if not ok:
        print('\n❌ Aborting.')
        sys.exit(1)

    # ── Step 3b: Import check_doctor_referral_pattern tool ───────────────────
    tmp_doctor = _build_tool_py(
        f'{tools_dir}/check_doctor_referral_pattern.py',
        'check_doctor_referral_pattern', tool_doctor
    )
    try:
        ok = run(
            [
                'orchestrate', 'tools', 'import',
                '-k', 'python',
                '-f', tmp_doctor,
                '--requirements-file', requirements,
                '--app-id', app_id,
            ],
            f'Step 3b/5 — Import tool: {tool_doctor}'
        )
    finally:
        Path(tmp_doctor).unlink(missing_ok=True)
    if not ok:
        print('\n❌ Aborting.')
        sys.exit(1)

    # ── Step 3c: Import analyze_test_necessity tool ───────────────────────────
    tmp_test = _build_tool_py(
        f'{tools_dir}/analyze_test_necessity.py',
        'analyze_test_necessity', tool_test
    )
    try:
        ok = run(
            [
                'orchestrate', 'tools', 'import',
                '-k', 'python',
                '-f', tmp_test,
                '--requirements-file', requirements,
                '--app-id', app_id,
            ],
            f'Step 3c/5 — Import tool: {tool_test}'
        )
    finally:
        Path(tmp_test).unlink(missing_ok=True)
    if not ok:
        print('\n❌ Aborting.')
        sys.exit(1)

    # ── Step 4: Import agent (using a temp YAML with suffixed names) ──────────
    tmp_agent_yaml = _build_agent_yaml(
        f'{agents_dir}/diagnostic_fraud_detector.yaml', initials
    )
    try:
        ok = run(
            [
                'orchestrate', 'agents', 'import',
                '-f', tmp_agent_yaml,
            ],
            f'Step 4/5 — Import agent: {agent_name}'
        )
    finally:
        Path(tmp_agent_yaml).unlink(missing_ok=True)  # always clean up temp file

    if not ok:
        print('\n❌ Aborting.')
        sys.exit(1)

    # ── Summary ──────────────────────────────────────────────────────────────
    print('\n' + '=' * 60)
    print('  ✅ Setup complete!')
    print('=' * 60)
    print(f"""
Next steps:
  1. Open watsonx Orchestrate UI
  2. Find agent : {agent_name}   ← sorted by your initials in the UI
  3. Test with  : "Is Quick Lab Diagnostics trustworthy?"
  4. Test with  : "Check Dr. Vinod Mehta's referral pattern"

Or verify from CLI:
  orchestrate connections list
  orchestrate tools list
  orchestrate agents list
""")


if __name__ == '__main__':
    main()
