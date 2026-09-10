from fastapi import FastAPI

from apps.api.src.routes.research_runs import router as research_runs_router
from apps.api.src.routes.reports import router as reports_router
from apps.api.src.routes.discovery import router as discovery_router
from apps.api.src.routes.companies import router as companies_router
from apps.api.src.routes.documents import router as documents_router
from apps.api.src.routes.evidence import router as evidence_router
from apps.api.src.routes.claims import router as claims_router
from apps.api.src.routes.report import router as report_router
from apps.api.src.routes.diagnostics import router as diagnostics_router

app = FastAPI(title="EquityScout API", version="0.1.0")

app.include_router(research_runs_router, prefix="/research-runs", tags=["research-runs"])
app.include_router(reports_router, prefix="/reports", tags=["reports"])
app.include_router(companies_router, prefix="/companies", tags=["companies"])
app.include_router(discovery_router, prefix="/research-runs", tags=["discovery"])
app.include_router(documents_router, tags=["documents"])
app.include_router(evidence_router, tags=["evidence"])
app.include_router(claims_router, tags=["claims"])
app.include_router(report_router, tags=["report"])
app.include_router(diagnostics_router, tags=["diagnostics"])

@app.get("/health")
def health():
    return {"status": "ok"}