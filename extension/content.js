// Detect Accepted submissions on LeetCode

function extractCode() {
    const editor = document.querySelector(".view-lines");
    if (!editor) return "";

    let code = "";
    editor.querySelectorAll(".view-line").forEach(line => {
        code += line.innerText + "\n";
    });
    return code;
}

function extractMetadata() {
    const titleElem = document.querySelector("[data-cy='question-title']");
    let title = titleElem ? titleElem.innerText.trim() : "";

    // Extract ID + Title (ex: "1. Two Sum")
    let pid = "0";
    let titleText = title;
    const m = title.match(/(\d+)\.\s*(.+)/);
    if (m) {
        pid = m[1];
        titleText = m[2];
    }

    const runtime = document.querySelector("._1h9p53f")?.innerText || "N/A";
    const memory = document.querySelector("._1h9p53f + ._1h9p53f")?.innerText || "N/A";

    return { pid, title: titleText, runtime, memory };
}

function sendSync(data) {
    fetch("http://localhost:5005/sync", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data),
    }).then(r => console.log("Synced:", r.status))
      .catch(err => console.error("Sync error:", err));
}

function trySync() {
    const verdictElem = document.querySelector(".success__3Ai7, .status-column__result");
    if (!verdictElem) return;

    const verdict = verdictElem.innerText.trim();
    if (!verdict.includes("Accepted")) return;

    const meta = extractMetadata();
    const code = extractCode();

    sendSync({
        id: meta.pid,
        title: meta.title,
        runtime: meta.runtime,
        memory: meta.memory,
        code: code
    });
}

// Observe DOM for changes
const obs = new MutationObserver(() => trySync());
obs.observe(document.body, { childList: true, subtree: true });
