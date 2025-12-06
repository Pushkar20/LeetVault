"""
server.py
FastAPI backend for:
- receiving LeetCode submission data from browser extension
- saving code into user's LeetCode solutions repo
- running evaluator module
- updating README with metrics
- committing & pushing changes

This backend is fully config-driven (config.json or env vars).
"""

from __future__ import annotations
from fastapi import FastAPI, Request, HTTPException
import uvicorn
import json, os, subprocess, shlex
from pathlib import Path
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

from evaluator.evaluator import evaluate


# ---------------- CONFIG LOADING ---------------- #

CONFIG_PATH = Path(__file__).parent / "config.json"
DEFAULT_CONFIG = {
    "REPO_PATH": "",
    "PYTHON_CMD": "python",
    "GIT_PUSH": True,
    "GIT_REMOTE_NAME": "origin",
    "GIT_BRANCH": "",
    "COMMIT_MSG_TEMPLATE": (
        "Auto-sync: {title} | local={time:.5f}s/{mem:.2f}KB | "
        "leetcode={lc_time}/{lc_mem}"
    )
}

def load_config():
    cfg = DEFAULT_CONFIG.copy()
    if CONFIG_PATH.exists():
        cfg.update(json.loads(CONFIG_PATH.read_text()))
    return cfg

config = load_config()


# ---------------- HELPERS ---------------- #

def safe_slug(text: str) -> str:
    s = text.lower()
    for ch in [' ', '/', '\\', ',', '.', ':', ';', '(', ')', '[', ']', '"', "'"]:
        s = s.replace(ch, '-')
    while "--" in s:
        s = s.replace("--", "-")
    return s.strip("-")


def ensure_problem_folder(problem_id: str, title: str, repo_path: str):
    repo = Path(repo_path)
    folder = repo / f"{problem_id}-{safe_slug(title)}"
    folder.mkdir(parents=True, exist_ok=True)

    readme = folder / "README.md"
    if not readme.exists():
        readme.write_text(f"# {problem_id}. {title}\n\n", encoding="utf8")

    return folder, readme


def append_leetcode_metrics(readme: Path, lc_runtime: str, lc_memory: str):
    block = (
        "\n---\n**LeetCode Metrics:**\n"
        f"- Runtime: {lc_runtime}\n"
        f"- Memory: {lc_memory}\n"
    )
    readme.write_text(readme.read_text(encoding="utf8") + block, encoding="utf8")


def append_local_metrics(readme: Path, result):
    block = (
        "\n---\n**Local Evaluation:**\n"
        f"- Time: {result.time:.5f} sec\n"
        f"- Memory: {result.memory:.2f} KB\n"
        f"- Status: {result.status}\n"
    )
    readme.write_text(readme.read_text(encoding="utf8") + block, encoding="utf8")


def run_git(repo_path: Path, args: list[str]):
    proc = subprocess.run(
        args, cwd=str(repo_path),
        capture_output=True, text=True
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    return proc.stdout


def commit_changes(repo_path: Path, commit_msg: str):
    run_git(repo_path, ["git", "add", "."])
    run_git(repo_path, ["git", "commit", "-m", commit_msg])

    if config["GIT_PUSH"]:
        remote = config["GIT_REMOTE_NAME"]
        branch = config["GIT_BRANCH"]
        if branch:
            run_git(repo_path, ["git", "push", remote, branch])
        else:
            run_git(repo_path, ["git", "push", remote])


# ---------------- FASTAPI SERVER ---------------- #

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://leetcode.com", "http://localhost:5005", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/sync")
async def sync(request: Request):
    data = await request.json()

    # Required fields from the extension:
    try:
        problem_id = str(data["id"])
        title = data["title"]
        code = data["code"]
        lc_time = data.get("runtime", "N/A")
        lc_memory = data.get("memory", "N/A")
    except KeyError:
        raise HTTPException(400, "Missing fields from extension")

    repo = config["REPO_PATH"]
    if not repo:
        raise HTTPException(500, "REPO_PATH not set in config.json")

    # 1. Save solution
    folder, readme = ensure_problem_folder(problem_id, title, repo)
    solution = folder / "solution.py"
    solution.write_text(code, encoding="utf8")

    # 2. Append LC metrics
    append_leetcode_metrics(readme, lc_time, lc_memory)

    # 3. Run local evaluation
    result = evaluate(problem_id, repo, python_cmd=config["PYTHON_CMD"])

    # 4. Append local evaluation
    append_local_metrics(readme, result)

    # 5. Commit and push
    commit_msg = config["COMMIT_MSG_TEMPLATE"].format(
        title=title,
        time=result.time,
        mem=result.memory,
        lc_time=lc_time,
        lc_mem=lc_memory
    )
    commit_changes(Path(repo), commit_msg)

    return {"status": "ok", "message": commit_msg}



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5005)
