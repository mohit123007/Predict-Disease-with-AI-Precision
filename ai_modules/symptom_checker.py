import re
from typing import List, Dict, Any

# Symptom → Disease mapping
SYMPTOM_MAP = {
    'fever': ['flu', 'malaria', 'typhoid', 'covid-19', 'dengue'],
    'cough': ['flu', 'tuberculosis', 'pneumonia', 'bronchitis', 'covid-19'],
    'chest pain': ['heart disease', 'angina', 'pleuritis', 'pneumonia', 'anxiety'],
    'shortness of breath': ['asthma', 'pneumonia', 'heart failure', 'anemia', 'covid-19'],
    'fatigue': ['anemia', 'diabetes', 'hypothyroidism', 'depression', 'chronic fatigue syndrome'],
    'frequent urination': ['diabetes', 'urinary tract infection', 'kidney disease', 'prostatitis'],
    'excessive thirst': ['diabetes', 'dehydration', 'hypercalcemia'],
    'blurred vision': ['diabetes', 'hypertension', 'glaucoma', 'migraine', 'cataracts'],
    'headache': ['migraine', 'hypertension', 'tension headache', 'meningitis', 'sinusitis'],
    'nausea': ['gastritis', 'food poisoning', 'migraine', 'liver disease', 'pregnancy'],
    'vomiting': ['food poisoning', 'gastroenteritis', 'appendicitis', 'liver disease'],
    'abdominal pain': ['appendicitis', 'gastritis', 'kidney stones', 'IBS', 'pancreatitis'],
    'joint pain': ['arthritis', 'gout', 'lupus', 'osteoporosis', 'lyme disease'],
    'skin rash': ['eczema', 'psoriasis', 'allergy', 'chickenpox', 'dermatitis'],
    'swelling': ['edema', 'kidney disease', 'heart failure', 'deep vein thrombosis'],
    'weight loss': ['diabetes', 'cancer', 'tuberculosis', 'hyperthyroidism', 'malabsorption'],
    'weight gain': ['hypothyroidism', 'PCOS', 'depression', 'cushing syndrome'],
    'dizziness': ['anemia', 'hypertension', 'vertigo', 'inner ear disorder'],
    'palpitations': ['arrhythmia', 'anxiety', 'hyperthyroidism', 'anemia'],
    'back pain': ['muscle strain', 'herniated disc', 'kidney stones', 'osteoporosis'],
}

URGENCY_KEYWORDS = [
    'chest pain', 'shortness of breath', 'severe headache', 'sudden weakness',
    'loss of consciousness', 'bleeding', 'numbness', 'high fever'
]


def analyze_symptoms(symptoms_text: str) -> Dict[str, Any]:
    """Analyze free-text symptoms and return matched diseases and advice."""
    text = symptoms_text.lower().strip()
    tokens = [t.strip() for t in re.split(r'[,;.\n]+', text) if len(t.strip()) > 2]

    # Match symptoms
    matched_symptoms: List[str] = []
    possible_diseases: Dict[str, int] = {}
    for symptom, diseases in SYMPTOM_MAP.items():
        if symptom in text:
            matched_symptoms.append(symptom)
            for d in diseases:
                possible_diseases[d] = possible_diseases.get(d, 0) + 1

    # Sort by frequency
    ranked = sorted(possible_diseases.items(), key=lambda x: x[1], reverse=True)
    top_diseases = [{'disease': d, 'match_score': count} for d, count in ranked[:5]]

    # Urgency check
    urgent = any(uw in text for uw in URGENCY_KEYWORDS)

    summary_parts = []
    if matched_symptoms:
        summary_parts.append(f"Identified symptoms: {', '.join(matched_symptoms)}.")
    if top_diseases:
        summary_parts.append(f"Possible conditions: {', '.join(d['disease'] for d in top_diseases[:3])}.")
    if urgent:
        summary_parts.append("⚠️ Some symptoms may require urgent medical attention.")

    return {
        'tokens': tokens,
        'matched_symptoms': matched_symptoms,
        'possible_diseases': top_diseases,
        'is_urgent': urgent,
        'summary': ' '.join(summary_parts) or 'No specific symptoms matched. Please describe symptoms in more detail.',
        'advice': 'Please consult a qualified physician for accurate diagnosis.'
    }
