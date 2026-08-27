"""
check_topics.py — Verify reports.raw topic exists in Confluent Cloud.

reports.raw is the only topic you need to create manually in the
Confluent Cloud UI. The sink topics (labs_patterns, doctors_patterns)
are created automatically by the Flink SQL CREATE TABLE statements.

Run: python check_topics.py
Credentials are loaded from .env in the same directory.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from confluent_kafka.admin import AdminClient

SCRIPT_DIR = Path(__file__).parent.resolve()
load_dotenv(dotenv_path=SCRIPT_DIR / '.env')

cfg = {
    'bootstrap.servers': os.getenv('BOOTSTRAP_SERVERS'),
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms':   'PLAIN',
    'sasl.username':     os.getenv('SASL_USERNAME'),
    'sasl.password':     os.getenv('SASL_PASSWORD'),
}

admin = AdminClient(cfg)
existing = admin.list_topics(timeout=10).topics

print('📋 Verifying reports.raw topic...\n')

if 'reports.raw' in existing:
    partitions = len(existing['reports.raw'].partitions)
    print(f'   ✅ reports.raw — exists ({partitions} partitions)')
    print('\n✅ Ready.')
    print('   Next step: run Flink SQL cells 1–6 in Confluent Cloud.')
else:
    print('   ❌ reports.raw — NOT FOUND')
    print('\n⚠️  Create it first:')
    print('   → Confluent Cloud → Topics → Add topic')
    print('   → Name: reports.raw  |  Partitions: 3  |  Default settings')
    sys.exit(1)
