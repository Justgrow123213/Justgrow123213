import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from real_estate_agents.api.routes import router

app = FastAPI(title="Real Estate Multi-Agent System")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

# Mount static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import os
    
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 8000))
    
    # In Docker, we want to use port 8000
    # In development environment, we might want to use port 12000
    if os.environ.get("DOCKER_ENV") == "true":
        port = 8000
    
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)