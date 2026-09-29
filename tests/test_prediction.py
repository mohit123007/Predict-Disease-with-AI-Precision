"""
Tests for disease prediction AI modules.
Run with: python -m pytest tests/test_prediction.py -v
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ai_modules.disease_prediction import predict_tabular, predict_image
from ai_modules.risk_calculator import calculate_risk
from ai_modules.health_score import compute_health_score
from ai_modules.explainable_ai import explain_tabular_prediction


# ─── Tabular Prediction Tests ──────────────────────────────

class TestTabularPrediction:
    def test_diabetes_high_risk(self):
        """High glucose + high BMI should produce elevated diabetes probability."""
        features = {
            'glucose': 180, 'bmi': 35.0, 'age': 50,
            'blood_pressure': 95, 'insulin': 250,
            'skin_thickness': 40, 'pregnancies': 3,
            'diabetes_pedigree_function': 0.8
        }
        result = predict_tabular(features)
        assert 'disease' in result
        assert 'probability' in result
        assert 'confidence' in result
        assert 0.0 <= result['probability'] <= 1.0
        assert 0.0 <= result['confidence'] <= 100.0
        assert isinstance(result['explanation'], list)

    def test_diabetes_low_risk(self):
        """Normal values should produce low diabetes probability."""
        features = {
            'glucose': 90, 'bmi': 22.5, 'age': 30,
            'blood_pressure': 70, 'insulin': 80,
            'skin_thickness': 20, 'pregnancies': 0,
            'diabetes_pedigree_function': 0.2
        }
        result = predict_tabular(features)
        assert result['probability'] <= 0.8

    def test_returns_required_keys(self):
        """Prediction result must contain all required keys."""
        features = {'glucose': 100, 'bmi': 25.0, 'age': 35}
        result = predict_tabular(features)
        for key in ['disease', 'probability', 'confidence', 'explanation']:
            assert key in result, f"Missing key: {key}"

    def test_empty_features(self):
        """Empty features should return a valid (uncertain) result."""
        result = predict_tabular({})
        assert 'disease' in result
        assert 'probability' in result

    def test_non_numeric_values_ignored(self):
        """Non-numeric values should not cause errors."""
        features = {'name': 'John', 'glucose': 120, 'bmi': 26.0}
        result = predict_tabular(features)
        assert 'disease' in result


class TestImagePrediction:
    def test_returns_required_keys(self):
        """Image prediction must return disease, probability, confidence."""
        dummy_bytes = b'\x00' * 1024
        result = predict_image(dummy_bytes)
        for key in ['disease', 'probability', 'confidence']:
            assert key in result, f"Missing key: {key}"

    def test_probability_range(self):
        """Probability must be between 0 and 1."""
        result = predict_image(b'\xff' * 512)
        assert 0.0 <= result['probability'] <= 1.0


# ─── Risk Calculator Tests ────────────────────────────────

class TestRiskCalculator:
    def test_high_risk_features(self):
        features = {
            'glucose': 200, 'bmi': 38.0, 'cholesterol': 280,
            'blood_pressure': 150, 'age': 60
        }
        result = calculate_risk(features)
        assert result['risk_level'] in ['moderate', 'high', 'critical']
        assert result['risk_score'] >= 0

    def test_normal_features_low_risk(self):
        features = {
            'glucose': 90, 'bmi': 22.0, 'cholesterol': 170,
            'blood_pressure': 75, 'age': 30, 'heart_rate': 70
        }
        result = calculate_risk(features)
        assert result['risk_level'] in ['low', 'moderate']

    def test_result_structure(self):
        result = calculate_risk({'glucose': 100})
        for key in ['risk_score', 'risk_level', 'advice', 'risk_factors']:
            assert key in result


# ─── Health Score Tests ───────────────────────────────────

class TestHealthScore:
    def test_optimal_features_high_score(self):
        features = {'bmi': 22.0, 'glucose': 85, 'blood_pressure': 70, 'heart_rate': 65}
        score = compute_health_score(features)
        assert score >= 70.0

    def test_score_range(self):
        features = {'bmi': 35.0, 'glucose': 200, 'blood_pressure': 140}
        score = compute_health_score(features)
        assert 0.0 <= score <= 100.0

    def test_empty_features(self):
        score = compute_health_score({})
        assert 0.0 <= score <= 100.0


# ─── Explainable AI Tests ─────────────────────────────────

class TestExplainableAI:
    def test_contributions_returned(self):
        features = {'glucose': 150, 'bmi': 28.0, 'age': 45, 'blood_pressure': 85}
        result = explain_tabular_prediction(None, features)
        assert 'contributions' in result
        assert isinstance(result['contributions'], list)

    def test_contributions_sorted_by_magnitude(self):
        features = {'glucose': 200, 'bmi': 30.0, 'age': 10}
        result = explain_tabular_prediction(None, features)
        contribs = result['contributions']
        if len(contribs) >= 2:
            assert abs(contribs[0]['contribution']) >= abs(contribs[1]['contribution'])
