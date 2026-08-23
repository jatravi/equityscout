from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from apps.api.src.db import get_db
from apps.api.src.schemas import CompanyResolveRequest, CompanyResolveResponse
from apps.api.src.services.company_resolver import CompanyResolver, CompanyUnresolvedError

router = APIRouter()


@router.post("/resolve", response_model=CompanyResolveResponse)
def resolve_company(payload: CompanyResolveRequest, db: Session = Depends(get_db)):
    resolver = CompanyResolver(db)
    try:
        resolved = resolver.resolve(payload.company)
        return CompanyResolveResponse(
            companyId=resolved.company_id,
            legalName=resolved.legal_name,
            nseSymbol=resolved.nse_symbol,
            bseCode=resolved.bse_code,
            matchedAlias=resolved.matched_alias,
            confidence=resolved.confidence,
            matchType=resolved.match_type,
        )
    except CompanyUnresolvedError as e:
        raise HTTPException(status_code=404, detail=str(e))