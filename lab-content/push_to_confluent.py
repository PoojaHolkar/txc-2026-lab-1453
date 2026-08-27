"""
Push all 50 sample reports to Confluent Kafka as Avro messages.

Topic:  reports.raw
Format: Avro (key = report_id string, value = DiagnosticReport record)

IMPORTANT — correct order of operations:
  1. Run Flink SQL cells 1–4 (CREATE TABLE for sink topics)
  2. Run Flink SQL cells 5–6 (INSERT INTO jobs) — wait for 'Running' status
  3. Run this script — Flink jobs are already watching and will process all 50 messages

The schema is registered in Schema Registry on first run.
If Schema Registry already has an incompatible schema for 'reports.raw-value',
this script deletes it first so it can register the correct DiagnosticReport schema.

Run: python push_to_confluent.py
Credentials are loaded from a .env file in the same directory.
"""

import json
import os
import sys
from pathlib import Path

import requests
from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import SerializationContext, MessageField
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).parent.resolve()
load_dotenv(dotenv_path=SCRIPT_DIR / '.env')


def _require(key: str) -> str:
    val = os.getenv(key)
    if not val:
        print(f'❌ Missing required environment variable: {key}')
        print('   Copy .env.example → .env and fill in your Confluent credentials.')
        sys.exit(1)
    return val


KAFKA_CONFIG = {
    'bootstrap.servers': _require('BOOTSTRAP_SERVERS'),
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms':   'PLAIN',
    'sasl.username':     _require('SASL_USERNAME'),
    'sasl.password':     _require('SASL_PASSWORD'),
}

SR_URL    = _require('SCHEMA_REGISTRY_URL')
SR_KEY    = _require('SCHEMA_REGISTRY_KEY')
SR_SECRET = _require('SCHEMA_REGISTRY_SECRET')

SCHEMA_REGISTRY_CONFIG = {
    'url': SR_URL,
    'basic.auth.user.info': f'{SR_KEY}:{SR_SECRET}',
}

TOPIC = 'reports.raw'
SUBJECT = 'reports.raw-value'

# ── Avro schema — must match the Flink table definition ─────────────────────
REPORTS_VALUE_SCHEMA = json.dumps({
    "type": "record",
    "name": "DiagnosticReport",
    "namespace": "com.fraud.detection",
    "fields": [
        {"name": "report_id",   "type": "string"},
        {"name": "uploaded_at", "type": "string"},
        {
            "name": "lab",
            "type": {
                "type": "record", "name": "Lab",
                "fields": [
                    {"name": "name",            "type": "string"},
                    {"name": "city",            "type": "string"},
                    {"name": "nabl_accredited", "type": "boolean"}
                ]
            }
        },
        {
            "name": "referring_doctor",
            "type": {
                "type": "record", "name": "Doctor",
                "fields": [
                    {"name": "name",                "type": "string"},
                    {"name": "registration_number", "type": "string"}
                ]
            }
        },
        {
            "name": "patient",
            "type": {
                "type": "record", "name": "Patient",
                "fields": [
                    {"name": "age",    "type": "int"},
                    {"name": "gender", "type": "string"}
                ]
            }
        },
        {"name": "all_values_normal", "type": "boolean"},
        {"name": "test_count",        "type": "int"},
        {"name": "amount_paid",       "type": "double"},
        {"name": "fraud_label",       "type": "string"}
    ]
})


def ensure_schema_registered() -> int:
    """
    Ensure the DiagnosticReport schema is in Schema Registry.
    If an incompatible schema exists (e.g. old placeholder), delete it first.
    Returns the registered schema ID.
    """
    auth = (SR_KEY, SR_SECRET)

    # Check what's currently registered
    r = requests.get(f'{SR_URL}/subjects/{SUBJECT}/versions/latest', auth=auth)

    if r.status_code == 200:
        existing = r.json()
        if 'DiagnosticReport' in existing.get('schema', ''):
            schema_id = existing['id']
            print(f'  ✅ DiagnosticReport schema already registered (id={schema_id})')
            return schema_id
        else:
            # Incompatible schema — hard delete it
            print(f'  🗑️  Incompatible schema found — deleting subject "{SUBJECT}"...')
            requests.delete(f'{SR_URL}/subjects/{SUBJECT}', auth=auth)
            requests.delete(f'{SR_URL}/subjects/{SUBJECT}?permanent=true', auth=auth)
            print(f'  ✅ Deleted old subject')

    # Register the new schema
    payload = {"schema": REPORTS_VALUE_SCHEMA, "schemaType": "AVRO"}
    r = requests.post(
        f'{SR_URL}/subjects/{SUBJECT}/versions',
        auth=auth,
        headers={'Content-Type': 'application/vnd.schemaregistry.v1+json'},
        json=payload
    )
    if r.status_code in (200, 201):
        schema_id = r.json()['id']
        print(f'  ✅ DiagnosticReport schema registered (id={schema_id})')
        return schema_id
    else:
        print(f'  ❌ Failed to register schema: {r.status_code} {r.text}')
        sys.exit(1)


def delivery_report(err, msg):
    if err:
        print(f'  ❌ Failed: {err}')
    else:
        print(f'  ✅ Sent → partition={msg.partition()} offset={msg.offset()} key={msg.key().decode()}')


def main():
    with open(SCRIPT_DIR / 'sample-reports-50.json', 'r') as f:
        data = json.load(f)

    reports = data['reports']
    print(f'📊 Loaded {len(reports)} reports from sample-reports-50.json')

    # ── Step 1: Ensure schema is registered ─────────────────────────────────
    print(f'\n🔍 Checking Schema Registry...')
    ensure_schema_registered()

    # ── Step 2: Push all reports as Avro ────────────────────────────────────
    print(f'\n🔗 Connecting to Kafka...')
    schema_registry_client = SchemaRegistryClient(SCHEMA_REGISTRY_CONFIG)
    value_serializer = AvroSerializer(schema_registry_client, REPORTS_VALUE_SCHEMA)
    producer = Producer(KAFKA_CONFIG)

    print(f'\n📤 Pushing {len(reports)} reports → {TOPIC} (Avro)')
    print('-' * 50)

    for report in reports:
        value_bytes = value_serializer(
            report,
            SerializationContext(TOPIC, MessageField.VALUE)
        )
        producer.produce(
            topic=TOPIC,
            key=report['report_id'].encode('utf-8'),
            value=value_bytes,
            callback=delivery_report
        )
        producer.poll(0)

    producer.flush()

    print('-' * 50)
    print(f'✅ Done! {len(reports)} Avro-encoded reports pushed to {TOPIC}.')
    print(f'   The Flink INSERT jobs will process them within seconds.')


if __name__ == '__main__':
    main()
