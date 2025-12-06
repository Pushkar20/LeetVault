"""
runner.py

Responsible for executing a LeetCode solution file (solution.py)
inside the problem directory and collecting:

- stdout
- stderr
- return code
- execution time
- memory usage

This module uses profiler.run_subprocess() internally.
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import Dict, Any, Optional, List

from .profiler import run_subprocess


class ExecutionResult:
    """
    Represents the raw outcome of running a solution file.
    Contains exactly what the evaluator needs before forming EvalResult.
    """
    def __init__(
        self,
        time: float,
        memory_kb: Optional[float],
        stdout: str,
        stderr: str,
        returncode: int,
        workdir: Path,
    ):
        self.time = time
        self.memory_kb = memory_kb
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode
        self.workdir = workdir

    def to_dict(self) -> Dict[str, Any]:
        return {
            "time": self.time,
            "memory_kb": self.memory_kb,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "returncode": self.returncode,
            "workdir": str(self.workdir),
        }


def run_solution_file(problem_dir: Path, python_cmd: str = "python") -> ExecutionResult:
    """
    Runs the solution.py file inside a problem directory.

    Parameters:
        problem_dir: The directory containing solution.py
        python_cmd: Python command (python, python3, py, etc.)

    Returns:
        ExecutionResult
    """
    solution_path = problem_dir / "solution.py"

    if not solution_path.exists():
        raise FileNotFoundError(f"solution.py not found in: {problem_dir}")

    cmd = [python_cmd, str(solution_path)]

    result = run_subprocess(cmd, cwd=str(problem_dir))

    return ExecutionResult(
        time=result["time"],
        memory_kb=result["peak_kb"],
        stdout=result["stdout"],
        stderr=result["stderr"],
        returncode=result["returncode"],
        workdir=problem_dir,
    )
