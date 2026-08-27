from ibm_watsonx_orchestrate.agent_builder.tools import tool
from typing import Optional

@tool(
    name="analyze_test_necessity",
    description="Evaluates whether the number of diagnostic tests ordered by a doctor is medically appropriate for the patient's symptoms. Use this when a patient is concerned about excessive testing (e.g., '10 tests for fever') or suspects their doctor is ordering unnecessary tests for commission. Helps patients understand if they're being over-tested."
)
def analyze_test_necessity(symptoms: str, test_count: int, tests_ordered: Optional[str] = None) -> str:
    """Analyzes if the number of tests ordered is medically justified for given symptoms.
    
    This tool uses medical guidelines to assess whether the test count is appropriate,
    excessive, or insufficient based on the patient's reported symptoms.
    
    Args:
        symptoms (str): Patient's symptoms or condition (e.g., "fever", "chest pain", "diabetes checkup")
        test_count (int): Number of tests ordered by the doctor
        tests_ordered (Optional[str]): Optional comma-separated list of specific tests ordered
    
    Returns:
        str: A detailed analysis including:
            - Medical appropriateness assessment
            - Expected test range for the condition
            - Red flags if over-testing detected
            - Estimated cost implications
            - Recommendations for the patient
    """
    
    # Medical guidelines for common conditions (test count ranges)
    condition_guidelines = {
        # Acute conditions
        "fever": {"min": 2, "max": 5, "typical": ["CBC", "CRP", "Blood Culture", "Urine Test", "Chest X-ray"]},
        "cold": {"min": 0, "max": 2, "typical": ["CBC", "Throat Swab"]},
        "flu": {"min": 1, "max": 3, "typical": ["Flu Test", "CBC", "Chest X-ray"]},
        "cough": {"min": 1, "max": 4, "typical": ["Chest X-ray", "CBC", "Sputum Test", "TB Test"]},
        "headache": {"min": 0, "max": 3, "typical": ["CT Scan", "MRI", "Blood Pressure"]},
        "stomach pain": {"min": 2, "max": 6, "typical": ["Ultrasound", "CBC", "Stool Test", "Liver Function", "Kidney Function", "Amylase"]},
        "chest pain": {"min": 3, "max": 8, "typical": ["ECG", "Troponin", "Chest X-ray", "Lipid Profile", "CBC", "D-Dimer", "Stress Test", "Echocardiogram"]},
        
        # Chronic conditions
        "diabetes": {"min": 3, "max": 7, "typical": ["HbA1c", "Fasting Glucose", "Lipid Profile", "Kidney Function", "Liver Function", "Urine Microalbumin", "Thyroid"]},
        "hypertension": {"min": 3, "max": 6, "typical": ["Lipid Profile", "Kidney Function", "ECG", "Echocardiogram", "Urine Test", "Electrolytes"]},
        "thyroid": {"min": 2, "max": 5, "typical": ["TSH", "T3", "T4", "Thyroid Antibodies", "Ultrasound"]},
        
        # Routine checkups
        "health checkup": {"min": 8, "max": 15, "typical": ["CBC", "Lipid Profile", "Liver Function", "Kidney Function", "Thyroid", "Vitamin D", "Vitamin B12", "HbA1c", "Urine Test", "ECG"]},
        "annual checkup": {"min": 8, "max": 15, "typical": ["CBC", "Lipid Profile", "Liver Function", "Kidney Function", "Thyroid", "Vitamin D", "Vitamin B12", "HbA1c", "Urine Test", "ECG"]},
        "routine checkup": {"min": 8, "max": 15, "typical": ["CBC", "Lipid Profile", "Liver Function", "Kidney Function", "Thyroid", "Vitamin D", "Vitamin B12", "HbA1c", "Urine Test", "ECG"]},
    }
    
    # Normalize symptoms to lowercase for matching
    symptoms_lower = symptoms.lower().strip()
    
    # Find matching guideline
    guideline = None
    matched_condition = None
    
    for condition, guide in condition_guidelines.items():
        if condition in symptoms_lower:
            guideline = guide
            matched_condition = condition
            break
    
    # If no specific match, use general assessment
    if guideline is None:
        if test_count <= 3:
            severity = "minimal"
        elif test_count <= 6:
            severity = "moderate"
        elif test_count <= 10:
            severity = "significant"
        else:
            severity = "excessive"
        
        return f"""⚠️ **Test Necessity Analysis**

**Symptoms:** {symptoms}
**Tests Ordered:** {test_count}
**Condition Match:** No specific guideline found

**General Assessment:**
The number of tests ({test_count}) appears to be in the **{severity}** range for the reported symptoms.

**Recommendations:**
1. ✅ Ask your doctor to explain the medical necessity of each test
2. ✅ Request a written justification for the tests
3. ✅ Get a second opinion if you're concerned
4. ✅ Check if all tests are covered by insurance
5. ✅ Verify the lab is accredited (NABL/CAP)

**Your Rights:**
- You can refuse any test you don't understand
- You can ask for alternative diagnostic approaches
- You can request itemized cost estimates before testing

**Estimated Cost Range:** ₹{test_count * 300:,} - ₹{test_count * 800:,}

**Note:** Without specific symptom details, this is a general assessment. Consult your doctor for personalized medical advice."""
    
    # Analyze based on guideline
    min_tests = guideline["min"]
    max_tests = guideline["max"]
    typical_tests = guideline["typical"]
    
    # Determine if test count is appropriate
    if test_count < min_tests:
        status = "INSUFFICIENT"
        risk_level = "MODERATE"
        icon = "⚠️"
        assessment = f"The number of tests ({test_count}) is **below** the recommended minimum ({min_tests}) for {matched_condition}. This could mean incomplete diagnosis."
        
    elif test_count <= max_tests:
        status = "APPROPRIATE"
        risk_level = "LOW"
        icon = "✅"
        assessment = f"The number of tests ({test_count}) is **within the medically appropriate range** ({min_tests}-{max_tests}) for {matched_condition}."
        
    else:
        status = "EXCESSIVE"
        risk_level = "HIGH"
        icon = "🚨"
        excess_count = test_count - max_tests
        assessment = f"The number of tests ({test_count}) is **{excess_count} tests above** the recommended maximum ({max_tests}) for {matched_condition}. This suggests potential over-testing."
    
    # Calculate cost implications
    avg_cost_per_test = 500
    total_cost = test_count * avg_cost_per_test
    recommended_cost = max_tests * avg_cost_per_test
    potential_savings = max(0, (test_count - max_tests) * avg_cost_per_test)
    
    # Build response based on status
    if status == "EXCESSIVE":
        return f"""{icon} **OVER-TESTING ALERT**

**Symptoms:** {symptoms}
**Tests Ordered:** {test_count}
**Recommended Range:** {min_tests}-{max_tests} tests
**Status:** {status} - {risk_level} RISK

**Medical Assessment:**
{assessment}

**Typical Tests for {matched_condition.title()}:**
{', '.join(typical_tests[:max_tests])}

**Red Flags:**
- {excess_count} unnecessary tests ordered
- Potential commission-driven testing
- Risk of false positives from excessive testing
- Unnecessary patient anxiety and cost

**Financial Impact:**
- Estimated Total Cost: ₹{total_cost:,}
- Recommended Cost: ₹{recommended_cost:,}
- **Potential Savings: ₹{potential_savings:,}**

**What You Should Do:**
1. ❌ Question the medical necessity of extra tests
2. ✅ Ask your doctor: "Why do I need {test_count} tests for {symptoms}?"
3. ✅ Request to see only the essential tests first
4. ✅ Get a second opinion from another doctor
5. ✅ Check if your doctor has kickback arrangements with labs
6. ✅ Report excessive testing to medical authorities if confirmed

**Your Rights:**
- You can refuse unnecessary tests
- You can ask for itemized justification
- You can request phased testing (essential tests first)
- You can switch doctors if you feel exploited

**Next Steps:**
- Use the check_doctor_referral_pattern tool to see if your doctor has suspicious lab relationships
- Verify the recommended lab using check_lab_fraud_pattern tool"""
    
    elif status == "APPROPRIATE":
        return f"""{icon} **MEDICALLY APPROPRIATE TESTING**

**Symptoms:** {symptoms}
**Tests Ordered:** {test_count}
**Recommended Range:** {min_tests}-{max_tests} tests
**Status:** {status} - {risk_level} RISK

**Medical Assessment:**
{assessment}

**Typical Tests for {matched_condition.title()}:**
{', '.join(typical_tests[:test_count])}

**Positive Indicators:**
- Test count is within medical guidelines
- Appropriate diagnostic approach
- No evidence of over-testing
- Cost-effective medical care

**Financial Impact:**
- Estimated Total Cost: ₹{total_cost:,}
- This is within reasonable range for {matched_condition}

**Recommendations:**
1. ✅ The test count appears medically justified
2. ✅ Still verify the lab is accredited (NABL/CAP)
3. ✅ Ask your doctor to explain what each test checks for
4. ✅ Keep all reports for your medical records
5. ✅ Follow up with your doctor for results interpretation

**Note:** Appropriate test count doesn't guarantee the lab is fraud-free. Use check_lab_fraud_pattern to verify the lab's trustworthiness."""
    
    else:  # INSUFFICIENT
        return f"""{icon} **INSUFFICIENT TESTING**

**Symptoms:** {symptoms}
**Tests Ordered:** {test_count}
**Recommended Range:** {min_tests}-{max_tests} tests
**Status:** {status} - {risk_level} RISK

**Medical Assessment:**
{assessment}

**Typical Tests for {matched_condition.title()}:**
{', '.join(typical_tests[:min_tests])}

**Concerns:**
- Fewer tests than medically recommended
- Risk of incomplete diagnosis
- Important conditions might be missed
- May need additional testing later

**Recommendations:**
1. ⚠️ Ask your doctor why fewer tests are being ordered
2. ✅ Discuss if additional tests should be considered
3. ✅ Ensure critical tests are included
4. ✅ Get a second opinion if symptoms persist
5. ✅ Monitor symptoms and follow up if they worsen

**Note:** While over-testing is a concern, under-testing can also be problematic. Ensure your doctor is ordering adequate tests for proper diagnosis."""

# Made with Bob
