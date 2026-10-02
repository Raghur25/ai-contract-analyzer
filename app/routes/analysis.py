from bson import ObjectId
from fastapi import APIRouter, HTTPException

from app.config import GEMINI_API_KEY
from app.database import analysis_collection, contracts_collection
from app.service.gemini_analyse import analyze_contract

router = APIRouter(
    prefix="/analysis",
    tags=["analysis"],
)

@router.post("/analyse/{contract_id}")
async def analyse_contract(contract_id: str):
    """
    Analyse a contract using AI and return insights.
    """
    
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API key is not configured")
    
    contract = contracts_collection.find_one({"_id": ObjectId(contract_id)})
    
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    contracts_collection.update_one({"_id": ObjectId(contract_id)}, {"$set": {"status": "in_progress"}})
    
    try:
        result = await analyze_contract(contract_id, contract["text_content"])

        doc = result.model_dump()
        insert_result = analysis_collection.insert_one(doc)
        result.id = str(insert_result.inserted_id)

        contracts_collection.update_one(
            {"_id": ObjectId(contract_id)},
            {"$set": {"status": "analysed", "analysis_status": "completed"}},
        )
    except Exception as e:
        # Don't leave the contract stuck in "in_progress" if the analysis fails
        contracts_collection.update_one(
            {"_id": ObjectId(contract_id)},
            {"$set": {"status": "error", "analysis_status": "failed"}},
        )
        raise HTTPException(status_code=500, detail=f"Contract analysis failed: {e}") from e

    return {
        "message": "Contract analysis completed successfully",
        "analysis": result.model_dump(),
        "id": result.id
    }
    
@router.get("/{analysis_id}")
def get_analysis(analysis_id: str):
    """
    Retrieve the results of a specific analysis by its ID.
    """
    analysis = analysis_collection.find_one({"_id": ObjectId(analysis_id)})
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # ObjectId is not JSON serializable, so return it as a string "id" instead
    analysis["id"] = str(analysis.pop("_id"))

    return {
        "analysis": analysis
    }
    
@router.get('/')
def list_analyses():
    """
    List all analyses performed.
    """
    analyses = []
    for doc in analysis_collection.find({}):
        doc['id'] = str(doc.pop('_id'))
        analyses.append(doc)
        
    return {"analyses": analyses}


@router.get("/contract/{contract_id}")
async def get_analyses_for_contract(contract_id: str):
    """Get all analyses performed for a specific contract."""
    analyses = []
    cursor = analysis_collection.find({"contract_id": contract_id})
    
    for doc in cursor:
        doc['id'] = str(doc.pop('_id'))
        analyses.append(doc)
        
    return {"analyses": analyses, "total": len(analyses)}
