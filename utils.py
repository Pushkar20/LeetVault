import requests
import json
import os
from bs4 import BeautifulSoup

LEETCODE_GRAPHQL = "https://leetcode.com/graphql"

def fetch_question(title_slug):
    query = {
        "query": """
            query questionData($titleSlug: String!) {
                question(titleSlug: $titleSlug) {
                    questionId
                    title
                    content
                    difficulty
                    topicTags { name }
                }
            }
        """,
        "variables": { "titleSlug": title_slug }
    }

    resp = requests.post(LEETCODE_GRAPHQL, json=query)
    data = resp.json()["data"]["question"]

    # Convert HTML question body → Markdown-friendly text
    soup = BeautifulSoup(data["content"], "html.parser")
    markdown_text = soup.get_text("\n")

    return {
        "id": data["questionId"],
        "title": data["title"],
        "difficulty": data["difficulty"],
        "tags": [t["name"] for t in data["topicTags"]],
        "content_md": markdown_text
    }


def safe_slug(text):
    return text.lower().replace(" ", "-").replace(".", "").replace(",", "")
