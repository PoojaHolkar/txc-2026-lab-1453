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
    name="check_doctor_referral_pattern",
    description="Analyzes a doctor's referral patterns to detect potential kickback fraud. Use this when a patient is suspicious about their doctor always referring to the same lab, or wants to verify if their doctor has financial incentives from a specific lab. Detects 'Kickback Fraud' where doctors refer >80% of patients to a single lab in exchange for commissions. Also provides average tests per visit and average bill amounts for the doctor-lab combination.",
    expected_credentials=[
        {"app_id": APP_ID, "type": ConnectionType.KEY_VALUE}
    ]
)
def check_doctor_referral_pattern(doctor_name: str, lab_name: Optional[str] = None) -> str:
    """Analyzes referral patterns for a specific doctor by reading from Kafka topics.
    
    This tool connects to Confluent Kafka and reads:
    1. doctors_patterns topic - to check referral concentration (Avro format)
       Schema: Key={doctor_name, lab_name}, Value={referral_count}
    2. reports.raw topic - to calculate average tests and bills (JSON format)
    
    Fraud Detection Logic:
    - Kickback Fraud: If one lab receives >80% of doctor's referrals, the doctor is flagged
    - This indicates the doctor may be receiving commissions from that lab
    - Also analyzes average tests per visit and bills to detect over-testing patterns
    
    Args:
        doctor_name (str): The name of the doctor to check (e.g., "Dr. Vinod Mehta", "Dr. Sharma")
        lab_name (Optional[str]): Optional lab name to analyze doctor-lab combination specifically
    
    Returns:
        str: A detailed analysis including:
            - Doctor name and fraud status
            - Total referrals made
            - Top lab and referral percentage
            - Average tests per visit (for doctor-lab combination if lab_name provided)
            - Average bill amount (for doctor-lab combination if lab_name provided)
            - Fraud risk assessment
            - Patient protection recommendations
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
            'group.id': f'fraud-detection-doctor-{int(time.time())}',  # Unique group ID
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False
        }
        
        consumer = Consumer(consumer_config)
        avro_deserializer = AvroDeserializer(schema_registry_client)

        # Manually assign ALL partitions so we read every partition to EOF
        topic_meta = consumer.list_topics('doctors_patterns', timeout=10)
        partitions = [
            __import__('confluent_kafka').TopicPartition('doctors_patterns', p)
            for p in topic_meta.topics['doctors_patterns'].partitions
        ]
        consumer.assign(partitions)

        # Read ALL messages for this doctor and aggregate
        # Schema: Key={doctor_name, lab_name}, Value={referral_count}
        doctor_referrals = {}  # {lab_name: referral_count}
        max_messages = 500
        message_count = 0
        timeout_seconds = 15
        start_time = time.time()
        eof_partitions = set()

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
            
            # Deserialize value (always Avro)
            # Deserialize key: try Avro first, fall back to plain UTF-8 string
            try:
                key_ctx = SerializationContext('doctors_patterns', MessageField.KEY)
                value_ctx = SerializationContext('doctors_patterns', MessageField.VALUE)

                # Try Avro key decode first; if it fails decode as plain composite string
                try:
                    key_data = avro_deserializer(msg.key(), key_ctx) if msg.key() else None
                    if isinstance(key_data, dict):
                        found_doctor_name = key_data.get('doctor_name', '')
                        found_lab_name = key_data.get('lab_name', 'Unknown')
                    else:
                        found_doctor_name = ''
                        found_lab_name = 'Unknown'
                except Exception:
                    # Flink writes composite primary keys as concatenated plain UTF-8
                    # Format is typically "doctor_name\x00lab_name" or just "doctor_name"
                    raw_key = msg.key().decode('utf-8') if msg.key() else ''
                    parts = raw_key.split('\x00')  # Flink null-byte separator
                    found_doctor_name = parts[0] if parts else ''
                    found_lab_name = parts[1] if len(parts) > 1 else 'Unknown'

                value_data = avro_deserializer(msg.value(), value_ctx)

                def normalize(name):
                    return name.lower().replace('.', '').replace('  ', ' ').strip()

                if found_doctor_name and normalize(found_doctor_name) == normalize(doctor_name):
                    count = value_data.get('referral_count', 0) if isinstance(value_data, dict) else 0
                    doctor_referrals[found_lab_name] = doctor_referrals.get(found_lab_name, 0) + count

            except Exception:
                continue
            
            message_count += 1
        
        consumer.close()
        
        # Analyze the aggregated data
        if not doctor_referrals:
            return f"❌ **Doctor Not Found**\n\nNo referral pattern data available for '{doctor_name}'. This could mean:\n- The doctor name is misspelled\n- The doctor is not in our monitoring system\n- The doctor is new and hasn't been analyzed yet\n\n**Recommendation:** Verify the exact doctor name and try again, or ask your doctor directly about their lab referral practices."
        
        # Calculate fraud metrics
        total_referrals = sum(doctor_referrals.values())
        
        if total_referrals == 0:
            return f"⚠️ **Insufficient Data**\n\nDoctor: {doctor_name}\n\nNot enough referral data analyzed yet to determine patterns.\n\n**Recommendation:** Exercise caution and ask your doctor why they recommend a specific lab."
        
        # Find top lab
        top_lab = max(doctor_referrals, key=doctor_referrals.get)
        top_lab_count = doctor_referrals[top_lab]
        referral_percentage = (top_lab_count / total_referrals) * 100
        
        # Now read reports.raw topic to get average tests and bills for doctor-lab combination
        avg_tests = None
        avg_bill = None
        report_count = 0
        
        # Determine which lab to analyze (either provided lab_name or top_lab from patterns)
        target_lab = lab_name if lab_name else top_lab
        
        if target_lab and target_lab != 'Unknown':
            try:
                # Create new consumer for reports.raw (JSON format, not Avro)
                reports_consumer_config = {
                    'bootstrap.servers': bootstrap_servers,
                    'security.protocol': 'SASL_SSL',
                    'sasl.mechanisms': 'PLAIN',
                    'sasl.username': sasl_username,
                    'sasl.password': sasl_password,
                    'group.id': f'fraud-detection-reports-{int(time.time())}',
                    'auto.offset.reset': 'earliest',
                    'enable.auto.commit': False
                }
                
                reports_consumer = Consumer(reports_consumer_config)
                reports_consumer.subscribe(['reports.raw'])
                
                # Collect test counts and bills for this doctor-lab combination
                test_counts = []
                bill_amounts = []
                max_report_messages = 150
                report_message_count = 0
                report_timeout = 15
                report_start_time = time.time()
                
                while report_message_count < max_report_messages and (time.time() - report_start_time) < report_timeout:
                    msg = reports_consumer.poll(timeout=0.5)
                    
                    if msg is None:
                        continue
                    
                    if msg.error():
                        if msg.error().code() == KafkaError._PARTITION_EOF:
                            break
                        else:
                            continue
                    
                    # Parse JSON message
                    try:
                        report_data = json.loads(msg.value().decode('utf-8'))
                        
                        # Check if this report matches our doctor and lab
                        report_doctor = report_data.get('referring_doctor', {}).get('name', '')
                        report_lab = report_data.get('lab', {}).get('name', '')
                        
                        if (report_doctor.lower() == doctor_name.lower() and 
                            report_lab.lower() == target_lab.lower()):
                            # Collect test count and bill amount
                            test_count = report_data.get('test_count', 0)
                            amount = report_data.get('amount_paid', 0)
                            
                            if test_count > 0:
                                test_counts.append(test_count)
                            if amount > 0:
                                bill_amounts.append(amount)
                            
                            report_count += 1
                    except:
                        continue
                    
                    report_message_count += 1
                
                reports_consumer.close()
                
                # Calculate averages
                if test_counts:
                    avg_tests = sum(test_counts) / len(test_counts)
                if bill_amounts:
                    avg_bill = sum(bill_amounts) / len(bill_amounts)
                    
            except Exception as e:
                # If reports.raw analysis fails, continue with just the referral pattern data
                pass
        
        # Build additional metrics section if available
        additional_metrics = ""
        if avg_tests is not None or avg_bill is not None:
            additional_metrics = "\n**Doctor-Lab Combination Metrics:**"
            if report_count > 0:
                additional_metrics += f"\n- Reports Analyzed: {report_count}"
            if avg_tests is not None:
                additional_metrics += f"\n- Average Tests per Visit: {avg_tests:.1f} tests"
                if avg_tests > 6:
                    additional_metrics += " ⚠️ (Normal: 2-4 tests)"
            if avg_bill is not None:
                additional_metrics += f"\n- Average Bill Amount: ₹{avg_bill:,.0f}"
                if avg_bill > 3000:
                    additional_metrics += " ⚠️ (Normal: ₹500-800)"
        
        # Fraud detection threshold: >80% referrals to single lab
        is_fraudulent = referral_percentage > 80.0
        
        if is_fraudulent:
            return f"""🚨 **FRAUD ALERT - KICKBACK SUSPECTED**

**Doctor Name:** {doctor_name}
**Fraud Type:** Kickback Fraud Detected
**Risk Level:** HIGH ⚠️

**Referral Pattern Analysis:**
- Total Referrals Made: {total_referrals:,}
- Top Referred Lab: {top_lab}
- Referrals to Top Lab: {top_lab_count:,}
- Concentration Rate: {referral_percentage:.1f}%
- Fraud Threshold: 80%
{additional_metrics}

**What This Means:**
This doctor refers {referral_percentage:.1f}% of patients to a single lab ({top_lab}). This extremely high concentration suggests the doctor may be receiving financial kickbacks or commissions from this lab, compromising their medical judgment.

**Red Flags:**
- Unnatural referral concentration (healthy range: 30-50%)
- Potential conflict of interest
- Patient care may be compromised for profit
- Lab quality may not be the selection criteria
{"- Excessive testing pattern detected" if avg_tests and avg_tests > 6 else ""}
{"- High billing amounts detected" if avg_bill and avg_bill > 3000 else ""}

**Your Rights as a Patient:**
1. ✅ You have the RIGHT to choose your own diagnostic lab
2. ✅ You can request referrals to multiple labs for comparison
3. ✅ You can ask your doctor why they prefer this specific lab
4. ✅ You can report suspicious practices to medical boards

**Recommendations:**
1. ❌ Question this doctor's lab recommendations
2. ✅ Ask for alternative lab options
3. ✅ Get a second opinion from another doctor
4. ✅ Choose NABL/CAP accredited labs independently
5. ✅ Report to State Medical Council if concerned

**Next Steps:**
- Check if the referred lab ({top_lab}) has fraud patterns
- Consider switching to a doctor with balanced referral practices
- Report to medical authorities if you've experienced issues"""
        
        else:
            # Calculate referral diversity
            other_referrals = total_referrals - top_lab_count
            diversity_score = "Good" if referral_percentage < 50 else "Moderate"
            
            return f"""✅ **DOCTOR VERIFIED - LOW RISK**

**Doctor Name:** {doctor_name}
**Fraud Status:** No Kickback Fraud Detected
**Risk Level:** LOW ✓

**Referral Pattern Analysis:**
- Total Referrals Made: {total_referrals:,}
- Top Referred Lab: {top_lab}
- Referrals to Top Lab: {top_lab_count:,} ({referral_percentage:.1f}%)
- Other Labs: {other_referrals:,} referrals
- Referral Diversity: {diversity_score}
- Fraud Threshold: 80%
{additional_metrics}

**What This Means:**
This doctor shows a healthy referral pattern with {referral_percentage:.1f}% concentration to their most-referred lab. This is within normal medical practice ranges and suggests the doctor is making referrals based on quality and patient needs rather than financial incentives.

**Positive Indicators:**
- Balanced referral distribution
- No evidence of kickback arrangements
- Patient-centric decision making
- Professional medical judgment maintained
{"- Testing patterns appear reasonable" if avg_tests and avg_tests <= 6 else ""}
{"- Billing amounts are within normal range" if avg_bill and avg_bill <= 3000 else ""}

**Recommendations:**
1. ✅ This doctor's referral practices appear ethical
2. ✅ Still verify that referred labs are accredited
3. ✅ You can always ask why a specific lab is recommended
4. ✅ Feel free to choose your preferred lab if you have one
{"5. ⚠️ However, average tests per visit seem high - discuss test necessity with your doctor" if avg_tests and avg_tests > 6 else ""}

**Note:** This analysis is based on referral patterns. A good referral pattern doesn't guarantee all referred labs are fraud-free - always verify the lab independently."""
    
    except Exception as e:
        return f"❌ **Error Checking Doctor Pattern**\n\nUnable to analyze referral patterns for '{doctor_name}'.\n\nError: {str(e)}\n\n**Recommendation:** Try again or contact support if the issue persists."

# Made with Bob
