from fastapi import FastAPI
from routes import health, travel, user
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from utils.files import static_dir, ensure_dir

app = FastAPI(
    title="Travel Planner API",
    description="AI-powered travel planning backend",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(travel.router)
app.include_router(user.router)

# Mount static directory for generated images
ensure_dir(static_dir())
app.mount("/static", StaticFiles(directory=static_dir()), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
