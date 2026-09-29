from typing import List, Dict

RECOMMENDATIONS = {
    'excellent': {
        'range': (80, 100),
        'label': 'Excellent',
        'tips': [
            '🏆 Excellent health! Keep maintaining your current lifestyle.',
            '🥗 Continue your balanced diet rich in fruits and vegetables.',
            '🏃 Maintain 150+ minutes of aerobic exercise per week.',
            '😴 Keep up your 7–9 hours of quality sleep nightly.',
            '💧 Stay hydrated with 2–3 litres of water daily.',
            '🧘 Practice mindfulness or yoga to maintain mental wellness.',
        ]
    },
    'good': {
        'range': (60, 79),
        'label': 'Good',
        'tips': [
            '✅ Your health is generally good with room for improvement.',
            '🥦 Increase vegetable intake; reduce refined sugars and processed food.',
            '🚶 Add 30-minute daily walks to boost cardiovascular health.',
            '💤 Improve sleep consistency — aim for 7–8 hours nightly.',
            '💊 Schedule an annual health check-up.',
            '🧂 Reduce sodium intake to manage blood pressure.',
        ]
    },
    'moderate': {
        'range': (40, 59),
        'label': 'Moderate',
        'tips': [
            '⚠️ Your health score needs improvement. Consider lifestyle changes.',
            '🏋️ Start a supervised exercise program — 5 days/week, 30 min.',
            '🍎 Follow a low-GI diet to manage blood sugar and weight.',
            '🚭 Avoid smoking and limit alcohol consumption.',
            '👨⚕️ Consult a physician for a comprehensive health assessment.',
            '📋 Track your biometrics (BP, glucose, BMI) regularly.',
        ]
    },
    'low': {
        'range': (0, 39),
        'label': 'Low',
        'tips': [
            '🚨 Your health score is low. Please seek medical consultation immediately.',
            '🏥 Visit a physician for a full diagnostic evaluation.',
            '💊 Follow prescribed medication and treatment plans diligently.',
            '🛑 Stop all harmful habits (smoking, excessive alcohol, poor diet).',
            '🍲 Adopt a medically-supervised nutritional plan.',
            '🛏️ Prioritize rest and recovery — minimum 8 hours of sleep.',
        ]
    }
}


def recommend_lifestyle(score: float) -> List[str]:
    """Return lifestyle recommendations based on health score."""
    for _, rec in RECOMMENDATIONS.items():
        lo, hi = rec['range']
        if lo <= score <= hi:
            return rec['tips']
    return RECOMMENDATIONS['moderate']['tips']


def get_full_recommendation(score: float) -> Dict:
    """Return full recommendation object with label and tips."""
    for _, rec in RECOMMENDATIONS.items():
        lo, hi = rec['range']
        if lo <= score <= hi:
            return {'label': rec['label'], 'tips': rec['tips']}
    return {'label': 'Moderate', 'tips': RECOMMENDATIONS['moderate']['tips']}
