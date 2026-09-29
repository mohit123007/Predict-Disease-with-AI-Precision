import json
import os
from datetime import datetime
from typing import Dict, List, Any

HISTORY_PATH = 'generated_reports/charts/predictions.log'


def save_prediction(db_path: str, user: str, prediction: Dict[str, Any]) -> bool:
    """Append prediction to JSONL log file."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    entry = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'user': user,
        'prediction': prediction
    }
    try:
        with open(db_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
        return True
    except Exception:
        return False


def get_history(user: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Retrieve prediction history for a given user."""
    if not os.path.exists(HISTORY_PATH):
        return []
    entries = []
    try:
        with open(HISTORY_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if entry.get('user') == user:
                        entries.append(entry)
                except Exception:
                    continue
    except Exception:
        return []
    return list(reversed(entries[-limit:]))


def get_stats(user: str) -> Dict[str, Any]:
    """Return simple prediction statistics for a user."""
    history = get_history(user, limit=100)
    total = len(history)
    disease_counts: Dict[str, int] = {}
    for entry in history:
        pred = entry.get('prediction', {})
        disease = pred.get('disease', 'unknown')
        disease_counts[disease] = disease_counts.get(disease, 0) + 1
    return {
        'total_predictions': total,
        'disease_counts': disease_counts,
        'last_prediction': history[0] if history else None
    }
