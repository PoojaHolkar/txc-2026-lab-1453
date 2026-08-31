-- ============================================================
-- Flink SQL: Complete Real-time Fraud Detection Pipeline
-- Run these statements ONE AT A TIME in Confluent Cloud
-- → Environments → default → Flink → SQL Workspaces
-- ============================================================
--
-- ⚠️  CRITICAL ORDER OF OPERATIONS — do NOT change this order:
--
--   STEP 1: python push_to_confluent.py
--           → pushes 50 Avro reports into reports.raw FIRST
--
--   STEP 2: Run Statements 1–4 below (CREATE TABLE for sinks)
--
--   STEP 3: Run Statements 5–6 below (INSERT INTO jobs)
--           → Flink resets to earliest offset and processes
--             all 50 messages already in reports.raw
--
-- WHY ORDER MATTERS:
--   If you start the INSERT INTO jobs (Step 3) BEFORE pushing
--   data (Step 1), Flink commits its starting offset as "now"
--   and will never backfill the messages pushed afterwards.
--   labs_patterns and doctors_patterns will stay empty.
--
-- Pipeline:
--   reports.raw  (auto-discovered Kafka/Avro source topic)
--        ↓  Flink aggregates in real-time
--   labs_patterns    → check_lab_fraud_pattern tool
--   doctors_patterns → check_doctor_referral_pattern tool
-- ============================================================


-- ============================================================
-- STATEMENT 1 (in its own cell): Drop labs_patterns if exists
-- ============================================================

DROP TABLE IF EXISTS `labs_patterns`;


-- ============================================================
-- STATEMENT 2 (in its own cell): Create labs_patterns sink
--
-- PRIMARY KEY is required because GROUP BY produces upsert
-- changes. Without it Flink throws:
-- "Table sink doesn't support consuming update changes"
-- ============================================================

CREATE TABLE `labs_patterns` (
    lab_name        STRING,
    total_reports   BIGINT NOT NULL,
    normal_count    BIGINT NOT NULL,
    PRIMARY KEY (lab_name) NOT ENFORCED
) DISTRIBUTED BY HASH(lab_name) INTO 3 BUCKETS;


-- ============================================================
-- STATEMENT 3 (in its own cell): Drop doctors_patterns if exists
-- ============================================================

DROP TABLE IF EXISTS `doctors_patterns`;


-- ============================================================
-- STATEMENT 4 (in its own cell): Create doctors_patterns sink
-- ============================================================

CREATE TABLE `doctors_patterns` (
    doctor_name     STRING,
    lab_name        STRING,
    referral_count  BIGINT NOT NULL,
    PRIMARY KEY (doctor_name, lab_name) NOT ENFORCED
) DISTRIBUTED BY HASH(doctor_name, lab_name) INTO 3 BUCKETS;


-- ============================================================
-- STATEMENT 5 (in its own cell): Start lab fraud pattern job
--
-- Reads reports.raw (auto-discovered by Flink from Kafka),
-- aggregates per lab, writes running totals to labs_patterns.
-- ============================================================

INSERT INTO `labs_patterns`
SELECT
    lab.`name`                                                AS lab_name,
    COUNT(*)                                                  AS total_reports,
    SUM(CASE WHEN all_values_normal = TRUE THEN 1 ELSE 0 END) AS normal_count
FROM `reports.raw`
GROUP BY lab.`name`;


-- ============================================================
-- STATEMENT 6 (in its own cell): Start doctor kickback job
-- ============================================================

INSERT INTO `doctors_patterns`
SELECT
    referring_doctor.`name`   AS doctor_name,
    lab.`name`                AS lab_name,
    COUNT(*)                  AS referral_count
FROM `reports.raw`
GROUP BY referring_doctor.`name`, lab.`name`;
