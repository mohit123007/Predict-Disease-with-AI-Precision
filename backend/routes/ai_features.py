from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

from backend.services.auth_service import get_current_user
from ai_modules.chatbot import reply_to_query
from ai_modules.symptom_checker import analyze_symptoms
from ai_modules.health_score import compute_health_score
from ai_modules.health_recommendation import recommend_lifestyle
from ai_modules.doctor_recommendation import suggest_specialist
from ai_modules.risk_calculator import calculate_risk
from ai_modules.report_analysis import parse_report_text
from ai_modules.explainable_ai import explain_tabular_prediction
from ai_modules.history_manager import get_history, get_stats

router = APIRouter()


class ChatRequest(BaseModel):
    query: str


class SymptomsRequest(BaseModel):
    symptoms_text: str


class HealthScoreRequest(BaseModel):
    features: Dict[str, Any]


class DoctorRecommendRequest(BaseModel):
    symptoms: List[str]


class RiskRequest(BaseModel):
    features: Dict[str, Any]


class ReportTextRequest(BaseModel):
    text: str


class ExplainRequest(BaseModel):
    features: Dict[str, Any]


@router.post('/chatbot')
async def chatbot_endpoint(payload: ChatRequest, user=Depends(get_current_user)):
    """Medical AI chatbot — returns a knowledge-based reply to the health query."""
    try:
        return reply_to_query(payload.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/symptoms')
async def symptoms_endpoint(payload: SymptomsRequest, user=Depends(get_current_user)):
    """Analyze free-text symptom description and map to possible conditions."""
    try:
        return analyze_symptoms(payload.symptoms_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/health-score')
async def health_score_endpoint(payload: HealthScoreRequest, user=Depends(get_current_user)):
    """Compute a 0–100 health score from biometric features."""
    try:
        score = compute_health_score(payload.features)
        recommendations = recommend_lifestyle(score)
        return {'health_score': round(score, 2), 'recommendations': recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/doctor-recommend')
async def doctor_recommend_endpoint(payload: DoctorRecommendRequest, user=Depends(get_current_user)):
    """Suggest medical specialists based on symptom list."""
    try:
        specialists = suggest_specialist(payload.symptoms)
        return {'specialists': specialists}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/risk')
async def risk_endpoint(payload: RiskRequest, user=Depends(get_current_user)):
    """Calculate risk score and level from biometric/lifestyle features."""
    try:
        return calculate_risk(payload.features)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/upload-report')
async def upload_report_text(payload: ReportTextRequest, user=Depends(get_current_user)):
    """Parse and analyze pasted medical report text."""
    try:
        return parse_report_text(payload.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/upload-report-file')
async def upload_report_file(file: UploadFile = File(...), user=Depends(get_current_user)):
    """Parse an uploaded plain-text medical report file."""
    try:
        content = await file.read()
        text = content.decode('utf-8', errors='ignore')
        return parse_report_text(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/explain')
async def explain_endpoint(payload: ExplainRequest, user=Depends(get_current_user)):
    """Return explainable AI feature contributions for a set of features."""
    try:
        return explain_tabular_prediction(None, payload.features)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/history')
async def history_endpoint(user=Depends(get_current_user)):
    """Retrieve the current user's prediction history."""
    try:
        username = user.get('sub') or user.get('username', 'anonymous')
        history = get_history(username, limit=20)
        stats = get_stats(username)
        return {'history': history, 'stats': stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
