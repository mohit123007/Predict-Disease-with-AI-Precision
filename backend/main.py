import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.routes import auth, predict
from backend.routes.ai_features import router as ai_router

# Ensure required directories exist at startup
for d in [
    'generated_reports/charts', 'generated_reports/pdf',
    'uploads/reports', 'uploads/xrays', 'uploads/mri', 'uploads/profile',
    'frontend/static/images'
]:
    os.makedirs(d, exist_ok=True)

app = FastAPI(
    title='MedPredict — AI Medical Disease Prediction Platform',
    description='AI-powered disease prediction: tabular ML, image CNN, NLP report analysis, chatbot, and health analytics.',
    version='2.0.0'
)

# CORS — restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Static files & Jinja2 templates
app.mount('/static', StaticFiles(directory='frontend/static'), name='static')
templates = Jinja2Templates(directory='frontend/templates')


def _render(name: str, request: Request, ctx: dict = None):
    """Helper: compatible with both old and new Starlette TemplateResponse API."""
    context = ctx or {}
    try:
        # New Starlette >= 0.36: request is first positional arg
        return templates.TemplateResponse(request=request, name=name, context=context)
    except TypeError:
        # Old Starlette: request inside context dict
        context['request'] = request
        return templates.TemplateResponse(name, context)


# Routers
app.include_router(auth.router,  prefix='/auth',    tags=['Authentication'])
app.include_router(predict.router, prefix='/predict', tags=['Prediction'])
app.include_router(ai_router,    prefix='/ai',      tags=['AI Features'])


# ── Page Routes ─────────────────────────────────────────────

@app.get('/')
async def index(request: Request):
    return _render('index.html', request)

@app.get('/login.html')
async def login_page(request: Request):
    return _render('login.html', request)

@app.get('/dashboard.html')
async def dashboard_page(request: Request):
    return _render('dashboard.html', request)

@app.get('/disease_prediction.html')
async def disease_prediction_page(request: Request):
    return _render('disease_prediction.html', request)

@app.get('/chatbot.html')
async def chatbot_page(request: Request):
    return _render('chatbot.html', request)

@app.get('/image_prediction.html')
async def image_prediction_page(request: Request):
    return _render('image_prediction.html', request)

@app.get('/upload_report.html')
async def upload_report_page(request: Request):
    return _render('upload_report.html', request)

@app.get('/doctor_recommendation.html')
async def doctor_recommendation_page(request: Request):
    return _render('doctor_recommendation.html', request)

@app.get('/health_tips.html')
async def health_tips_page(request: Request):
    return _render('health_tips.html', request)

@app.get('/analytics.html')
async def analytics_page(request: Request):
    return _render('analytics.html', request)

@app.get('/profile.html')
async def profile_page(request: Request):
    return _render('profile.html', request)

@app.get('/health')
async def health_check():
    return {'status': 'ok', 'version': '2.0.0'}
