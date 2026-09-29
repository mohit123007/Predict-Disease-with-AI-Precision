from typing import Dict, Any, List
import os

MODEL_PATH = 'models/xgboost/model.joblib'

# Disease thresholds for multi-disease detection
DISEASE_RULES = {
    'diabetes': {
        'fields': ['glucose', 'bmi', 'age', 'insulin', 'blood_pressure', 'skin_thickness', 'pregnancies', 'diabetes_pedigree_function'],
        'threshold': 0.5,
        'weights': {'glucose': 0.35, 'bmi': 0.20, 'age': 0.10, 'insulin': 0.10,
                    'blood_pressure': 0.10, 'skin_thickness': 0.05, 'pregnancies': 0.05, 'diabetes_pedigree_function': 0.05},
        'norms': {'glucose': (70, 125), 'bmi': (18.5, 24.9), 'age': (20, 60),
                  'insulin': (16, 166), 'blood_pressure': (60, 90), 'skin_thickness': (10, 35),
                  'pregnancies': (0, 5), 'diabetes_pedigree_function': (0, 0.6)}
    },
    'heart_disease': {
        'fields': ['age', 'blood_pressure', 'cholesterol', 'max_heart_rate', 'chest_pain', 'fasting_blood_sugar', 'exercise_angina'],
        'threshold': 0.5,
        'weights': {'age': 0.10, 'blood_pressure': 0.15, 'cholesterol': 0.20, 'max_heart_rate': 0.15,
                    'chest_pain': 0.20, 'fasting_blood_sugar': 0.10, 'exercise_angina': 0.10},
        'norms': {'age': (20, 60), 'blood_pressure': (60, 120), 'cholesterol': (100, 200),
                  'max_heart_rate': (100, 170), 'chest_pain': (0, 1), 'fasting_blood_sugar': (70, 110), 'exercise_angina': (0, 1)}
    },
    'kidney_disease': {
        'fields': ['blood_pressure', 'specific_gravity', 'albumin', 'blood_urea', 'serum_creatinine', 'hemoglobin', 'age'],
        'threshold': 0.5,
        'weights': {'blood_pressure': 0.15, 'specific_gravity': 0.10, 'albumin': 0.20,
                    'blood_urea': 0.20, 'serum_creatinine': 0.20, 'hemoglobin': 0.10, 'age': 0.05},
        'norms': {'blood_pressure': (60, 90), 'specific_gravity': (1.010, 1.025), 'albumin': (0, 1),
                  'blood_urea': (7, 20), 'serum_creatinine': (0.6, 1.2), 'hemoglobin': (12, 17), 'age': (20, 65)}
    },
}

_model = None


def _is_number(v: Any) -> bool:
    try:
        float(v); return True
    except Exception:
        return False


def _load_model():
    global _model
    if _model is not None:
        return _model
    try:
        if os.path.exists(MODEL_PATH):
            import joblib
            _model = joblib.load(MODEL_PATH)
            return _model
    except Exception:
        _model = None
    return None


def _compute_rule_based_prob(features: Dict[str, Any], disease_key: str) -> float:
    """Compute probability using normalized feature weights."""
    rule = DISEASE_RULES.get(disease_key)
    if not rule:
        return 0.0
    total_weight = 0.0
    weighted_risk = 0.0
    for field, weight in rule['weights'].items():
        val = features.get(field)
        if val is None or not _is_number(val):
            continue
        val = float(val)
        norm_min, norm_max = rule['norms'].get(field, (0, 1))
        # Risk increases above normal maximum
        if val > norm_max:
            ratio = min(1.0, (val - norm_max) / max(1, norm_max))
        elif val < norm_min:
            ratio = min(1.0, (norm_min - val) / max(1, norm_min))
        else:
            ratio = 0.0
        weighted_risk += weight * ratio
        total_weight += weight
    if total_weight == 0:
        return 0.3  # uncertain
    return min(0.99, max(0.01, weighted_risk / total_weight + 0.1))


def predict_tabular(features: Dict[str, Any]) -> Dict[str, Any]:
    """Multi-disease prediction from structured features."""
    model = _load_model()
    keys = sorted(features.keys())
    feature_vector = [float(features[k]) if _is_number(features.get(k, 0)) else 0.0 for k in keys]

    # Try real model first (for diabetes as primary)
    if model is not None:
        try:
            prob = float(model.predict_proba([feature_vector])[0][1])
            disease = 'diabetes' if prob >= 0.5 else 'no_disease_detected'
            ranked = sorted(((k, float(v)) for k, v in features.items() if _is_number(v)),
                            key=lambda x: abs(x[1]), reverse=True)
            explanation = [f"{k.replace('_', ' ').title()} = {v:.2f}" for k, v in ranked[:4]]
            return {
                'disease': disease, 'probability': round(prob, 4),
                'confidence': round(prob * 100, 2), 'explanation': explanation,
                'model': 'XGBoost (trained)'
            }
        except Exception:
            pass

    # Auto-detect disease type from features present
    detected_disease = 'diabetes'  # default
    for disease_key, rule in DISEASE_RULES.items():
        matching = sum(1 for f in rule['fields'] if f in features)
        if matching >= 3:
            detected_disease = disease_key
            break

    prob = _compute_rule_based_prob(features, detected_disease)
    disease_label = detected_disease if prob >= 0.5 else 'no_disease_detected'

    ranked = sorted(((k, float(v)) for k, v in features.items() if _is_number(v)),
                    key=lambda x: abs(x[1]), reverse=True)
    explanation = []
    rule = DISEASE_RULES.get(detected_disease, {})
    norms = rule.get('norms', {})
    for k, v in ranked[:4]:
        norm = norms.get(k)
        if norm:
            status = 'normal' if norm[0] <= v <= norm[1] else ('high' if v > norm[1] else 'low')
            explanation.append(f"{k.replace('_', ' ').title()}: {v:.1f} ({status}, normal {norm[0]}–{norm[1]})")
        else:
            explanation.append(f"{k.replace('_', ' ').title()}: {v:.1f} (influences prediction)")

    return {
        'disease': disease_label,
        'disease_checked': detected_disease.replace('_', ' ').title(),
        'probability': round(prob, 4),
        'confidence': round(prob * 100, 2),
        'explanation': explanation,
        'model': 'Rule-based AI (no trained model loaded)'
    }


def predict_image(image_bytes: bytes) -> Dict[str, Any]:
    """CNN image prediction stub — replace with real model inference."""
    size = len(image_bytes)
    # Deterministic stub based on image size
    diseases = [
        {'disease': 'pneumonia', 'probability': 0.72, 'confidence': 72.0,
         'description': 'Bacterial or viral lung infection detected in lower lobes.'},
        {'disease': 'normal', 'probability': 0.91, 'confidence': 91.0,
         'description': 'No significant abnormalities detected in the image.'},
        {'disease': 'tuberculosis', 'probability': 0.58, 'confidence': 58.0,
         'description': 'Possible TB-related patterns observed. Further testing required.'},
    ]
    result = diseases[size % 3]
    result['explanation_image'] = None
    result['model'] = 'CNN Stub (integrate real model for production)'
    return result
