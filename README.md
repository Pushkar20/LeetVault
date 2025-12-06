# 📘 LeetCode Automation Tool

A lightweight command-line tool that **fetches LeetCode problems**, auto-creates folders with clean structure, generates a solution template, and prepares you for systematic problem-solving — while boosting GitHub activity.

This tool is ideal if you're solving all LeetCode problems and want:

✔ Auto-generated folders  
✔ Readable problem statements in Markdown  
✔ Pre-filled `solution.py` template  
✔ Consistent structure  
✔ Benchmark-ready environment  

---

## 🚀 Features

- **Fetch LeetCode question text using GraphQL**
- **Auto-create folder with problem ID + title**
- **Generate a clean `README.md` containing:**
  - Title  
  - Difficulty  
  - Tags  
  - Full problem description  
- **Auto-generate Python solution template**
- **Compatible with your future benchmarking script (`evaluate_solution.py`)**
- Predictable folder structure ideal for GitHub commits

---

## 📦 Folder Structure

When you run the tool, it creates folders like:

```
problems/
└── 1-two-sum/
    ├── README.md
    └── solution.py
```

---

## 🔧 Installation

Install dependencies:

```bash
pip install requests beautifulsoup4
```

---

## 🛠️ Usage

Run the script using:

```bash
python create_problem.py <problem-id>
```

### Example

```bash
python create_problem.py 1
```

This will create:

```
problems/1-two-sum/
  ├── README.md
  └── solution.py
```

---

## 📄 Generated README Example

The tool auto-generates a complete Markdown file containing:

- Problem ID  
- Title  
- Difficulty  
- Tags  
- Full cleaned problem description  
- Instructions for running evaluation  

Example excerpt:

```
# 1. Two Sum

**Difficulty:** Easy  
**Tags:** Array, Hash Table

---

## 📘 Problem Description
Given an array of integers nums and an integer target...

---

## 🧠 Your Solution (`solution.py`)
Write your Python solution in solution.py.

After completing, run:

python evaluate_solution.py 1
```

---

## 🧪 Solution Template

The tool generates a minimal `solution.py` with a `solve()` function:

```python
class Solution:
    def solve(self, *args, **kwargs):
        # TODO: Implement your solution
        pass

if __name__ == "__main__":
    sol = Solution()
    print(sol.solve())
```

You may customize this based on your test inputs or LeetCode approach.

---

## 🧩 Evaluation (Optional)

If you add the companion script `evaluate_solution.py`, you will also get:

- Execution time  
- Peak memory usage  
- Auto-append results to `README.md`  

This is ideal for tracking performance metrics.

---

## 🤖 Why This Tool?

This automation helps you:

- Stay consistent with folder structure  
- Maintain clean documentation  
- Automatically keep GitHub active  
- Focus only on solving the problem, not organizing files  

---


## 📝 License

MIT License — free for personal + commercial use.
