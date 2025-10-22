from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .middleware import RateLimitMiddleware
from .api import auth_router, sessions_router, websocket_router, files_router
from .logging_config import setup_logging

settings = get_settings()

# Initialize logging system with rotating file handler (3MB x 3 files)
logger = setup_logging(log_dir=settings.LOG_DIR, log_file="app.log")
logger.info("=" * 80)
logger.info("🚀 Claude Code Remote Web Controller - Starting")
logger.info("=" * 80)
logger.info(f"Server: {settings.HOST}:{settings.PORT}")
logger.info(f"Debug mode: {settings.DEBUG}")
logger.info(f"Claude Code: {settings.CLAUDE_CODE_PATH}")
logger.info(f"Working Directory: {settings.CLAUDE_WORKING_DIRECTORY}")
logger.info(f"Log Directory: {settings.LOG_DIR}")
logger.info("=" * 80)

app = FastAPI(
    title="Claude Code Remote Controller API",
    description="Backend API for remote Claude Code control",
    version="0.1.0",
    debug=settings.DEBUG
)

# Add CORS middleware first (handles preflight requests before rate limiting)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware (T121-T122)
app.add_middleware(RateLimitMiddleware, requests_per_minute=10)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(sessions_router, prefix="/api/v1")
app.include_router(files_router, prefix="/api/v1")
app.include_router(websocket_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "claude-remote-backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
