from ibm_watsonx_orchestrate.agent_builder.tools import tool
from ibm_watsonx_orchestrate.agent_builder.connections import ConnectionType
from ibm_watsonx_orchestrate.run import connections
from confluent_kafka import Consumer, KafkaError
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField
import json
import time
from typing import Optional

APP_ID = 'confluent_kafka_fraud_detection'

@tool(
    name="check_lab_fraud_pattern",
    description="Checks if a diagnostic lab has suspicious fraud patterns by analyzing their test report history. Use this when a patient asks about lab trustworthiness or wants to verify if a lab report is genuine. Detects 'Sink Test' fraud where labs produce >85% 'all normal' reports to appear legitimate while providing fake results.",
    expected_credentials=[
        {"app_id": APP_ID, "type": ConnectionType.KEY_VALUE}
    ]
)
def check_lab_fraud_pattern(lab_name: str) -> str:
    """Analyzes fraud patterns for a specific diagnostic lab by reading from Kafka topic.
    
    This tool connects to Confluent Kafka and reads the labs_patterns topic to check
    if the specified lab has suspicious patterns indicating potential fraud.
    
    Fraud Detection Logic:
    - Sink Test Fraud: If normal_count/total_reports > 85%, the lab is flagged
    - This indicates the lab is producing mostly "all normal" reports to appear legitimate
    
    Args:
        lab_name (str): The name of the diagnostic lab to check (e.g., "Quick Lab Diagnostics", "Speedy Path Lab")
    
    Returns:
        str: A detailed analysis including:
            - Lab name and fraud status
            - Total reports analyzed
            - Percentage of normal reports
            - Fraud risk assessment
            - Estimated financial impact if fraud detected
            - Recommendations for the patient
    """
    
    try:
        # Get Kafka credentials from connection
        conn = connections.key_value(APP_ID)
        bootstrap_servers = conn.get("BOOTSTRAP_SERVERS") or conn.get("bootstrap.servers")
        sasl_username = conn.get("SASL_USERNAME") or conn.get("sasl.username")
        sasl_password = conn.get("SASL_PASSWORD") or conn.get("sasl.password")
        schema_registry_url = conn.get("SCHEMA_REGISTRY_URL") or conn.get("schema.registry.url")
        schema_registry_key = conn.get("SCHEMA_REGISTRY_KEY") or conn.get("schema.registry.key")
        schema_registry_secret = conn.get("SCHEMA_REGISTRY_SECRET") or conn.get("schema.registry.secret")
        
        # Validate required credentials
        if not bootstrap_servers or not sasl_username or not sasl_password:
            return f"❌ **Configuration Error**\n\nKafka credentials are not properly configured. Please contact support.\n\nMissing: {', '.join([k for k, v in [('bootstrap_servers', bootstrap_servers), ('sasl_username', sasl_username), ('sasl_password', sasl_password)] if not v])}"
        
        if not schema_registry_url or not schema_registry_key or not schema_registry_secret:
            return f"❌ **Configuration Error**\n\nSchema Registry credentials are not properly configured. Please contact support.\n\nMissing: {', '.join([k for k, v in [('schema_registry_url', schema_registry_url), ('schema_registry_key', schema_registry_key), ('schema_registry_secret', schema_registry_secret)] if not v])}"
        
        # Configure Schema Registry client
        schema_registry_conf = {
            'url': schema_registry_url,
            'basic.auth.user.info': f'{schema_registry_key}:{schema_registry_secret}'
        }
        schema_registry_client = SchemaRegistryClient(schema_registry_conf)
        
        # Configure Kafka consumer with unique group ID to read from beginning
        consumer_config = {
            'bootstrap.servers': bootstrap_servers,
            'security.protocol': 'SASL_SSL',
            'sasl.mechanisms': 'PLAIN',
            'sasl.username': sasl_username,
            'sasl.password': sasl_password,
            'group.id': f'fraud-detection-lab-{int(time.time())}',  # Unique group ID
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False
        }
        
        consumer = Consumer(consumer_config)
        avro_deserializer = AvroDeserializer(schema_registry_client)

        # Manually assign ALL partitions so we read every partition to EOF
        topic_meta = consumer.list_topics('labs_patterns', timeout=10)
        partitions = [
            __import__('confluent_kafka').TopicPartition('labs_patterns', p)
            for p in topic_meta.topics['labs_patterns'].partitions
        ]
        consumer.assign(partitions)

        # Read until all partitions hit EOF or timeout
        lab_data = None
        max_messages = 500
        message_count = 0
        timeout_seconds = 15
        start_time = time.time()
        eof_partitions = set()
        debug_seen = []  # collect raw key samples for diagnostics

        while message_count < max_messages and (time.time() - start_time) < timeout_seconds:
            if len(eof_partitions) == len(partitions):
                break  # all partitions exhausted

            msg = consumer.poll(timeout=1.0)

            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    eof_partitions.add(msg.partition())
                    continue
                else:
                    raise Exception(f"Kafka error: {msg.error()}")

            message_count += 1

            # Deserialize key: try Avro first, fall back to plain UTF-8 string
            key_ctx = SerializationContext('labs_patterns', MessageField.KEY)
            value_ctx = SerializationContext('labs_patterns', MessageField.VALUE)

            found_lab_name = ''
            value_data = {}

            # --- Key decode ---
            try:
                key_decoded = avro_deserializer(msg.key(), key_ctx) if msg.key() else None
                if isinstance(key_decoded, dict):
                    found_lab_name = key_decoded.get('lab_name', '')
                elif isinstance(key_decoded, str):
                    found_lab_name = key_decoded
                else:
                    # Avro returned something unexpected — fall back to raw bytes
                    found_lab_name = msg.key().decode('utf-8', errors='replace') if msg.key() else ''
            except Exception:
                # Flink writes primary-key as plain UTF-8, not Avro-wrapped
                found_lab_name = msg.key().decode('utf-8', errors='replace') if msg.key() else ''

            # --- Value decode ---
            try:
                value_data = avro_deserializer(msg.value(), value_ctx) or {}
            except Exception:
                pass  # value decode failed; skip this message

            # Collect up to 5 key samples for diagnostics
            if len(debug_seen) < 5:
                debug_seen.append(repr(found_lab_name))

            # Normalize: lowercase + strip periods/extra spaces for fuzzy match
            def normalize(name):
                return name.lower().replace('.', '').replace('  ', ' ').strip()

            if found_lab_name and normalize(found_lab_name) == normalize(lab_name):
                base = {'lab_name': found_lab_name}
                if isinstance(value_data, dict):
                    base.update(value_data)
                lab_data = base
                break

        consumer.close()

        # Analyze the data
        if lab_data is None:
            debug_info = f"\n\n🔍 **Debug — keys seen in topic:** {', '.join(debug_seen) if debug_seen else 'none (topic may be empty)'}"
            return (
                f"❌ **Lab Not Found**\n\nNo fraud pattern data available for '{lab_name}'. This could mean:\n"
                f"- The lab name is misspelled\n"
                f"- The lab is not in our monitoring system\n"
                f"- The lab is new and hasn't been analyzed yet\n\n"
                f"**Recommendation:** Verify the exact lab name on your report and try again."
                + debug_info
            )
        
        # Calculate fraud metrics
        total_reports = lab_data.get('total_reports', 0)
        normal_count = lab_data.get('normal_count', 0)
        
        if total_reports == 0:
            return f"⚠️ **Insufficient Data**\n\nLab: {lab_name}\n\nNot enough reports analyzed yet to determine fraud patterns.\n\n**Recommendation:** Exercise caution and consider getting a second opinion from another lab."
        
        normal_percentage = (normal_count / total_reports) * 100
        
        # Fraud detection threshold: >85% normal reports
        is_fraudulent = normal_percentage > 85.0
        
        if is_fraudulent:
            estimated_savings = "₹2,000 - ₹3,000"
            return f"""🚨 **FRAUD ALERT - HIGH RISK**

**Lab Name:** {lab_name}
**Fraud Type:** Sink Test Fraud Detected
**Risk Level:** HIGH ⚠️

**Analysis:**
- Total Reports Analyzed: {total_reports:,}
- Normal Reports: {normal_count:,}
- Normal Report Rate: {normal_percentage:.1f}%
- Fraud Threshold: 85%

**What This Means:**
This lab shows a suspicious pattern where {normal_percentage:.1f}% of all reports come back as "all normal". This is significantly higher than the medical average and indicates potential "Sink Test" fraud, where labs provide fake normal results to appear legitimate.

**Financial Impact:**
By avoiding this lab, you could save: {estimated_savings} per test

**Recommendations:**
1. ❌ DO NOT trust reports from this lab
2. ✅ Get retested at a reputable hospital lab
3. ✅ Report this lab to local health authorities
4. ✅ Consider labs with <70% normal report rates
5. ✅ Always verify lab accreditation (NABL/CAP certified)

**Next Steps:**
Ask me to recommend trustworthy labs in your area, or check another lab's fraud pattern."""
        
        else:
            return f"""✅ **LAB VERIFIED - LOW RISK**

**Lab Name:** {lab_name}
**Fraud Status:** No Fraud Detected
**Risk Level:** LOW ✓

**Analysis:**
- Total Reports Analyzed: {total_reports:,}
- Normal Reports: {normal_count:,}
- Normal Report Rate: {normal_percentage:.1f}%
- Fraud Threshold: 85%

**What This Means:**
This lab shows a healthy pattern with {normal_percentage:.1f}% normal reports, which is within expected medical ranges. The lab appears to be providing genuine diagnostic services.

**Recommendations:**
1. ✅ This lab appears trustworthy based on current data
2. ✅ Still verify the lab has proper accreditation (NABL/CAP)
3. ✅ Keep your reports for medical records
4. ✅ If results seem unusual, consider a second opinion

**Note:** This analysis is based on pattern detection. Always consult with your doctor about test results."""
    
    except Exception as e:
        return f"❌ **Error Checking Lab Pattern**\n\nUnable to analyze fraud patterns for '{lab_name}'.\n\nError: {str(e)}\n\n**Recommendation:** Try again or contact support if the issue persists."

# Made with Bob
