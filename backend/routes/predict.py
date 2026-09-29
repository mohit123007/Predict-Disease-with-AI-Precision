from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from backend.services.auth_service import get_current_user
from backend.controllers.prediction_controller import predict_tabular_controller, predict_image_controller
from ai_modules.history_manager import save_prediction, get_history, get_stats
from ai_modules.explainable_ai import explain_tabular_prediction

router = APIRouter()
HISTORY_LOG = 'generated_reports/charts/predictions.log'


class TabularRequest(BaseModel):
    features: Dict[str, Any]


@router.post('/tabular')
async def predict_tabular_route(payload: TabularRequest, user=Depends(get_current_user)):
    """Endpoint for tabular/structured data disease prediction."""
    try:
        result = predict_tabular_controller(payload.features)
        # Add explainability
        explain = explain_tabular_prediction(None, payload.features)
        result['top_features'] = explain.get('contributions', [])[:3]
        username = user.get('sub') or user.get('username', 'anonymous')
        save_prediction(HISTORY_LOG, username, result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/image')
async def predict_image_route(file: UploadFile = File(...), user=Depends(get_current_user)):
    """Endpoint for medical image prediction (X-ray, MRI, CT)."""
    contents = await file.read()
    try:
        result = predict_image_controller(contents)
        username = user.get('sub') or user.get('username', 'anonymous')
        save_prediction(HISTORY_LOG, username, {'type': 'image', **result})
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/history')
async def prediction_history(user=Depends(get_current_user)):
    """Get prediction history for the current user."""
    try:
        username = user.get('sub') or user.get('username', 'anonymous')
        history = get_history(username, limit=20)
        stats = get_stats(username)
        return {'history': history, 'stats': stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
