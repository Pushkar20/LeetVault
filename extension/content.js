console.log("[LeetVault] content.js loaded");

chrome.runtime.sendMessage({
  type: "LEETCODE_TAB_READY"
});
