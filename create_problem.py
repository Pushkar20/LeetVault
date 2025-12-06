#!/usr/bin/env python3
"""
create_problem.py - Enhanced standalone script to fetch a LeetCode problem and create
a local folder with README and solution template.

Features:
- Accepts only the numeric LeetCode problem id (e.g. 1)
- Auto-fetches titleSlug from LeetCode
- Fetches full problem details and writes README.md + solution.py
- Requires: requests, beautifulsoup4

Usage:
    python create_problem.py <question-id>
Example:
    python create_problem.py 1

Install dependencies:
    pip install requests beautifulsoup4
"""

import os
import sys
import requests
from bs4 import BeautifulSoup

LEETCODE_GRAPHQL = "https://leetcode.com/graphql"
BASE_DIR = "problems"

README_TEMPLATE = (
    "# {id}. {title}\n\n"
    "**Difficulty:** {difficulty}  \n"
    "**Tags:** {tags}\n\n---\n\n"
    "## Problem Description\n"
    "{content}\n\n---\n\n"
    "## Your Solution (solution.py)\n"
    "Write your Python solution in solution.py.\n\n"
    "After completing, run:\n\n"
    "python evaluate_solution.py {id}\n"
)

SOLUTION_TEMPLATE = (
    "\"\"\"Solution for LeetCode problem.\"\"\"\n\n"
    "class Solution:\n"
    "    def solve(self, *args, **kwargs):\n"
    "        # TODO: Implement your solution\n"
    "        return None\n\n"
    "if __name__ == '__main__':\n"
    "    sol = Solution()\n"
    "    print(sol.solve())\n"
)

def graphql_request(query, variables):
    resp = requests.post(LEETCODE_GRAPHQL, json={"query": query, "variables": variables})
    resp.raise_for_status()
    return resp.json()

def get_slug_from_id(qid):
    """Return titleSlug using LeetCode's public metadata API."""
    url = "https://leetcode.com/api/problems/all/"
    resp = requests.get(url)
    resp.raise_for_status()

    data = resp.json().get("stat_status_pairs", [])

    qid = int(qid)

    for item in data:
        stat = item.get("stat", {})
        if stat.get("question_id") == qid:
            return stat.get("question__title_slug")

    raise ValueError(f"Could not find slug for problem ID {qid}.")

def fetch_question(slug):
    query = (
        "query questionData($titleSlug: String!) {\n"
        "  question(titleSlug: $titleSlug) {\n"
        "    questionId title content difficulty topicTags { name }\n"
        "  }\n"
        "}"
    )
    data = graphql_request(query, {"titleSlug": slug})
    q = data.get("data", {}).get("question")
    if not q:
        raise ValueError("Invalid slug or no question data returned")

    soup = BeautifulSoup(q.get("content", ""), "html.parser")
    text = soup.get_text("\n")

    return {
        "id": q.get("questionId"),
        "title": q.get("title"),
        "difficulty": q.get("difficulty"),
        "tags": [t.get("name") for t in q.get("topicTags", [])],
        "content_md": text,
    }

def safe_slug(text):
    s = text.lower().replace(" ", "-")
    for ch in ['/', '\\', ',', '.', ':', ';', '(', ')', '[', ']', '"', "'"]:
        s = s.replace(ch, '-')
    while '--' in s:
        s = s.replace('--', '-')
    return s.strip('-')

def create_problem_folder(qid, slug):
    q = fetch_question(slug)
    folder = f"{qid}-{safe_slug(q['title'])}"
    path = os.path.join(BASE_DIR, folder)
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, 'README.md'), 'w', encoding='utf8') as f:
        f.write(README_TEMPLATE.format(
            id=q['id'],
            title=q['title'],
            difficulty=q['difficulty'],
            tags=', '.join(q['tags']),
            content=q['content_md']
        ))

    with open(os.path.join(path, 'solution.py'), 'w', encoding='utf8') as f:
        f.write(SOLUTION_TEMPLATE)

    print(f"✔ Created folder: {path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python create_problem.py <problem-id>")
        sys.exit(1)

    qid = sys.argv[1]
    print(f"Fetching slug for problem {qid}...")
    slug = get_slug_from_id(qid)
    print(f"→ Slug found: {slug}")

    create_problem_folder(qid, slug)

if __name__ == '__main__':
    main()
