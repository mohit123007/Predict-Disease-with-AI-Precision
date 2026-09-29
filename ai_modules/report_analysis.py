import re
from typing import Dict, Any, List

# Medical keywords to flag
FLAG_KEYWORDS = [
    'elevated', 'high', 'low', 'abnormal', 'critical', 'borderline',
    'positive', 'negative', 'detected', 'not detected', 'within range',
    'out of range', 'increased', 'decreased', 'borderline', 'mild', 'moderate', 'severe'
]

LAB_PATTERNS = [
    (r'glucose[:\s]+([\d.]+)', 'Glucose'),
    (r'hemoglobin[:\s]+([\d.]+)', 'Hemoglobin'),
    (r'creatinine[:\s]+([\d.]+)', 'Creatinine'),
    (r'cholesterol[:\s]+([\d.]+)', 'Total Cholesterol'),
    (r'hdl[:\s]+([\d.]+)', 'HDL'),
    (r'ldl[:\s]+([\d.]+)', 'LDL'),
    (r'triglyceride[:\s]+([\d.]+)', 'Triglycerides'),
    (r'blood pressure[:\s]+([\d/]+)', 'Blood Pressure'),
    (r'bmi[:\s]+([\d.]+)', 'BMI'),
    (r'tsh[:\s]+([\d.]+)', 'TSH'),
    (r'urea[:\s]+([\d.]+)', 'Blood Urea'),
    (r'wbc[:\s]+([\d.]+)', 'WBC Count'),
    (r'rbc[:\s]+([\d.]+)', 'RBC Count'),
    (r'platelets?[:\s]+([\d,]+)', 'Platelets'),
]


def parse_report_text(text: str) -> Dict[str, Any]:
    """Extract structured data and key findings from medical report text."""
    # Split into sentences
    sentences = [s.strip() for s in re.split(r'[.!?\n]+', text) if len(s.strip()) > 5]

    # Extract lab values
    lab_values: Dict[str, str] = {}
    text_lower = text.lower()
    for pattern, label in LAB_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            lab_values[label] = match.group(1)

    # Flag abnormal sentences
    flagged: List[str] = []
    for sentence in sentences:
        s_lower = sentence.lower()
        if any(kw in s_lower for kw in FLAG_KEYWORDS):
            flagged.append(sentence)

    # Summary
    summary = sentences[0] if sentences else 'No content found.'
    if flagged:
        summary = f"Report contains {len(flagged)} flagged finding(s). First: {flagged[0][:120]}"

    return {
        'sentences': sentences[:20],
        'flagged_findings': flagged[:10],
        'lab_values': lab_values,
        'summary': summary,
        'total_sentences': len(sentences),
        'has_abnormal': len(flagged) > 0
    }
