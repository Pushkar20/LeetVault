import json
import subprocess
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

# -------------------------------------------------
# App setup
# -------------------------------------------------

app = FastAPI(title="LeetVault Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# Config
# -------------------------------------------------

CONFIG_PATH = Path(__file__).parent / "config.json"
CONFIG = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

REPO_PATH = Path(CONFIG["REPO_PATH"]).expanduser().resolve()
GIT_PUSH = CONFIG.get("GIT_PUSH", False)
GIT_REMOTE = CONFIG.get("GIT_REMOTE_NAME", "origin")
GIT_BRANCH = CONFIG.get("GIT_BRANCH", "")
COMMIT_TEMPLATE = CONFIG.get(
    "COMMIT_MSG_TEMPLATE",
    "Auto-sync: {title} | leetcode={lc_time}/{lc_mem}"
)

if not REPO_PATH.exists():
    raise RuntimeError(f"Repo not found: {REPO_PATH}")

LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"

HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# -------------------------------------------------
# Models
# -------------------------------------------------

class Submission(BaseModel):
    id: str | None = "X"
    slug: str
    title: str
    language: str
    runtime: str
    memory: str
    code: str

# -------------------------------------------------
# Helpers
# -------------------------------------------------

def git_commit(problem_dir: Path, message: str):
    subprocess.run(["git", "add", str(problem_dir)], cwd=REPO_PATH, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=REPO_PATH, check=True)

    if GIT_PUSH:
        cmd = ["git", "push", GIT_REMOTE]
        if GIT_BRANCH:
            cmd.append(GIT_BRANCH)
        subprocess.run(cmd, cwd=REPO_PATH, check=True)

def fetch_problem_meta(question_id: str):
    """
    Fetch title and slug from LeetCode using questionId.
    This endpoint requires browser-like headers.
    """
    query = """
    query getQuestion($questionId: String!) {
      question(questionId: $questionId) {
        title
        titleSlug
      }
    }
    """

    resp = requests.post(
        LEETCODE_GRAPHQL_URL,
        headers=HEADERS,
        json={
            "query": query,
            "variables": {"questionId": str(question_id)}
        },
        timeout=10
    )

    if resp.status_code != 200:
        # Fail gracefully instead of crashing the whole sync
        print(
            f"[LeetVault][WARN] LeetCode GraphQL failed "
            f"({resp.status_code}), falling back to unknown"
        )
        return "Unknown Problem", "unknown"

    data = resp.json()

    q = data.get("data", {}).get("question")
    if not q:
        return "Unknown Problem", "unknown"

    return q["title"], q["titleSlug"]

def slug_to_title(slug: str) -> str:
    return slug.replace("-", " ").title()

# -------------------------------------------------
# API
# -------------------------------------------------

@app.post("/sync")
def sync_solution(sub: Submission):
    slug = sub.slug or "unknown"
    title = slug_to_title(slug)
    folder_name = f"{sub.id}-{slug}"
    problem_dir = REPO_PATH / folder_name
    problem_dir.mkdir(parents=True, exist_ok=True)

    # Write solution
    LANG_EXT_MAP = {
        "python": "py",
        "python3": "py",
        "cpp": "cpp",
        "c++": "cpp",
        "java": "java",
        "javascript": "js",
        "typescript": "ts",
        "go": "go",
        "rust": "rs"
    }

    ext = LANG_EXT_MAP.get(sub.language.lower(), "txt")

    solution_path = problem_dir / f"solution.{ext}"
    solution_path.write_text(sub.code.rstrip() + "\n", encoding="utf-8")

    # Write README
    readme_path = problem_dir / "README.md"
    readme_path.write_text(
        f"""# {sub.id}. {title}

## LeetCode Submission

- **Language:** {sub.language}
- **Runtime:** {sub.runtime}
- **Memory:** {sub.memory}

> Synced automatically using **LeetVault**
""",
        encoding="utf-8"
    )

    commit_msg = COMMIT_TEMPLATE.format(
        title=sub.title,
        lc_time=sub.runtime,
        lc_mem=sub.memory
    )

    git_commit(problem_dir, commit_msg)

    return {"status": "ok", "path": str(problem_dir)}
