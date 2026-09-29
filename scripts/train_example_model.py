"""
Training script for example XGBoost diabetes prediction model.
Uses the Pima Indians Diabetes dataset (diabetes.csv).

Run with: python scripts/train_example_model.py
"""
import os
import sys
import json

# ── Dataset path ────────────────────────────────────────────
DATASET_PATH = 'dataset/diabetes.csv'
MODEL_DIR = 'models/xgboost'
MODEL_PATH = os.path.join(MODEL_DIR, 'model.joblib')
METRICS_PATH = os.path.join(MODEL_DIR, 'metrics.json')


def generate_synthetic_dataset(n_samples=800):
    """Generate a synthetic diabetes-like dataset if CSV not available."""
    import random
    random.seed(42)
    rows = []
    for _ in range(n_samples):
        pregnancies = random.randint(0, 12)
        glucose = random.gauss(120, 32)
        bp = random.gauss(69, 19)
        skin = random.gauss(20, 16)
        insulin = random.gauss(79, 115)
        bmi = random.gauss(31, 8)
        dpf = random.gauss(0.47, 0.33)
        age = random.randint(21, 81)
        # Simple rule-based label
        outcome = int(glucose > 130 and bmi > 28 or glucose > 160)
        rows.append([
            max(0, int(pregnancies)), max(0, round(glucose, 1)),
            max(0, round(bp, 1)), max(0, round(skin, 1)),
            max(0, round(insulin, 1)), max(10, round(bmi, 1)),
            max(0.05, round(dpf, 3)), max(21, int(age)), outcome
        ])
    return rows


def train():
    print("=" * 60)
    print("  MedPredict — Training Example XGBoost Model")
    print("=" * 60)

    # Try importing required libraries
    try:
        import numpy as np
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import StandardScaler
        from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
        import joblib
    except ImportError as e:
        print(f"[ERROR] Missing dependency: {e}")
        print("Install with: pip install scikit-learn joblib numpy")
        sys.exit(1)

    # Load or generate dataset
    if os.path.exists(DATASET_PATH):
        try:
            import csv
            with open(DATASET_PATH, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            feature_cols = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
                            'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
            X = np.array([[float(r[c]) for c in feature_cols] for r in rows])
            y = np.array([int(r['Outcome']) for r in rows])
            print(f"[✓] Loaded dataset: {DATASET_PATH} ({len(y)} samples)")
        except Exception as e:
            print(f"[!] Could not load CSV ({e}), using synthetic data.")
            data = generate_synthetic_dataset()
            arr = np.array(data)
            X, y = arr[:, :8], arr[:, 8].astype(int)
    else:
        print(f"[!] {DATASET_PATH} not found. Generating synthetic dataset…")
        data = generate_synthetic_dataset()
        import numpy as np
        arr = np.array(data)
        X, y = arr[:, :8], arr[:, 8].astype(int)

    print(f"    Samples: {len(y)}, Positives: {y.sum()}, Negatives: {len(y) - y.sum()}")

    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Scale
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    # Try XGBoost, fallback to RandomForest
    try:
        from xgboost import XGBClassifier
        model = XGBClassifier(
            n_estimators=200, max_depth=4, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8, use_label_encoder=False,
            eval_metric='logloss', random_state=42
        )
        model_name = 'XGBoost'
    except ImportError:
        print("[!] XGBoost not installed. Falling back to RandomForestClassifier.")
        from sklearn.ensemble import RandomForestClassifier
        model = RandomForestClassifier(n_estimators=200, random_state=42)
        model_name = 'RandomForest'

    print(f"[→] Training {model_name} model…")
    model.fit(X_train_s, y_train)

    # Evaluate
    y_pred = model.predict(X_test_s)
    y_prob = model.predict_proba(X_test_s)[:, 1]
    acc = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)

    print(f"\n[✓] Training complete!")
    print(f"    Accuracy : {acc:.4f} ({acc*100:.2f}%)")
    print(f"    ROC-AUC  : {auc:.4f}")
    print(f"\n{classification_report(y_test, y_pred, target_names=['No Diabetes', 'Diabetes'])}")

    # Save model + scaler
    os.makedirs(MODEL_DIR, exist_ok=True)
    # We save the scaled model — note: prediction code must also scale
    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, os.path.join(MODEL_DIR, 'scaler.joblib'))

    # Save metrics
    metrics = {'model': model_name, 'accuracy': round(acc, 4), 'roc_auc': round(auc, 4)}
    with open(METRICS_PATH, 'w') as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[✓] Model saved to : {MODEL_PATH}")
    print(f"[✓] Scaler saved to: {os.path.join(MODEL_DIR, 'scaler.joblib')}")
    print(f"[✓] Metrics saved  : {METRICS_PATH}")
    print("\n" + "=" * 60)
    print("  Start the server: uvicorn backend.main:app --reload")
    print("=" * 60)


if __name__ == '__main__':
    train()
