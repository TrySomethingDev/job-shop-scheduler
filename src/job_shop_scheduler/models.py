"""Core data structures for job shop scheduling."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence


@dataclass(frozen=True)
class Operation:
    """A single operation in a job's routing."""

    operation_id: str
    machine_id: str
    duration: float
    setup_time: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def total_time(self) -> float:
        return self.duration + self.setup_time


@dataclass(frozen=True)
class Job:
    """A job consisting of ordered operations."""

    job_id: str
    operations: Sequence[Operation]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Machine:
    """A machine resource with a known availability."""

    machine_id: str
    available_from: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ScheduleItem:
    """Scheduled timing for an operation on a machine."""

    job_id: str
    operation_id: str
    machine_id: str
    start_time: float
    end_time: float
    setup_time: float = 0.0
