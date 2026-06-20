from fastapi import FastAPI
from app.api import endpoints
from app.core.services import services

app = FastAPI(title="Semantic Analytical Copilot API")

@app.on_event("startup")
async def startup_event():
    services.init_services()

# Include API routes
app.include_router(endpoints.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Semantic Analytical Copilot API",
        "status": "online",
        "services": {
            "semantic": "initialized" if services.semantic_service else "failed",
            "rag": "initialized" if services.rag_service else "failed"
        }
    }
