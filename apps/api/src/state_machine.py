from enum import Enum


class RunStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"


ALLOWED_TRANSITIONS = {
    RunStatus.PENDING: {RunStatus.RUNNING, RunStatus.FAILED},
    RunStatus.RUNNING: {RunStatus.COMPLETED, RunStatus.FAILED, RunStatus.PARTIAL},
    RunStatus.COMPLETED: set(),
    RunStatus.FAILED: set(),
    RunStatus.PARTIAL: set(),
}


def can_transition(current: RunStatus, target: RunStatus) -> bool:
    return target in ALLOWED_TRANSITIONS[current]


def ensure_transition(current: RunStatus, target: RunStatus) -> None:
    if not can_transition(current, target):
        raise ValueError(f"Invalid transition: {current} -> {target}")