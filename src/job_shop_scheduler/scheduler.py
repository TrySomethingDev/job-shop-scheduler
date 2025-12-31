"""Scheduling heuristics for job shop environments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import Job, Machine, Operation, ScheduleItem


@dataclass(frozen=True)
class ScheduleResult:
    """Container for schedule output and summary metrics."""

    items: tuple[ScheduleItem, ...]
    makespan: float


class GreedyScheduler:
    """Dispatch operations using a simple greedy rule set."""

    def schedule(self, jobs: Iterable[Job], machines: Iterable[Machine]) -> ScheduleResult:
        jobs_by_id = {job.job_id: job for job in jobs}
        machine_ready = {machine.machine_id: machine.available_from for machine in machines}

        if not jobs_by_id:
            return ScheduleResult(items=(), makespan=0.0)

        self._validate_jobs(jobs_by_id)

        job_ready = {job_id: 0.0 for job_id in jobs_by_id}
        job_indices = {job_id: 0 for job_id in jobs_by_id}
        schedule: list[ScheduleItem] = []

        total_ops = sum(len(job.operations) for job in jobs_by_id.values())
        while len(schedule) < total_ops:
            candidate_ops = self._collect_candidates(jobs_by_id, job_indices)
            next_job_id, operation = self._select_next_operation(candidate_ops, job_ready, machine_ready)

            ready_time = max(job_ready[next_job_id], machine_ready[operation.machine_id])
            start_time = ready_time
            end_time = start_time + operation.total_time

            schedule.append(
                ScheduleItem(
                    job_id=next_job_id,
                    operation_id=operation.operation_id,
                    machine_id=operation.machine_id,
                    start_time=start_time,
                    end_time=end_time,
                    setup_time=operation.setup_time,
                )
            )

            job_ready[next_job_id] = end_time
            machine_ready[operation.machine_id] = end_time
            job_indices[next_job_id] += 1

        makespan = max(item.end_time for item in schedule) if schedule else 0.0
        return ScheduleResult(items=tuple(schedule), makespan=makespan)

    @staticmethod
    def _validate_jobs(jobs_by_id: dict[str, Job]) -> None:
        for job in jobs_by_id.values():
            if not job.operations:
                raise ValueError(f"Job {job.job_id} has no operations to schedule.")
            for operation in job.operations:
                if operation.duration <= 0:
                    raise ValueError(
                        f"Operation {operation.operation_id} in job {job.job_id} "
                        "must have a positive duration."
                    )

    @staticmethod
    def _collect_candidates(
        jobs_by_id: dict[str, Job],
        job_indices: dict[str, int],
    ) -> list[tuple[str, Operation]]:
        candidates: list[tuple[str, Operation]] = []
        for job_id, job in jobs_by_id.items():
            index = job_indices[job_id]
            if index < len(job.operations):
                candidates.append((job_id, job.operations[index]))
        return candidates

    @staticmethod
    def _select_next_operation(
        candidates: Iterable[tuple[str, Operation]],
        job_ready: dict[str, float],
        machine_ready: dict[str, float],
    ) -> tuple[str, Operation]:
        def sort_key(candidate: tuple[str, Operation]) -> tuple[float, float, str]:
            job_id, operation = candidate
            earliest_start = max(job_ready[job_id], machine_ready[operation.machine_id])
            return (earliest_start, operation.total_time, job_id)

        return min(candidates, key=sort_key)
