import uvicorn
import traceback
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
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

# Add exception handler for detailed error messages
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_detail = {
        "error": str(exc),
        "traceback": traceback.format_exc()
    }
    print(f"ERROR: {error_detail}")
    return JSONResponse(
        status_code=500,
        content=error_detail,
    )

# Include API routes
app.include_router(router)

# Mount static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import os
    
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 12000))
    
    uvicorn.run("debug_server:app", host="0.0.0.0", port=port, reload=True)