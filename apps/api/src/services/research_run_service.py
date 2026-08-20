import uuid
from sqlalchemy.orm import Session
from models import Company, ResearchRun, ResearchTask

DEFAULT_TASKS = ["BUSINESS", "FINANCIAL", "PROMOTER"]

def create_research_run(db: Session, company_name: str):
    company = db.query(Company).filter(Company.legal_name == company_name, Company.market == "IN").first()
    if not company:
        company = Company(id=uuid.uuid4(), legal_name=company_name, market="IN")
        db.add(company)
        db.flush()

    run = ResearchRun(
        id=uuid.uuid4(),
        company_id=company.id,
        input_company_text=company_name,
        status="PENDING",
    )
    db.add(run)
    db.flush()

    for t in DEFAULT_TASKS:
        db.add(ResearchTask(id=uuid.uuid4(), run_id=run.id, task_type=t, status="PENDING"))

    db.commit()
    db.refresh(run)
    return run, company

def get_research_run(db: Session, run_id: str):
    run = db.query(ResearchRun).filter(ResearchRun.id == run_id).first()
    if not run:
        return None
    company = db.query(Company).filter(Company.id == run.company_id).first()
    tasks = db.query(ResearchTask).filter(ResearchTask.run_id == run.id).all()
    return run, company, tasks