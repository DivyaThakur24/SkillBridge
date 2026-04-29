from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.database import Base, engine
from src.routes_auth import router as auth_router
from src.routes_batches import router as batches_router
from src.routes_sessions import router as sessions_router
from src.routes_summaries import router as summaries_router

# Create tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="SkillBridge API",
    description="Attendance Management System for SkillBridge",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(batches_router)
app.include_router(sessions_router)
app.include_router(summaries_router)


@app.get("/")
def read_root():
    """Root endpoint."""
    return {
        "message": "Welcome to SkillBridge API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
