console.log("[LeetVault] content.js loaded");

/* ---------------------------------------------------------
   Notify background to attach debugger
--------------------------------------------------------- */
chrome.runtime.sendMessage({
  type: "LEETCODE_TAB_READY"
});

/* ---------------------------------------------------------
   Extract question text
--------------------------------------------------------- */
function extractQuestionText() {
  const container = document.querySelector(
    '[data-track-load="description_content"]'
  );

  if (!container) return "";

  return container.innerText.trim();
}

/* ---------------------------------------------------------
   Respond to background request (IMPORTANT)
--------------------------------------------------------- */
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg?.type === "GET_QUESTION_TEXT") {
    const container = document.querySelector(
      '[data-track-load="description_content"]'
    );

    const question = container ? container.innerText.trim() : "";

    sendResponse({ question });

    return true;
  }
});

