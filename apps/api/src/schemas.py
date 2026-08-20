from pydantic import BaseModel
from typing import Optional, List

class CreateResearchRunRequest(BaseModel):
    company: str

class CreateResearchRunResponse(BaseModel):
    runId: str
    status: str
    company: str

class ResearchTaskOut(BaseModel):
    id: str
    taskType: str
    status: str

class ResearchRunOut(BaseModel):
    runId: str
    company: str
    status: str
    startedAt: Optional[str] = None
    finishedAt: Optional[str] = None
    errorMessage: Optional[str] = None
    tasks: List[ResearchTaskOut]

class ReportOut(BaseModel):
    runId: str
    markdown: str
    validationStatus: str