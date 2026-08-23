from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Optional
from sqlalchemy.orm import Session

from apps.api.src.models import Company, CompanyAlias


@dataclass
class ResolvedCompany:
    company_id: str
    legal_name: str
    nse_symbol: Optional[str]
    bse_code: Optional[str]
    matched_alias: Optional[str]
    confidence: float
    match_type: str  # EXACT_LEGAL_NAME | EXACT_ALIAS | FUZZY_ALIAS


class CompanyUnresolvedError(Exception):
    pass


def _normalize(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


class CompanyResolver:
    def __init__(self, db: Session):
        self.db = db

    def resolve(self, input_text: str) -> ResolvedCompany:
        if not input_text or not input_text.strip():
            raise CompanyUnresolvedError("Company input is empty")

        raw = input_text.strip()
        norm = _normalize(raw)

        # 1) exact legal name
        companies = self.db.query(Company).all()
        for c in companies:
            if _normalize(c.legal_name) == norm:
                return ResolvedCompany(
                    company_id=str(c.id),
                    legal_name=c.legal_name,
                    nse_symbol=getattr(c, "nse_symbol", None),
                    bse_code=getattr(c, "bse_code", None),
                    matched_alias=c.legal_name,
                    confidence=1.0,
                    match_type="EXACT_LEGAL_NAME",
                )

        # 2) exact alias
        aliases = self.db.query(CompanyAlias).all()
        for a in aliases:
            if _normalize(a.alias) == norm:
                c = self.db.query(Company).filter(Company.id == a.company_id).first()
                if c:
                    return ResolvedCompany(
                        company_id=str(c.id),
                        legal_name=c.legal_name,
                        nse_symbol=getattr(c, "nse_symbol", None),
                        bse_code=getattr(c, "bse_code", None),
                        matched_alias=a.alias,
                        confidence=float(a.confidence) if a.confidence is not None else 0.95,
                        match_type="EXACT_ALIAS",
                    )

        # 3) normalized fuzzy alias
        best_score = 0.0
        best_alias = None
        best_company = None
        best_confidence = 0.0

        for a in aliases:
            alias_norm = _normalize(a.alias)
            score = _similarity(norm, alias_norm)
            if score > best_score:
                c = self.db.query(Company).filter(Company.id == a.company_id).first()
                if c:
                    best_score = score
                    best_alias = a.alias
                    best_company = c
                    alias_conf = float(a.confidence) if a.confidence is not None else 0.7
                    best_confidence = min(0.95, (0.6 * score) + (0.4 * alias_conf))

        # threshold for fuzzy acceptance
        if best_company and best_score >= 0.80:
            return ResolvedCompany(
                company_id=str(best_company.id),
                legal_name=best_company.legal_name,
                nse_symbol=getattr(best_company, "nse_symbol", None),
                bse_code=getattr(best_company, "bse_code", None),
                matched_alias=best_alias,
                confidence=round(best_confidence, 3),
                match_type="FUZZY_ALIAS",
            )

        # 4) fallback unresolved
        raise CompanyUnresolvedError(f"Unable to resolve company for input: '{raw}'")