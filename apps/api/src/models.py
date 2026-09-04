from datetime import datetime
import uuid

from sqlalchemy import Boolean, Column, Index, Numeric, String, Text, ForeignKey, Integer, DateTime, LargeBinary, func, Float
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from apps.api.src.db import Base
from sqlalchemy.dialects.postgresql import UUID, JSONB

class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True)
    legal_name = Column(Text, nullable=False)
    market = Column(Text, nullable=False, default="IN")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    nse_symbol = Column(Text, nullable=True)
    bse_code = Column(Text, nullable=True)
    cin = Column(Text, nullable=True)
    is_listed = Column(Boolean, nullable=False, default=True)

class CompanyAlias(Base):
    __tablename__ = "company_aliases"

    id = Column(UUID(as_uuid=True), primary_key=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    alias = Column(Text, nullable=False)
    alias_type = Column(String, nullable=False)
    confidence = Column(Numeric(4, 3), nullable=False, default=1.000)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Source(Base):
    __tablename__ = "sources"

    id = Column(UUID(as_uuid=True), primary_key=True)
    run_id = Column(UUID(as_uuid=True), ForeignKey("research_runs.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    task_type = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    title = Column(Text, nullable=False)
    url = Column(Text, nullable=False)
    publisher = Column(Text, nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    discovered_at = Column(DateTime(timezone=True), server_default=func.now())
    authority_score = Column(Float, nullable=True)
    rank_score = Column(Float, nullable=True)
    metadata_json = Column(JSONB, nullable=True)

class ResearchRun(Base):
    __tablename__ = "research_runs"

    id = Column(UUID(as_uuid=True), primary_key=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    input_company_text = Column(Text, nullable=False)
    status = Column(String, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ResearchTask(Base):
    __tablename__ = "research_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True)
    run_id = Column(UUID(as_uuid=True), ForeignKey("research_runs.id"), nullable=False)
    task_type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    run_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("research_runs.id", ondelete="SET NULL"), nullable=True)
    source_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sources.id", ondelete="SET NULL"), nullable=True)

    url: Mapped[str] = mapped_column(Text, nullable=False)
    canonical_url: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    final_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    http_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content_length: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    raw_bytes: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    parser_status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING", server_default="PENDING")
    parse_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

Index("ux_documents_company_canonical_url", Document.company_id, Document.canonical_url, unique=True)
# Enable only if you chose global hash dedupe:
# Index("ux_documents_content_hash", Document.content_hash, unique=True)

Index("ix_documents_run_id", Document.run_id)
Index("ix_documents_source_id", Document.source_id)
Index("ix_documents_fetched_at", Document.fetched_at)
Index("ix_documents_parser_status", Document.parser_status)

class ParsedDocument(Base):
    __tablename__ = "parsed_documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), unique=True, nullable=False)

    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    plain_text: Mapped[str] = mapped_column(Text, nullable=False)
    text_length: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("research_runs.id", ondelete="CASCADE"), nullable=False
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )

    evidence_type: Mapped[str] = mapped_column(Text, nullable=False)
    key: Mapped[str] = mapped_column(Text, nullable=False)

    value_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    value_num: Mapped[float | None] = mapped_column(Float, nullable=True)
    value_unit: Mapped[str | None] = mapped_column(Text, nullable=True)
    period: Mapped[str | None] = mapped_column(Text, nullable=True)

    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    locator_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    snippet: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("research_runs.id", ondelete="CASCADE"), nullable=False
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )

    claim_type: Mapped[str] = mapped_column(Text, nullable=False)
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    stance: Mapped[str | None] = mapped_column(Text, nullable=True)

    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    contradiction_tag: Mapped[str] = mapped_column(Text, nullable=False, default="NONE")
    contradiction_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    supporting_evidence_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    supporting_locators_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("research_runs.id", ondelete="CASCADE"), nullable=False
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )

    version: Mapped[str] = mapped_column(Text, nullable=False, default="v1")
    verdict_label: Mapped[str] = mapped_column(Text, nullable=False)
    verdict_summary: Mapped[str] = mapped_column(Text, nullable=False)
    report_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    citation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
