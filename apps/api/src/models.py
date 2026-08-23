from sqlalchemy import Boolean, Column, Numeric, String, Text, ForeignKey, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from apps.api.src.db import Base
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import Float

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


class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True)
    run_id = Column(UUID(as_uuid=True), ForeignKey("research_runs.id"), nullable=False, unique=True)
    markdown = Column(Text, nullable=False)
    validation_status = Column(String, nullable=False, default="PENDING")
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())