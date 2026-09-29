import re
from typing import Dict

# Knowledge base: keyword → responses
KB: Dict[str, list] = {
    "diabetes": [
        "Diabetes is a chronic condition affecting blood sugar regulation.",
        "Key risk factors include obesity, family history, and sedentary lifestyle.",
        "Fasting blood sugar ≥ 126 mg/dL on two separate tests indicates diabetes.",
        "Management: balanced diet, regular exercise, medication as prescribed by a doctor."
    ],
    "heart": [
        "Heart disease is the leading cause of death worldwide.",
        "Risk factors: high BP, high cholesterol, smoking, obesity, diabetes.",
        "Symptoms: chest pain, shortness of breath, fatigue, irregular heartbeat.",
        "Preventive measures: regular exercise, low-sodium diet, stress management."
    ],
    "kidney": [
        "Chronic kidney disease (CKD) reduces the kidneys' ability to filter blood.",
        "Early stages are often symptom-free; regular blood and urine tests help detect it.",
        "Stay hydrated, control blood pressure, and avoid NSAIDs if at risk."
    ],
    "liver": [
        "Liver disease can stem from alcohol, fatty liver (NAFLD), hepatitis, or cirrhosis.",
        "Symptoms: jaundice, abdominal swelling, fatigue, dark urine.",
        "Avoid alcohol, maintain a healthy weight, get vaccinated for hepatitis."
    ],
    "pneumonia": [
        "Pneumonia is a lung infection causing cough, fever, and difficulty breathing.",
        "Bacterial pneumonia is treated with antibiotics; viral pneumonia with rest and antivirals.",
        "Vaccination (pneumococcal vaccine) helps prevent bacterial pneumonia."
    ],
    "bmi": [
        "BMI (Body Mass Index) = weight(kg) / height(m)².",
        "Healthy BMI range: 18.5 – 24.9. Overweight: 25–29.9. Obese: ≥ 30.",
        "BMI is a screening tool, not a diagnostic measure."
    ],
    "glucose": [
        "Normal fasting glucose: 70–100 mg/dL.",
        "Pre-diabetes: 100–125 mg/dL. Diabetes: ≥ 126 mg/dL.",
        "Postprandial glucose (2 hours after meal) should be under 140 mg/dL in healthy individuals."
    ],
    "blood pressure": [
        "Normal BP: below 120/80 mmHg.",
        "High BP (hypertension): consistently ≥ 130/80 mmHg.",
        "Lifestyle changes: reduce salt, increase potassium, exercise, limit alcohol."
    ],
    "cholesterol": [
        "Total cholesterol should be below 200 mg/dL.",
        "HDL (good) cholesterol: ≥ 40 mg/dL men, ≥ 50 mg/dL women.",
        "LDL (bad) cholesterol: below 100 mg/dL is optimal."
    ],
    "diet": [
        "A balanced diet includes fruits, vegetables, whole grains, lean protein, and healthy fats.",
        "Limit processed foods, refined sugar, and saturated fats.",
        "Mediterranean diet is widely associated with lower cardiovascular risk."
    ],
    "exercise": [
        "WHO recommends at least 150 minutes of moderate aerobic activity per week.",
        "Strength training at least 2 days per week improves metabolic health.",
        "Even 30-minute daily walks significantly reduce chronic disease risk."
    ],
    "sleep": [
        "Adults need 7–9 hours of sleep per night.",
        "Poor sleep increases risk of obesity, diabetes, and cardiovascular disease.",
        "Maintain a consistent sleep schedule and avoid screens 1 hour before bed."
    ],
    "stress": [
        "Chronic stress raises cortisol levels, increasing inflammation and disease risk.",
        "Techniques: meditation, deep breathing, yoga, journaling, and regular exercise.",
        "Seek professional mental health support if stress is unmanageable."
    ],
    "symptom": [
        "Common symptoms to watch: persistent fatigue, unexplained weight loss, frequent urination, chest pain.",
        "Do not self-diagnose — always consult a certified healthcare professional.",
        "Use the Disease Prediction tool to get an AI-based risk assessment."
    ],
    "default": [
        "I'm here to help with general health and medical questions.",
        "Please consult a qualified physician for personalized medical advice.",
        "You can use our Disease Prediction, Health Score, and Doctor Recommendation tools for AI-powered insights."
    ]
}


def _find_intent(query: str) -> str:
    q = query.lower()
    for key in KB:
        if key in q:
            return key
    # partial matches
    patterns = {
        r'sugar|insulin|a1c|hba1c': 'glucose',
        r'heart|cardiac|chest|cardio': 'heart',
        r'lung|breath|cough|pulmonary': 'pneumonia',
        r'weight|fat|obese|overweight': 'bmi',
        r'bp|blood pressure|hypertension': 'blood pressure',
        r'food|eat|nutrition|meal': 'diet',
        r'walk|run|gym|workout|fitness': 'exercise',
        r'tired|fatigue|rest|insomnia': 'sleep',
        r'stress|anxiety|mental|depress': 'stress',
    }
    for pattern, intent in patterns.items():
        if re.search(pattern, q):
            return intent
    return 'default'


def reply_to_query(query: str) -> dict:
    """Smart rule-based chatbot for medical Q&A."""
    import random
    intent = _find_intent(query)
    responses = KB.get(intent, KB['default'])
    reply = '\n'.join(responses)
    return {
        "query": query,
        "intent": intent,
        "reply": reply,
        "disclaimer": "⚕️ This is AI-generated health information. Always consult a licensed medical professional for diagnosis and treatment."
    }
