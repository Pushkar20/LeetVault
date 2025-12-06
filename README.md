# 🧠 LeetCode Local Sync + Auto-Evaluate + Auto-Commit  
A secure, local-first alternative to LeetHub — fully open-source, fully private.


![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.70+-009688?logo=fastapi&logoColor=white)
![Uvicorn](https://img.shields.io/badge/Uvicorn-Server-4E9CD6?logo=uvicorn&logoColor=white)
![Chrome Extension](https://img.shields.io/badge/Chrome%20Extension-MV3-4285F4?logo=google-chrome&logoColor=white)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-Parsing-2F3B7A?logo=beautifulsoup&logoColor=white)
![psutil](https://img.shields.io/badge/psutil-System-6C6C6C?logo=python&logoColor=white)



This tool automatically:

1. Detects **Accepted** LeetCode submissions through a browser extension  
2. Sends solution data to a **local FastAPI backend**  
3. Saves code to your own LeetCode solutions repository  
4. Runs a **local evaluator** to measure execution time & memory  
5. Updates `README.md` with metrics  
6. Performs `git add → commit → push` automatically  

All processing happens **locally**.  
Your GitHub token **never** leaves your machine.  
Your submissions **never** go to third-party servers.

---

# 🚀 Features

### ✔ Automatic save of accepted solutions  
The extension extracts:
- Code  
- Problem ID  
- Title  
- LeetCode runtime  
- LeetCode memory  

### ✔ Local performance evaluation  
Your solution is executed locally and measured for:
- Time (seconds)  
- Peak memory (KB)  
- Output logs  
- Runtime errors  

### ✔ Automatic Git sync  
The backend commits changes with a rich message:
```bash
Auto-sync: Two Sum | local=0.0041s/152KB | leetcode=56 ms/15 MB
```

### ✔ Fully configurable  
All settings live in `config.json`, editable by the user:

- Path to solutions repo  
- Python command  
- Commit message template  
- Whether to push or not  
- Git remote & branch  

### ✔ Privacy-focused  
- No access to GitHub token from browser  
- No cloud services  
- No credentials stored in files  
- Extension communicates only with `localhost:5005`

---

# 📦 Project Structure
```bash
.
├── server/
│ ├── server.py # FastAPI backend
│ └── config.example.json # User config template
│
├── evaluator/
│ ├── init.py
│ ├── evaluator.py # Public API: evaluate()
│ ├── runner.py # Executes solution.py
│ └── profiler.py # Time + memory measurement
│
├── extension/
│ ├── manifest.json # Chrome extension manifest
│ ├── content.js # Submission detector & data sender
│ └── README.md # Extension documentation
```

---

# 🛠 Installation Guide

## 1. Clone this repository

```bash
git clone https://github.com/yourname/leetcode-tool
cd leetcode-tool
```

## 2. Create your solutions repository
You should keep solutions separate from the tool:
```bash
C:\Projects\leetcode-solutions
```
This is where solved problems will appear:
```bash
1-two-sum/
2-add-two-numbers/
...
```

## 3. Copy config file
```bash
cd server
cp config.example.json config.json
```

Open config.json and fill:
```bash
{
  "REPO_PATH": "C:/Projects/leetcode-solutions",
  "PYTHON_CMD": "python",
  "GIT_PUSH": true,
  "GIT_REMOTE_NAME": "origin",
  "GIT_BRANCH": "",
  "COMMIT_MSG_TEMPLATE": "Auto-sync: {title} | local={time:.5f}s/{mem:.2f}KB | leetcode={lc_time}/{lc_mem}"
}
```

## 4. Install dependencies
```bash
pip install fastapi uvicorn psutil
```

## 5. Run the backend server
```bash
cd server
uvicorn server:app --reload --port 5005
```

The server listens at: <http://localhost:5005/sync>


# 🧩 Install Chrome Extension
[Installing the extension](extension/README.md)

# 🔄 How the System Works (Architecture)
```bash
     ┌─────────────────────┐
     │   LeetCode Submit   │
     └──────────┬──────────┘
                │
   Detect Accepted (content.js)
                │
                ▼
 ┌───────────────────────────────────┐
 │  Send JSON → http://localhost:5005/sync
 └───────────────────────────────────┘
                │
                ▼
 ┌───────────────────────────────────┐
 │            Backend                │
 │  - Save solution.py               │
 │  - Append LeetCode metrics        │
 │  - Run evaluator/evaluate()       │
 │  - Append local metrics           │
 │  - git add + commit + (push)      │
 └───────────────────────────────────┘
                │
                ▼
      Your LeetCode solutions repo
```

# 🤝 Contributing

PRs are welcome!
This project aims to be:

- Modular
- Extensible
- Privacy-preserving
- Well-documented

You can improve:

- DOM selectors in extension
- Evaluator logic
- Memory/time profiling
- Git automation
- Config system
- Multi-language support (Java, C++, Rust)

# 📄 License

MIT License — free for personal & commercial use. **DUH!!**