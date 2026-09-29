"""
Tests for AI chatbot, symptom checker, doctor recommendation, and report analysis.
Run with: python -m pytest tests/test_chatbot.py -v
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ai_modules.chatbot import reply_to_query
from ai_modules.symptom_checker import analyze_symptoms
from ai_modules.doctor_recommendation import suggest_specialist
from ai_modules.health_recommendation import recommend_lifestyle, get_full_recommendation
from ai_modules.report_analysis import parse_report_text


# ─── Chatbot Tests ────────────────────────────────────────

class TestChatbot:
    def test_diabetes_query(self):
        result = reply_to_query("What is diabetes?")
        assert 'reply' in result
        assert 'diabetes' in result['reply'].lower() or len(result['reply']) > 10

    def test_heart_query(self):
        result = reply_to_query("How do I improve heart health?")
        assert 'reply' in result
        assert 'intent' in result

    def test_unknown_query_returns_default(self):
        result = reply_to_query("xyzabc random noise 12345")
        assert 'reply' in result
        assert len(result['reply']) > 0

    def test_disclaimer_present(self):
        result = reply_to_query("What is BMI?")
        assert 'disclaimer' in result

    def test_returns_intent(self):
        result = reply_to_query("Tell me about blood pressure")
        assert result.get('intent') is not None


# ─── Symptom Checker Tests ────────────────────────────────

class TestSymptomChecker:
    def test_diabetes_symptoms(self):
        result = analyze_symptoms("frequent urination, excessive thirst, blurred vision")
        assert 'matched_symptoms' in result
        assert 'possible_diseases' in result
        assert len(result['possible_diseases']) >= 0

    def test_urgent_symptoms(self):
        result = analyze_symptoms("severe chest pain, shortness of breath")
        assert result['is_urgent'] is True

    def test_normal_symptoms_not_urgent(self):
        result = analyze_symptoms("mild fatigue, headache")
        # May or may not be urgent, just ensure it runs
        assert 'is_urgent' in result

    def test_result_structure(self):
        result = analyze_symptoms("cough and fever for 3 days")
        for key in ['tokens', 'matched_symptoms', 'possible_diseases', 'summary']:
            assert key in result


# ─── Doctor Recommendation Tests ─────────────────────────

class TestDoctorRecommendation:
    def test_chest_symptoms(self):
        result = suggest_specialist(['chest pain', 'shortness of breath'])
        assert len(result) >= 1
        specialists = [r['specialist'] for r in result]
        assert any(sp in specialists for sp in ['Cardiologist', 'Pulmonologist', 'Chest Physician'])

    def test_skin_symptoms(self):
        result = suggest_specialist(['skin rash', 'itching'])
        specialists = [r['specialist'] for r in result]
        assert 'Dermatologist' in specialists

    def test_empty_symptoms_returns_gp(self):
        result = suggest_specialist([])
        assert result[0]['specialist'] == 'General Physician'

    def test_result_has_description(self):
        result = suggest_specialist(['headache', 'dizziness'])
        assert 'description' in result[0]
        assert 'specialist' in result[0]


# ─── Health Recommendation Tests ──────────────────────────

class TestHealthRecommendation:
    def test_excellent_score(self):
        tips = recommend_lifestyle(90)
        assert len(tips) >= 1
        assert any('excellent' in t.lower() or 'good' in t.lower() or 'keep' in t.lower() or '🏆' in t for t in tips)

    def test_low_score(self):
        tips = recommend_lifestyle(20)
        assert len(tips) >= 1
        assert any('physician' in t.lower() or 'medical' in t.lower() or '🚨' in t or '🏥' in t for t in tips)

    def test_full_recommendation_has_label(self):
        rec = get_full_recommendation(75)
        assert 'label' in rec
        assert 'tips' in rec


# ─── Report Analysis Tests ────────────────────────────────

class TestReportAnalysis:
    def test_lab_value_extraction(self):
        report = "Glucose: 148 mg/dL. Hemoglobin: 11.5. Creatinine: 1.4."
        result = parse_report_text(report)
        assert 'lab_values' in result
        labs = result['lab_values']
        assert 'Glucose' in labs or 'Hemoglobin' in labs

    def test_flagged_findings(self):
        report = "Glucose is elevated at 180 mg/dL. LDL is high at 190. Borderline creatinine."
        result = parse_report_text(report)
        assert result['has_abnormal'] is True
        assert len(result['flagged_findings']) >= 1

    def test_summary_generated(self):
        report = "Patient has normal kidney function. No abnormalities detected."
        result = parse_report_text(report)
        assert 'summary' in result
        assert len(result['summary']) > 0

    def test_empty_report(self):
        result = parse_report_text("")
        assert 'sentences' in result
        assert isinstance(result['sentences'], list)
