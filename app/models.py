from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"   
    CRITICAL = "critical"


class Contract(BaseModel):
    id: str | None = None
    filename: str
    original_name: str
    upload_date: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    text_content: str = ""
    page_count: int = 0
    word_count: int = 0
    status: str = "uploaded"  # uploaded, analysed, error


class ClauseAnalysis(BaseModel):
    clause_title: str
    clause_text: str
    explanation: str  
    is_standard: bool  # low, medium, high
    
class RiskFlag(BaseModel):
    risk_title: str
    description: str
    risk_level: RiskLevel
    recommendation: str 
    clause_reference: str = ""# low, medium, high
    
class AnalysisResult(BaseModel):
    id: str | None = None
    contract_id: str
    analysis_date: str = ""
    summary: str = ""
    contract_type: str = ""
    key_clauses: list[ClauseAnalysis] = []
    risk_flags: list[RiskFlag] = []
    overall_risk_level: RiskLevel = RiskLevel.LOW
    recommendations: list[str] = []