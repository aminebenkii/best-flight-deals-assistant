from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from app.backend.api.chat_api import router
from fastapi.middleware.cors import CORSMiddleware

# ─────────────────────────────────────────────
# PATH CONFIGURATION
PROJECT_ROOT_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = PROJECT_ROOT_DIR / "app" / "frontend"
STATIC_DIR = FRONTEND_DIR / "static"
INDEX_FILE_PATH = FRONTEND_DIR / "index.html"

# ─────────────────────────────────────────────
# FASTAPI APPLICATION INITIALIZATION
app = FastAPI(title="Flight Deals Chatbot API", version="1.0.0")

# ─────────────────────────────────────────────
# MIDDLEWARE (for CORS during development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# ROUTES AND STATIC FILES
app.include_router(router)

# Serve static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Serve main frontend page
@app.get("/", response_class=FileResponse)
def serve_homepage():
    """Serves the main chat frontend page."""
    return FileResponse(INDEX_FILE_PATH)

# Health Check Route
@app.get("/health", response_class=JSONResponse)
def health_check():
    """Basic Health Check Endpoint"""
    return JSONResponse(status_code=200, content={"status": "ok"})