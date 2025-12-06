console.log("[LeetVault] content.js loaded");

let synced = false;

const observer = new MutationObserver(() => trySync());
observer.observe(document.body, { childList: true, subtree: true });


function trySync() {
    console.log("[LeetVault] Checking for Accepted...");

    if (synced) return;

    const verdictElem = document.querySelector('[data-e2e-locator="submission-result"]');
    if (!verdictElem) return;

    const verdictText = verdictElem.innerText.trim().toLowerCase();
    console.log("[LeetVault] Verdict detected:", verdictText);

    if (!verdictText.includes("accepted")) return;

    console.log("[LeetVault] ACCEPTED DETECTED — extracting...");
    synced = true;
    observer.disconnect();

    const payload = extractPayload();
    console.log("[LeetVault] Payload:", payload);

    sendSync(payload);
}


function extractPayload() {
    const code = extractCode();
    const meta = extractMetadata();

    return {
        id: meta.pid,
        title: meta.title,
        runtime: meta.runtime,
        memory: meta.memory,
        code: code,
    };
}


function extractCode() {
    const editor = document.querySelector(".view-lines");
    if (!editor) {
        console.log("[LeetVault] Editor not found");
        return "";
    }

    let code = "";
    editor.querySelectorAll(".view-line").forEach(line => {
        code += line.innerText + "\n";
    });

    return code;
}


function extractMetadata() {
    const titleElem = document.querySelector('[data-e2e-locator="question-title"]');
    let title = titleElem ? titleElem.innerText.trim() : "";

    let pid = "0";
    let titleText = title;

    const m = title.match(/(\d+)\.\s*(.+)/);
    if (m) {
        pid = m[1];
        titleText = m[2];
    }

    const runtime = document.querySelector('[data-e2e-locator="runtime-detail"]')?.innerText || "N/A";
    const memory  = document.querySelector('[data-e2e-locator="memory-detail"]')?.innerText || "N/A";

    return { pid, title: titleText, runtime, memory };
}


function sendSync(data) {
    console.log("[LeetVault] Sending to backend:", data);

    fetch("http://127.0.0.1:5005/sync", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    })
    .then(res => {
        console.log("[LeetVault] Server response:", res.status);
    })
    .catch(err => {
        console.error("[LeetVault] Sync error:", err);
    });
}
