# LeetCode Sync Browser Extension

This folder contains the browser extension that detects accepted LeetCode
submissions and sends the data to your local backend (`server.py`)
for automatic saving, evaluation, and Git commit.

---

## 🔧 How to Install (Chrome / Edge)

1. Open your browser and go to: <chrome://extensions>

2. Enable **Developer Mode** (top-right toggle)

3. Click **Load Unpacked**

4. Select this `extension/` folder

5. Done! 🎉  
The extension now runs automatically on: <https://leetcode.com/>

---

## 🚀 How it Works

- When you click **Submit** on LeetCode  
- The extension waits for the **Accepted** result to appear  
- It extracts:
- Problem ID  
- Problem title  
- Submitted code  
- Runtime  
- Memory usage  
- Then it POSTs this JSON to: <http://localhost:5005/sync>

Your backend receives it and handles everything else.

---

## 📁 Files

### **manifest.json**
Declares extension permissions & content scripts.

### **content.js**
Main logic:
- Watches for changes in the submission result area  
- Extracts metadata  
- Extracts code from Monaco editor  
- Sends all data to the backend  

---

## 🛠️ Customization

You may modify:
- The detection logic (if LeetCode changes DOM)  
- The backend URL (`localhost:5005/sync`)  
- Extracted metadata fields  

---

## ❗ Security Note

This extension does **not**:
- Store your GitHub token  
- Access any external network except your local backend  
- Upload code anywhere online  

This makes it **far safer** than Chrome Web Store extensions.

---

## ❤️ Contributing

Feel free to submit PRs to improve parsing, performance, or add UI to the extension.
