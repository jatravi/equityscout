from sqlalchemy.orm import Session
from state_machine import RunStatus, ensure_transition
from models import ResearchRun  # your ORM model


def update_run_status(db: Session, run_id: str, new_status: RunStatus):
    run = db.query(ResearchRun).filter(ResearchRun.id == run_id).first()
    if not run:
        raise ValueError("Run not found")

    current = RunStatus(run.status)
    ensure_transition(current, new_status)

    run.status = new_status.value
    if new_status == RunStatus.RUNNING and run.started_at is None:
        from datetime import datetime, timezone
        run.started_at = datetime.now(timezone.utc)

    if new_status in {RunStatus.COMPLETED, RunStatus.FAILED, RunStatus.PARTIAL}:
        from datetime import datetime, timezone
        run.finished_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(run)
    return run