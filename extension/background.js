/* =========================================================
   LeetVault – FINAL background.js (FIXED)
   ========================================================= */

let attachedTabId = null;

const STATUS_ACCEPTED = 10;
const BACKEND_URL = "http://127.0.0.1:5005/sync";

// submissionId (string) -> { code, language, questionId }
const pendingSubmissions = new Map();
const synced = new Set();

let lastSubmitPayload = null;

/* ---------------------------------------------------------
   Listen for LeetCode tab
--------------------------------------------------------- */
chrome.runtime.onMessage.addListener((msg, sender) => {
  if (msg?.type === "LEETCODE_TAB_READY" && sender.tab?.id) {
    attachDebugger(sender.tab.id);
  }
});

/* ---------------------------------------------------------
   Attach CDP
--------------------------------------------------------- */
function attachDebugger(tabId) {
  if (attachedTabId === tabId) {
    // Already attached
    return;
  }

  // Defensive detach in case MV3 lost state
  chrome.debugger.detach({ tabId }, () => {});

  chrome.debugger.attach({ tabId }, "1.3", () => {
    if (chrome.runtime.lastError) {
      console.error(
        "[LeetVault] Debugger attach failed:",
        chrome.runtime.lastError.message
      );
      return;
    }

    attachedTabId = tabId;
    console.log("[LeetVault] Debugger attached");

    chrome.debugger.sendCommand({ tabId }, "Network.enable");
  });
}

/* ---------------------------------------------------------
   CDP Event Listener
--------------------------------------------------------- */
chrome.debugger.onEvent.addListener(async (source, method, params) => {
  try {
    /* 1. Capture SUBMIT request */
    if (method === "Network.requestWillBeSent") {
      const { request } = params;

      if (request.url.includes("/submit/") && request.postData) {
        const body = JSON.parse(request.postData);

        const slugMatch = request.url.match(/problems\/([^/]+)\//);

        // Ask content script for question AT SUBMIT TIME
        const { question } = await chrome.tabs.sendMessage(
            source.tabId,
            { type: "GET_QUESTION_TEXT" }
        );
        console.log("[LeetVault] Question length:", question?.length);

        lastSubmitPayload = {
            code: body.typed_code,
            language: body.lang,
            questionId: body.question_id,
            slug: slugMatch ? slugMatch[1] : "unknown",
            question: question || ""
        };

        console.log("[LeetVault] Code captured at submit");
      }
    }

    /* 2. Capture SUBMIT response (submission_id) */
    if (method === "Network.responseReceived") {
      const url = params.response.url;

      if (url.includes("/submit/")) {
        const body = await getResponseBody(source.tabId, params.requestId);
        if (!body || !lastSubmitPayload) return;

        const json = JSON.parse(body);
        const submissionId = String(json.submission_id);
        if (!submissionId) return;

        pendingSubmissions.set(submissionId, lastSubmitPayload);
        lastSubmitPayload = null;

        console.log(
          "[LeetVault] submission_id linked:",
          submissionId
        );
      }
    }

    /* 3. Detect ACCEPTED via /check/ */
    if (
      method === "Network.responseReceived" &&
      params.response.url.includes("/submissions/detail/") &&
      params.response.url.endsWith("/check/")
    ) {
      const submissionId = extractSubmissionId(params.response.url);
      if (!submissionId || synced.has(submissionId)) return;

      const body = await getResponseBody(source.tabId, params.requestId);
      if (!body) return;

      const json = JSON.parse(body);
      if (json.status_code !== STATUS_ACCEPTED) return;

      const submission = pendingSubmissions.get(submissionId);
      if (!submission) return;

      synced.add(submissionId);
      pendingSubmissions.delete(submissionId);

      console.log("[LeetVault] Accepted:", submissionId);

      setTimeout(() => {
        syncToBackend({
            id: submission.questionId,
            slug: submission.slug,
            title: "", // backend can derive from slug
            language: submission.language,
            runtime: json.status_runtime,
            memory: json.status_memory,
            code: submission.code,
            question: submission.question
        });
      }, 0);
    }
  } catch (err) {
    console.error("[LeetVault] CDP error:", err);
  }
});

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

/* ---------------------------------------------------------
   Backend sync
--------------------------------------------------------- */
async function syncToBackend(payload) {
  console.log("[LeetVault] Syncing to backend…");

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
