"""Tkinter-based GUI for editing job shop plans."""

from __future__ import annotations

import json
import tkinter as tk
from dataclasses import asdict
from tkinter import filedialog, messagebox, ttk
from typing import Any

from .models import Job, Operation


class PlanEditor(tk.Tk):
    """Simple GUI for importing, editing, and exporting plans."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Job Shop Plan Editor")
        self.geometry("900x600")

        self.jobs: list[Job] = []
        self.selected_job_index: int | None = None

        self._build_layout()

    def _build_layout(self) -> None:
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=8, pady=8)

        ttk.Button(toolbar, text="Import Plan", command=self.import_plan).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Export Plan", command=self.export_plan).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(toolbar, text="Add Job", command=self.add_job).pack(side=tk.LEFT, padx=(24, 0))
        ttk.Button(toolbar, text="Add Operation", command=self.add_operation).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(toolbar, text="Remove", command=self.remove_selected).pack(side=tk.LEFT, padx=(8, 0))

        main = ttk.Frame(self)
        main.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        jobs_frame = ttk.LabelFrame(main, text="Jobs")
        jobs_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        self.jobs_list = tk.Listbox(jobs_frame)
        self.jobs_list.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.jobs_list.bind("<<ListboxSelect>>", self._on_job_select)

        operations_frame = ttk.LabelFrame(main, text="Operations")
        operations_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.operations_list = tk.Listbox(operations_frame)
        self.operations_list.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        self.operations_list.bind("<Button-1>", self._on_drag_start)
        self.operations_list.bind("<B1-Motion>", self._on_drag_motion)
        self.operations_list.bind("<ButtonRelease-1>", self._on_drag_drop)

        details_frame = ttk.LabelFrame(self, text="Selection Details")
        details_frame.pack(fill=tk.X, padx=8, pady=(0, 8))

        self.details_var = tk.StringVar(value="Select a job and operation to edit.")
        ttk.Label(details_frame, textvariable=self.details_var).pack(anchor=tk.W, padx=6, pady=6)

        self.operations_list.bind("<<ListboxSelect>>", self._on_operation_select)

    def import_plan(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            messagebox.showerror("Import failed", str(exc))
            return

        self.jobs = [self._job_from_dict(item) for item in payload.get("jobs", [])]
        self.selected_job_index = None
        self._refresh_jobs()
        self._refresh_operations()

    def export_plan(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not path:
            return
        payload = {"jobs": [self._job_to_dict(job) for job in self.jobs]}
        try:
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2)
        except OSError as exc:
            messagebox.showerror("Export failed", str(exc))

    def add_job(self) -> None:
        job_id = f"job-{len(self.jobs) + 1}"
        self.jobs.append(Job(job_id=job_id, operations=[]))
        self._refresh_jobs()

    def add_operation(self) -> None:
        if self.selected_job_index is None:
            messagebox.showwarning("Select job", "Choose a job before adding operations.")
            return
        operation_id = f"op-{len(self.jobs[self.selected_job_index].operations) + 1}"
        new_operation = Operation(operation_id=operation_id, machine_id="machine-1", duration=1.0)
        job = self.jobs[self.selected_job_index]
        updated_ops = list(job.operations) + [new_operation]
        self.jobs[self.selected_job_index] = Job(job_id=job.job_id, operations=updated_ops, metadata=job.metadata)
        self._refresh_operations()

    def remove_selected(self) -> None:
        if self.operations_list.curselection():
            self._remove_operation()
            return
        if self.selected_job_index is not None:
            self.jobs.pop(self.selected_job_index)
            self.selected_job_index = None
            self._refresh_jobs()
            self._refresh_operations()

    def _remove_operation(self) -> None:
        if self.selected_job_index is None:
            return
        selection = self.operations_list.curselection()
        if not selection:
            return
        index = selection[0]
        job = self.jobs[self.selected_job_index]
        updated_ops = list(job.operations)
        updated_ops.pop(index)
        self.jobs[self.selected_job_index] = Job(job_id=job.job_id, operations=updated_ops, metadata=job.metadata)
        self._refresh_operations()

    def _on_job_select(self, _event: tk.Event) -> None:
        selection = self.jobs_list.curselection()
        if not selection:
            return
        self.selected_job_index = selection[0]
        self._refresh_operations()

    def _on_operation_select(self, _event: tk.Event) -> None:
        if self.selected_job_index is None:
            return
        selection = self.operations_list.curselection()
        if not selection:
            return
        operation = self.jobs[self.selected_job_index].operations[selection[0]]
        self.details_var.set(
            f"Operation {operation.operation_id} on {operation.machine_id} "
            f"(duration {operation.duration}, setup {operation.setup_time})"
        )

    def _refresh_jobs(self) -> None:
        self.jobs_list.delete(0, tk.END)
        for job in self.jobs:
            self.jobs_list.insert(tk.END, job.job_id)

    def _refresh_operations(self) -> None:
        self.operations_list.delete(0, tk.END)
        if self.selected_job_index is None:
            return
        for operation in self.jobs[self.selected_job_index].operations:
            label = f"{operation.operation_id} | {operation.machine_id} | {operation.duration}"
            self.operations_list.insert(tk.END, label)

    def _job_to_dict(self, job: Job) -> dict[str, Any]:
        return {
            "job_id": job.job_id,
            "operations": [asdict(op) for op in job.operations],
            "metadata": job.metadata,
        }

    def _job_from_dict(self, payload: dict[str, Any]) -> Job:
        operations = [Operation(**op) for op in payload.get("operations", [])]
        return Job(job_id=payload["job_id"], operations=operations, metadata=payload.get("metadata", {}))

    def _on_drag_start(self, event: tk.Event) -> None:
        self._drag_start_index = self.operations_list.nearest(event.y)

    def _on_drag_motion(self, event: tk.Event) -> None:
        if self.selected_job_index is None:
            return
        target_index = self.operations_list.nearest(event.y)
        if target_index != self._drag_start_index:
            self._swap_operations(self._drag_start_index, target_index)
            self._drag_start_index = target_index

    def _on_drag_drop(self, _event: tk.Event) -> None:
        self._drag_start_index = None

    def _swap_operations(self, index_a: int, index_b: int) -> None:
        if self.selected_job_index is None:
            return
        job = self.jobs[self.selected_job_index]
        operations = list(job.operations)
        operations[index_a], operations[index_b] = operations[index_b], operations[index_a]
        self.jobs[self.selected_job_index] = Job(job_id=job.job_id, operations=operations, metadata=job.metadata)
        self._refresh_operations()
        self.operations_list.selection_set(index_b)


def main() -> None:
    editor = PlanEditor()
    editor.mainloop()


if __name__ == "__main__":
    main()
