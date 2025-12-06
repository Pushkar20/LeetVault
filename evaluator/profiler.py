"""
profiler.py

Utilities to measure execution time and memory usage for:
- Python callables (run_function)
- External processes (run_subprocess)

Dependencies:
- psutil (for subprocess memory tracking)
- tracemalloc (standard lib, for Python-callable memory)
"""

from __future__ import annotations
import time
import tracemalloc
import subprocess
import threading
from typing import Optional, Dict, Any, List

# psutil is optional but recommended for accurate child-process memory monitoring
try:
    import psutil
except Exception:
    psutil = None


def run_function(func, *args, **kwargs) -> Dict[str, Any]:
    """
    Run a Python callable and measure elapsed time + peak memory.
    Returns:
        {
            "time": float (seconds),
            "peak_kb": float,
            "result": any,
            "error": Optional[str]
        }
    """
    tracemalloc.start()
    start = time.perf_counter()

    try:
        result = func(*args, **kwargs)
        error = None
    except Exception as e:
        result = None
        error = repr(e)

    end = time.perf_counter()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "time": end - start,
        "peak_kb": peak / 1024.0,
        "result": result,
        "error": error
    }


def _monitor_subprocess_memory(proc: subprocess.Popen, interval: float = 0.05) -> float:
    """
    Return peak RSS memory usage of subprocess.
    Requires psutil, else returns -1.
    """
    if psutil is None:
        return -1.0

    try:
        p = psutil.Process(proc.pid)
    except Exception:
        return -1.0

    peak = 0
    while True:
        if proc.poll() is not None:
            break
        try:
            mem = p.memory_info().rss
        except psutil.NoSuchProcess:
            break
        peak = max(peak, mem)
        time.sleep(interval)

    # One last check after exit:
    try:
        mem = p.memory_info().rss
        peak = max(peak, mem)
    except Exception:
        pass

    return float(peak)


def run_subprocess(cmd: List[str], cwd: Optional[str] = None, timeout: Optional[int] = 300) -> Dict[str, Any]:
    """
    Execute an external command and measure:
    - wall time
    - peak memory (KB)
    - stdout
    - stderr
    - exit code
    """
    start = time.perf_counter()
    proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    peak_bytes = -1.0
    monitor_thread = None

    if psutil is not None:
        def _mon():
            nonlocal peak_bytes
            peak_bytes = _monitor_subprocess_memory(proc)

        monitor_thread = threading.Thread(target=_mon, daemon=True)
        monitor_thread.start()

    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()

    end = time.perf_counter()

    if monitor_thread is not None:
        monitor_thread.join(timeout=0.1)

    peak_kb = peak_bytes / 1024.0 if peak_bytes > 0 else None

    return {
        "time": end - start,
        "peak_kb": peak_kb,
        "stdout": stdout or "",
        "stderr": stderr or "",
        "returncode": proc.returncode,
    }
