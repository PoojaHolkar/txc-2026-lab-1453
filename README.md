# Real-Time Diagnostic Fraud Detection with Event-Driven Agentic AI
### IBM TechXchange 2026 — Hands-On Lab

---

## Problem Statement

Diagnostic lab fraud is a growing crisis in India's healthcare system. Labs produce fake "all-normal" reports without running real tests (**sink test fraud**), doctors receive financial kickbacks for steering patients to specific labs (**referral fraud**), and patients are billed for medically unnecessary tests (**over-testing fraud**). These practices drain insurance funds, harm patients, and are nearly impossible to catch manually at scale.

## What We Are Building

An event-driven AI system that detects these fraud patterns **in real time** — the moment a new diagnostic report arrives:

- **Confluent Kafka** streams every report as it is submitted
- **Apache Flink SQL** continuously aggregates fraud signals across all labs and doctors
- **IBM watsonx Orchestrate** runs an AI agent that any patient, insurer, or regulator can query in plain language to instantly surface fraud alerts

A patient can ask: *"Is Quick Lab Diagnostics trustworthy?"* and receive a fraud verdict backed by live streaming data — not a static database query, not a batch report that's days old.

---

## Lab Guide

The full step-by-step setup instructions are in [`lab-content/`](lab-content/).

Start here → [`lab-content/.env.example`](lab-content/.env.example)
