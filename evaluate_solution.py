#!/usr/bin/env python3
"""
Enhanced evaluate_solution.py
Now supports:
✔ Running evaluation using ONLY problem ID
✔ Automatically locates correct folder
"""

import os
import sys
import time
import tracemalloc

BASE_DIR = "problems"

def find_folder_by_id(qid):
    """Find directory matching '<id>-...'"""
    for name in os.listdir(BASE_DIR):
        if name.startswith(f"{qid}-"):
            return os.path.join(BASE_DIR, name)
    raise FileNotFoundError(f"No folder found for problem ID {qid}")

def run_solution(path):
    """Execute solution.py while tracking time + memory."""
    tracemalloc.start()
    t1 = time.time()

    os.system(f"python {path}")

    current, peak = tracemalloc.get_traced_memory()
    t2 = time.time()

    return (t2 - t1), (peak / 1024)

def append_results(folder, time_taken, memory_kb):
    readme = os.path.join(folder, "README.md")

    block = f"""
---

# 🧪 Performance Results

**Execution Time:** {time_taken:.4f} sec  
**Memory Usage:** {memory_kb:.2f} KB  
"""

    with open(readme, "a", encoding="utf-8") as f:
        f.write(block)

def main():
    if len(sys.argv) < 2:
        print("Usage: python evaluate_solution.py <id>")
        sys.exit(1)

    qid = sys.argv[1]
    folder = find_folder_by_id(qid)
    sol_path = os.path.join(folder, "solution.py")

    print(f"Evaluating problem {qid}...")

    t, mem = run_solution(sol_path)
    append_results(folder, t, mem)

    print(f"Results saved → {folder}/README.md")

if __name__ == "__main__":
    main()
