import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.api import calls, scenarios, webhook

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)
settings = get_settings()

app = FastAPI(
    title="Voice AI Agent API",
    description=(
        "Backend for an AI-powered outbound voice call system. "
        "Integrates Vapi for STT + LLM + TTS + telephony."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "null",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(calls.router, prefix="/api")
app.include_router(scenarios.router, prefix="/api")
app.include_router(webhook.router, prefix="/api")


# ── Health check ───────────────────────────────────────────────────────────────
@app.get("/health", tags=["health"])
async def health():
    return {
        "status": "ok",
        "service": "voice-ai-agent",
        "vapi_configured": bool(settings.vapi_api_key and settings.vapi_phone_number_id),
    }


@app.get("/", tags=["root"])
async def root():
    return JSONResponse(
        {
            "message": "Voice AI Agent API",
            "docs": "/docs",
            "health": "/health",
        }
    )
