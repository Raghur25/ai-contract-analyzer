from fastapi import FastAPI

from app.database import init_db
from app.routes.analysis import router as analysis_router
from app.routes.contracts import router as contracts_router

app = FastAPI(
    title="Vakeel Contacts API",
    description="AI-Powered Contact Analysis using Gemini",
    version="1.0.0",
)

@app.on_event("startup")
async def startup_event():
    init_db()  # Initialize the database and create indexes

@app.get("/")
async def root():
    return {
        "app": "Vakeel Contacts API!",
        "version": "1.0.0",
        "endpoints": {
            "POST /contracts/upload": "Upload a PDF or TXT contact for analysis",
            "GET/contracts/": "Retrieve a list of all uploaded contacts",
            "GET /contracts/{id}": "Retrieve details of a specific contract by ID",
            "POST /analysis/analyse/{contact_id}":"Analyse a contract using AI and return insights",
            "GET /analysis/{analysis_id}": "Retrieve the results of a specific analysis by ID",
            "GET/ analysis/contract/{contract_id}": "Retrieve a list of all analyses performed for a specific contract by ID"
        }
        }
    
app.include_router(contracts_router)
app.include_router(analysis_router)