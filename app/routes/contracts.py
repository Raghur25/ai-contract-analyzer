import asyncio
import os
import uuid
from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB, UPLOAD_DIR
from app.database import contracts_collection
from app.models import Contract
from app.service.document_parser import extract_text

router = APIRouter(
    prefix="/contracts",
    tags=["contracts"],
)


def _write_file(path: str, content: bytes) -> None:
    with open(path, "wb") as f:
        f.write(content)


@router.post("/upload")
async def upload_contract(
    file: Annotated[UploadFile, File()],
):
    """
    Upload a PDF or TXT contract for analysis.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is missing")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="File type not allowed")

    content = await file.read()

    size_mb = len(content) / (1024 * 1024)

    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=400, detail="File size exceeds the maximum limit")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    unique_name = f"{uuid.uuid4().hex}{ext}"

    file_path = os.path.join(UPLOAD_DIR, unique_name)

    await asyncio.to_thread(_write_file, file_path, content)

    try:
        parsed = extract_text(file_path)

        contract_data = Contract(
            filename=unique_name,
            original_name=file.filename,
            text_content=parsed["text"],
            page_count=int(parsed["page_count"]),
            word_count=int(parsed["word_count"]),
        )

        doc = contract_data.model_dump()
        result = contracts_collection.insert_one(doc)
        contract_data.id = str(result.inserted_id)
    except Exception as e:
        # Don't leave an orphan file on disk if parsing or saving fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to process contract: {e}") from e

    return {
        "message": "File uploaded and processed successfully",
        "contract": contract_data.model_dump(),
        "id": contract_data.id
    }


@router.get("/")
async def list_contracts():
    """
    List all uploaded contracts
    """
    contracts = []
    for doc in contracts_collection.find({}, {"text_content": 0}):
        contract = Contract(**doc)
        contract.id = str(doc["_id"])
        contracts.append(contract.model_dump())

    return {"contracts": contracts}


@router.get("/{contract_id}")
async def get_contract(contract_id: str):
    """
    Retrieve a specific contract by its ID.
    """
    doc = contracts_collection.find_one({"_id": ObjectId(contract_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Contract not found")

    contract = Contract(**doc)
    contract.id = str(doc["_id"])

    return {"contract": contract.model_dump()}
