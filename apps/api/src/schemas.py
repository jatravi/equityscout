from __future__ import annotations

from pydantic import BaseModel
from typing import Literal, Optional, List, Any
from datetime import datetime

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

class CompanyResolveRequest(BaseModel):
    company: str


class CompanyResolveResponse(BaseModel):
    companyId: str
    legalName: str
    nseSymbol: Optional[str] = None
    bseCode: Optional[str] = None
    matchedAlias: Optional[str] = None
    confidence: float
    matchType: str


class IngestDocsResponse(BaseModel):
    runId: str
    totalSources: int
    fetched: int
    deduped: int
    parsed: int
    failed: int


class DocumentItem(BaseModel):
    documentId: str
    sourceId: str | None = None
    url: str
    canonicalUrl: str
    contentHash: str
    httpStatus: int | None = None
    contentType: str | None = None
    fetchedAt: datetime
    parserStatus: str
    parseTitle: str | None = None
    parseLength: int | None = None
    parseMetadata: dict[str, Any] | None = None


class DocumentsListResponse(BaseModel):
    runId: str
    items: list[DocumentItem]

EvidenceType = Literal["BUSINESS_SIGNAL", "FINANCIAL_METRIC", "PROMOTER_HOLDING"]

class ExtractEvidenceResponse(BaseModel):
    runId: str
    processedDocuments: int
    extracted: int
    deduped: int
    failedDocuments: int
    countsByType: dict[str, int]

class EvidenceItem(BaseModel):
    evidenceId: str
    runId: str
    companyId: str
    documentId: str
    evidenceType: EvidenceType
    key: str
    valueText: str | None = None
    valueNum: float | None = None
    valueUnit: str | None = None
    period: str | None = None
    confidence: float
    locator: dict[str, Any]
    snippet: str | None = None
    createdAt: datetime

class EvidenceListResponse(BaseModel):
    runId: str
    items: list[EvidenceItem]

class GenerateReportResponse(BaseModel):
    runId: str
    version: str
    verdictLabel: str
    verdictSummary: str
    citationCount: int
    reportMarkdown: str
    createdAt: datetime | None = None

class ReportResponse(BaseModel):
    runId: str
    version: str
    verdictLabel: str
    verdictSummary: str
    citationCount: int
    reportMarkdown: str
    createdAt: datetime