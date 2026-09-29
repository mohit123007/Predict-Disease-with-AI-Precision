from typing import Dict, Any

# Optimal ranges for health scoring
OPTIMAL = {
    'bmi':           (18.5, 24.9),
    'glucose':       (70, 100),
    'blood_pressure':(60, 80),
    'heart_rate':    (60, 80),
    'cholesterol':   (100, 180),
    'hemoglobin':    (12.0, 17.5),
    'age':           (20, 45),
    'sleep_hours':   (7, 9),
    'water_intake':  (2.0, 3.5),
    'exercise_min':  (150, 300),
}


def _is_num(v: Any) -> bool:
    try:
        float(v); return True
    except Exception:
        return False


def compute_health_score(features: Dict[str, Any]) -> float:
    """Compute a 0–100 health score from biometric and lifestyle features."""
    scores = []
    for key, val in features.items():
        if not _is_num(val):
            continue
        v = float(val)
        k = key.lower().replace(' ', '_')
        opt = OPTIMAL.get(k)
        if opt:
            lo, hi = opt
            if lo <= v <= hi:
                scores.append(100.0)
            elif v < lo:
                ratio = v / lo
                scores.append(max(0.0, ratio * 100))
            else:
                ratio = hi / v
                scores.append(max(0.0, ratio * 100))

    if not scores:
        # Fallback: generic computation
        vals = [float(v) for v in features.values() if _is_num(v)]
        return max(0.0, min(100.0, 100.0 - sum(vals) / max(1, len(vals) * 2)))

    return round(sum(scores) / len(scores), 2)
