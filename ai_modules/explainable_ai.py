from typing import Dict, Any, List

FEATURE_DESCRIPTIONS = {
    'glucose': 'Blood glucose level (mg/dL) — key indicator for diabetes risk.',
    'bmi': 'Body Mass Index — measures body fat relative to height and weight.',
    'blood_pressure': 'Systolic blood pressure — elevated values increase cardiovascular risk.',
    'age': 'Patient age — risk increases with advancing age.',
    'insulin': 'Serum insulin level — resistance correlates with diabetes.',
    'skin_thickness': 'Triceps skin fold thickness — proxy for body fat percentage.',
    'pregnancies': 'Number of pregnancies — gestational diabetes increases risk.',
    'diabetes_pedigree_function': 'Genetic diabetes likelihood score based on family history.',
    'cholesterol': 'Total cholesterol — elevated levels increase heart disease risk.',
    'chest_pain': 'Presence and type of chest pain — strong predictor of cardiac events.',
    'max_heart_rate': 'Maximum heart rate achieved — indicates cardiac capacity.',
    'exercise_angina': 'Exercise-induced angina — strong indicator of coronary artery disease.',
    'hemoglobin': 'Hemoglobin level — low values indicate anemia.',
    'creatinine': 'Serum creatinine — elevated levels indicate kidney dysfunction.',
    'albumin': 'Urine albumin — abnormal levels suggest kidney disease.',
}


def _is_num(v: Any) -> bool:
    try:
        float(v); return True
    except Exception:
        return False


def explain_tabular_prediction(model: Any, features: Dict[str, Any]) -> Dict[str, Any]:
    """Compute feature contributions and explanations."""
    contributions: List[Dict] = []
    for k, v in features.items():
        if not _is_num(v):
            continue
        fval = float(v)
        # Normalized contribution (stub — replace with SHAP in production)
        contribution = round(fval * 0.1, 4)
        desc = FEATURE_DESCRIPTIONS.get(k.lower(), f'{k} — biometric feature influencing prediction.')
        contributions.append({
            'feature': k,
            'value': fval,
            'contribution': contribution,
            'direction': 'increases risk' if contribution > 0 else 'decreases risk',
            'description': desc
        })

    contributions = sorted(contributions, key=lambda x: abs(x['contribution']), reverse=True)[:6]
    return {
        'contributions': contributions,
        'method': 'Feature Contribution Analysis (Stub — integrate SHAP for production)',
        'top_factor': contributions[0]['feature'] if contributions else 'N/A'
    }
