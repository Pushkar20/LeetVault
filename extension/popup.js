function formatTime(ts) {
  if (!ts) return "Never";
  const diff = Math.floor((Date.now() - ts) / 1000);
  return diff < 60 ? `${diff}s ago` : `${Math.floor(diff / 60)}m ago`;
}

function refreshStatus() {
  chrome.runtime.sendMessage({ type: "GET_STATUS" }, (res) => {
    const statusEl = document.getElementById("status");
    const timeEl = document.getElementById("time");

    if (!res) {
      statusEl.textContent = "Background inactive";
      statusEl.className = "status bad";
      return;
    }

    if (res.debuggerAttached) {
      statusEl.textContent = "Debugger: Attached";
      statusEl.className = "status ok";
    } else {
      statusEl.textContent = "Debugger: Detached";
      statusEl.className = "status bad";
    }

    timeEl.textContent = "Last activity: " + formatTime(res.lastActiveAt);
  });
}

document.getElementById("reload").addEventListener("click", () => {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (!tabs.length) return;

    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (!tabs.length) return;

    chrome.runtime.sendMessage(
        {
        type: "FORCE_REATTACH",
        tabId: tabs[0].id
        },
        () => refreshStatus()
    );
    });
  });
});

refreshStatus();
