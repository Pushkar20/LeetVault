/* =========================================================
   LeetVault – background.js (FINAL, CLEAN)
   ========================================================= */

const BACKEND_URL = "http://127.0.0.1:5005/sync";
const STATUS_ACCEPTED = 10;

let attachedTabId = null;
let leetcodeTabId = null;

let lastSubmitPayload = null;

const pendingSubmissions = new Map(); // submissionId -> payload
const synced = new Set();             // submissionIds already synced

let debuggerAttached = false;
let lastActiveAt = null;

/* ---------------------------------------------------------
   Listen for LeetCode tab readiness & popup actions
--------------------------------------------------------- */
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg?.type === "LEETCODE_TAB_READY" && sender.tab?.id) {
    leetcodeTabId = sender.tab.id;
    attachDebugger(leetcodeTabId);
  }

  if (msg?.type === "GET_STATUS") {
    sendResponse({ debuggerAttached, lastActiveAt });
    return true;
  }

  if (msg?.type === "FORCE_REATTACH") {
    if (typeof leetcodeTabId === "number") {
      console.log(
        "[LeetVault] Manual debugger re-attach requested for LeetCode tab",
        leetcodeTabId
      );
      attachDebugger(leetcodeTabId);
    }
    sendResponse({ ok: true });
    return true;
  }
});

/* ---------------------------------------------------------
   Attach Chrome Debugger (safe)
--------------------------------------------------------- */
function attachDebugger(tabId) {
  chrome.debugger.attach({ tabId }, "1.3", () => {
    if (chrome.runtime.lastError) {
      if (
        chrome.runtime.lastError.message?.includes(
          "Another debugger is already attached"
        )
      ) {
        debuggerAttached = true;
        attachedTabId = tabId;
        return;
      }

      console.error(
        "[LeetVault] Debugger attach failed:",
        chrome.runtime.lastError.message
      );
      debuggerAttached = false;
      return;
    }

    attachedTabId = tabId;
    debuggerAttached = true;
    lastActiveAt = Date.now();

    console.log("[LeetVault] Debugger attached");

    chrome.debugger.sendCommand(
      { tabId },
      "Network.enable",
      {},
      () => {
        if (chrome.runtime.lastError) {
          console.warn(
            "[LeetVault] Network.enable failed:",
            chrome.runtime.lastError.message
          );
        }
      }
    );
  });
}

/* ---------------------------------------------------------
   CDP Network Listener
--------------------------------------------------------- */
chrome.debugger.onEvent.addListener(async (source, method, params) => {
  try {
    /* ------------------------------
       SUBMIT REQUEST
    ------------------------------ */
    if (
      method === "Network.requestWillBeSent" &&
      params.request.url.includes("/submit/") &&
      params.request.postData
    ) {
      const body = JSON.parse(params.request.postData);
      const slugMatch = params.request.url.match(/problems\/([^/]+)\//);

      const { question } = await chrome.tabs.sendMessage(
        source.tabId,
        { type: "GET_QUESTION_TEXT" }
      );

      lastSubmitPayload = {
        code: body.typed_code,
        language: body.lang,
        questionId: body.question_id,
        slug: slugMatch ? slugMatch[1] : "unknown",
        question: question || ""
      };

      lastActiveAt = Date.now();
      console.log("[LeetVault] Code captured at submit");
    }

    /* ------------------------------
       SUBMIT RESPONSE
       (submission_id + possible Accepted)
    ------------------------------ */
    if (
      method === "Network.responseReceived" &&
      params.response.url.includes("/submit/")
    ) {
      const body = await getResponseBody(source.tabId, params.requestId);
      if (!body || !lastSubmitPayload) return;

      const json = JSON.parse(body);
      const submissionId = String(json.submission_id);
      if (!submissionId) return;

      pendingSubmissions.set(submissionId, lastSubmitPayload);
      console.log("[LeetVault] submission_id linked:", submissionId);

      if (
        json.status_code === STATUS_ACCEPTED ||
        json.state === "SUCCESS" ||
        json.status === "ACCEPTED"
      ) {
        attemptSync(submissionId, json);
      }

      lastSubmitPayload = null;
    }

    /* ------------------------------
       CHECK RESPONSE (fallback path)
    ------------------------------ */
    if (
      method === "Network.responseReceived" &&
      params.response.url.includes("/submissions/detail/") &&
      params.response.url.endsWith("/check/")
    ) {
      const submissionId = extractSubmissionId(params.response.url);
      if (!submissionId) return;

      const body = await getResponseBody(source.tabId, params.requestId);
      if (!body) return;

      const json = JSON.parse(body);

      if (
        json.status_code === STATUS_ACCEPTED ||
        json.state === "SUCCESS"
      ) {
        attemptSync(submissionId, json);
      }
    }

    /* ------------------------------
       ACCEPTED VIA BANNER API
       (UI verdict path)
    ------------------------------ */
    if (
      method === "Network.responseReceived" &&
      params.response.url.includes("/api/banner/qd-submission-banner/")
    ) {
      const lastSubmissionId = Array.from(pendingSubmissions.keys()).pop();
      if (lastSubmissionId) {
        attemptSync(lastSubmissionId, {});
      }
    }
  } catch (err) {
    console.error("[LeetVault] CDP error:", err);
  }
});

/* ---------------------------------------------------------
   Attempt backend sync (single-shot)
--------------------------------------------------------- */
function attemptSync(submissionId, resultJson) {
  if (synced.has(submissionId)) return;

  const submission = pendingSubmissions.get(submissionId);
  if (!submission) return;

  synced.add(submissionId);
  pendingSubmissions.delete(submissionId);

  console.log("[LeetVault] Accepted:", submissionId);
  console.log("[LeetVault] Syncing to backend…");

  (async () => {
    let runtime = resultJson.status_runtime || "";
    let memory = resultJson.status_memory || "";

    // Banner-based Accepted → fetch performance explicitly
    if (!runtime && !memory) {
      const details = await fetchSubmissionDetails(submissionId);
      runtime = details.runtime || "";
      memory = details.memory || "";
    }

    syncToBackend({
      id: submission.questionId,
      slug: submission.slug,
      title: "",
      language: submission.language,
      runtime,
      memory,
      code: submission.code,
      question: submission.question
    });
  })();
}

/* ---------------------------------------------------------
   Helpers
--------------------------------------------------------- */
function extractSubmissionId(url) {
  const m = url.match(/detail\/(\d+)\//);
  return m ? String(m[1]) : null;
}

function getResponseBody(tabId, requestId) {
  return new Promise((resolve) => {
    chrome.debugger.sendCommand(
      { tabId },
      "Network.getResponseBody",
      { requestId },
      (res) => {
        if (chrome.runtime.lastError || !res?.body) {
          resolve(null);
        } else {
          resolve(res.body);
        }
      }
    );
  });
}

async function fetchSubmissionDetails(submissionId) {
  try {
    const res = await fetch(
      `https://leetcode.com/submissions/detail/${submissionId}/`,
      { credentials: "include" }
    );

    if (!res.ok) return {};

    const text = await res.text();

    // Extract JSON embedded in the page
    const match = text.match(/submissionDetail:\s*(\{.*?\})\s*,/s);
    if (!match) return {};

    return JSON.parse(match[1]);
  } catch {
    return {};
  }
}

/* ---------------------------------------------------------
   Backend sync
--------------------------------------------------------- */
async function syncToBackend(payload) {
  try {
    const res = await fetch(BACKEND_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const text = await res.text();
      console.error(
        "[LeetVault] Backend error:",
        res.status,
        text
      );
      return;
    }

    console.log("[LeetVault] Backend sync OK");
  } catch (err) {
    console.error("[LeetVault] Backend fetch failed:", err);
  }
}
