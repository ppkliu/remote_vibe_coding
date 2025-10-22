from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .middleware import RateLimitMiddleware
from .api import auth_router, sessions_router, websocket_router, files_router

settings = get_settings()

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
