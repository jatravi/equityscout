from sqlalchemy.orm import Session
from models import Report

def get_report_by_run_id(db: Session, run_id: str):
    return db.query(Report).filter(Report.run_id == run_id).first()