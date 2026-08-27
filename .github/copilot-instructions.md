# GitHub Copilot Instructions — Fraud Detection Lab

## Project Overview
This is an IBM TechXchange 2026 lab repository for "Real-Time Diagnostic Fraud Detection
with Event-Driven Agentic AI" using Confluent Cloud, Apache Flink SQL, and IBM watsonx Orchestrate.

## Architecture
```
reports.raw (Kafka/Avro)
      ↓  Apache Flink SQL streaming aggregation
labs_patterns + doctors_patterns (Kafka/Avro)
      ↓  IBM watsonx Orchestrate tools read these topics
diagnostic_fraud_detector agent answers patient queries
```

## Key Files
- `lab-content/push_to_confluent.py` — pushes Avro data to Kafka
- `lab-content/setup_wxo.py` — deploys connection, tools, agent to watsonx Orchestrate
- `lab-content/tools/` — Python tools imported into watsonx Orchestrate
- `lab-content/flink_statements/` — Flink SQL pipeline statements

## Coding Standards
- All credentials loaded from `.env` via `python-dotenv` — never hardcoded
- Avro format for all three Kafka topics (reports.raw, labs_patterns, doctors_patterns)
- Flink SQL: one statement per cell in Confluent Cloud SQL Workspaces
- watsonx Orchestrate tools use `connections.key_value('confluent_kafka_fraud_detection')`

## Fraud Detection Thresholds
- Sink Test Fraud: lab normal_count/total_reports > 85%
- Kickback Fraud: doctor referral concentration to one lab > 80%
- Over-testing: test count exceeds medical guidelines per symptom
