# Job Shop Scheduler

A scheduling system for job shop and manufacturing environments.

This project focuses on generating feasible and practical production schedules
under real-world constraints such as machine availability, operation precedence,
setup times, and finite capacity.

## Quick start

```python
from job_shop_scheduler import GreedyScheduler, Job, Machine, Operation

jobs = [
    Job(
        job_id="job-1",
        operations=[
            Operation(operation_id="op-1", machine_id="m1", duration=3.0, setup_time=0.5),
            Operation(operation_id="op-2", machine_id="m2", duration=2.0),
        ],
    ),
    Job(
        job_id="job-2",
        operations=[
            Operation(operation_id="op-1", machine_id="m2", duration=4.0),
            Operation(operation_id="op-2", machine_id="m1", duration=1.0),
        ],
    ),
]

machines = [Machine(machine_id="m1"), Machine(machine_id="m2")]

schedule = GreedyScheduler().schedule(jobs, machines)
print(schedule.makespan)
```

## GUI plan editor

Launch the Tkinter editor to import, reorder, and export plans:

```bash
python -m job_shop_scheduler.gui
```

The GUI supports:
- Importing plans from JSON (containing a list of jobs and operations)
- Drag-and-drop reordering of operations within a job
- Exporting the updated plan back to JSON
