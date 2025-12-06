"""
evaluator.py

High-level evaluation API for running a LeetCode solution, collecting:
- execution time
- memory usage
- stdout
- stderr
- logs
- status codes
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict, Any

from .runner import run_solution_file, ExecutionResult


@dataclass
class EvalResult:
    problem_id: str
    time: Optional[float]
    memory: Optional[float]
    output: str
    error: Optional[str]
    logs: List[str]
    status: str  # "success" | "runtime_error" | "failed"
    workdir: str


def evaluate(problem_id: str, repo_path: str, python_cmd: str = "python") -> EvalResult:
    """
    Main evaluation entry point.
    Finds the problem folder, runs solution.py, collects performance data.
    """

    repo = Path(repo_path)
    if not repo.exists():
        raise RuntimeError(f"Repository path does not exist: {repo_path}")

    # Find folder matching: "<id>-slug"
    target = None
    for folder in repo.iterdir():
        if folder.is_dir() and folder.name.startswith(f"{problem_id}-"):
            target = folder
            break

    if target is None:
        raise RuntimeError(f"No problem folder found for id={problem_id}")

    # Run solution
    raw: ExecutionResult = run_solution_file(target, python_cmd=python_cmd)

    status = "success"
    if raw.returncode != 0:
        status = "runtime_error"

    return EvalResult(
        problem_id=problem_id,
        time=raw.time,
        memory=raw.memory_kb,
        output=raw.stdout,
        error=raw.stderr if raw.stderr else None,
        logs=[raw.stdout, raw.stderr],
        status=status,
        workdir=str(target),
    )
