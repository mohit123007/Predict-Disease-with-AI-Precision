from typing import Dict, Any

# Normal ranges for common biometrics
NORMAL_RANGES = {
    'age':              (20, 60, 1.0),
    'bmi':              (18.5, 24.9, 1.5),
    'glucose':          (70, 100, 2.0),
    'blood_pressure':   (60, 90, 1.5),
    'cholesterol':      (100, 200, 1.5),
    'insulin':          (16, 166, 0.8),
    'heart_rate':       (60, 100, 1.0),
    'hemoglobin':       (12.0, 17.5, 1.2),
    'creatinine':       (0.6, 1.2, 1.8),
    'triglycerides':    (50, 150, 1.0),
    'urea':             (7, 20, 1.0),
    'skin_thickness':   (10, 35, 0.5),
    'pregnancies':      (0, 5, 0.3),
}


def _is_num(v: Any) -> bool:
    try:
        float(v); return True
    except Exception:
        return False


def calculate_risk(features: Dict[str, Any]) -> Dict[str, Any]:
    """Compute weighted risk score from biometric features."""
    total_weight = 0.0
    weighted_risk = 0.0
    risk_factors = []

    for key, value in features.items():
        if not _is_num(value):
            continue
        val = float(value)
        key_lower = key.lower().replace(' ', '_')
        norm = NORMAL_RANGES.get(key_lower)
        if norm:
            norm_min, norm_max, weight = norm
            if val > norm_max:
                deviation = min(1.0, (val - norm_max) / max(1, norm_max) * 2)
                weighted_risk += weight * deviation
                risk_factors.append({'factor': key, 'value': val, 'status': 'HIGH', 'normal': f'{norm_min}–{norm_max}'})
            elif val < norm_min:
                deviation = min(1.0, (norm_min - val) / max(1, norm_min) * 2)
                weighted_risk += weight * deviation
                risk_factors.append({'factor': key, 'value': val, 'status': 'LOW', 'normal': f'{norm_min}–{norm_max}'})
            else:
                risk_factors.append({'factor': key, 'value': val, 'status': 'NORMAL', 'normal': f'{norm_min}–{norm_max}'})
            total_weight += weight
        else:
            # Unknown field — add small contribution
            weighted_risk += abs(val) * 0.01
            total_weight += 0.5

    if total_weight == 0:
        raw_score = sum(float(v) for v in features.values() if _is_num(v))
        risk_score = min(100, max(0, raw_score))
    else:
        risk_score = min(100, max(0, (weighted_risk / total_weight) * 100))

    if risk_score < 20:
        risk_level = 'low'
        risk_color = 'green'
        advice = 'Your biometric values look healthy. Maintain your current lifestyle.'
    elif risk_score < 50:
        risk_level = 'moderate'
        risk_color = 'yellow'
        advice = 'Some values are outside normal range. Consider lifestyle improvements and regular check-ups.'
    elif risk_score < 75:
        risk_level = 'high'
        risk_color = 'orange'
        advice = 'Multiple risk factors detected. Consult a physician promptly and adjust lifestyle.'
    else:
        risk_level = 'critical'
        risk_color = 'red'
        advice = 'Critical risk levels detected. Seek immediate medical attention.'

    return {
        'risk_score': round(risk_score, 2),
        'risk_level': risk_level,
        'risk_color': risk_color,
        'advice': advice,
        'risk_factors': risk_factors,
        'factors_checked': len(risk_factors)
    }
