(() => {
  console.log("[LeetVault] page-hook injected (XHR + FETCH DEBUG)");

  let lastSubmissionId = null;

  /* =====================================================
     FETCH HOOK (keep for submit_id capture)
  ====================================================== */
  const originalFetch = window.fetch;
  window.fetch = async (...args) => {
    const res = await originalFetch(...args);

    try {
      const url = args[0]?.toString() || "";

      if (url.includes("/submit/")) {
        const clone = res.clone();
        const data = await clone.json();
        if (data?.submission_id) {
          lastSubmissionId = data.submission_id;
          console.log("[LeetVault] submission_id captured:", lastSubmissionId);
        }
      }
    } catch {}

    return res;
  };

  /* =====================================================
     XHR HOOK (this is where results actually come from)
  ====================================================== */
  const origOpen = XMLHttpRequest.prototype.open;
  const origSend = XMLHttpRequest.prototype.send;

  XMLHttpRequest.prototype.open = function (method, url, ...rest) {
    this._leetvault_url = url;
    return origOpen.call(this, method, url, ...rest);
  };

  XMLHttpRequest.prototype.send = function (body) {
    this.addEventListener("load", () => {
      try {
        if (!this._leetvault_url) return;

        // Log everything after submit
        if (lastSubmissionId && this._leetvault_url.includes("leetcode.com")) {
          console.group(
            "%c[LeetVault][DEBUG] XHR response",
            "color: lime; font-weight: bold"
          );
          console.log("URL:", this._leetvault_url);
          console.log("status:", this.status);

          let json = null;
          try {
            json = JSON.parse(this.responseText);
            console.dir(json);
          } catch {
            console.log("Non-JSON response");
          }

          console.groupEnd();

          // Try to detect accepted submission
          const accepted = findAccepted(json);
          if (accepted) {
            console.log(
              "[LeetVault] Accepted detected via XHR:",
              accepted.question.title
            );

            window.postMessage(
              {
                source: "leetvault",
                payload: {
                  id: accepted.question.questionFrontendId,
                  slug: accepted.question.titleSlug,
                  title: accepted.question.title,
                  language: accepted.lang,
                  runtime: accepted.runtime,
                  memory: accepted.memory,
                  code: accepted.code
                }
              },
              "*"
            );
          }
        }
      } catch (e) {
        console.error("[LeetVault] XHR hook error:", e);
      }
    });

    return origSend.call(this, body);
  };

  /* =====================================================
     Deep search helper
  ====================================================== */
  function findAccepted(obj) {
    if (!obj || typeof obj !== "object") return null;

    if (
      obj.statusDisplay === "Accepted" &&
      obj.code &&
      obj.question
    ) {
      return obj;
    }

    for (const key in obj) {
      const found = findAccepted(obj[key]);
      if (found) return found;
    }
    return null;
  }
})();
