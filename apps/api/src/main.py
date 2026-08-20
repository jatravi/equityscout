from fastapi import FastAPI
from apps.api.src.routes.research_runs import router as research_runs_router
from apps.api.src.routes.reports import router as reports_router

app = FastAPI(title="EquityScout API", version="0.1.0")

app.include_router(research_runs_router, prefix="/research-runs", tags=["research-runs"])
app.include_router(reports_router, prefix="/reports", tags=["reports"])


@app.get("/health")
def health():
    return {"status": "ok"}