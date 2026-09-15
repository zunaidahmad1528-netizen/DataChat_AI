# 💬 DataChat AI

A Flask web app that lets you upload data from **Excel or CSV** and ask questions about it in plain English. DataChat AI understands your question, converts it into pandas logic behind the scenes, and returns the answer — it can even clean your data (remove duplicates, fill missing values, filter rows) just by asking.

---

## 🧠 How It Works (Explained)

1. **Upload a file** — You upload a `.csv` or `.xlsx` file through the web page.
2. **Data gets loaded** — Flask reads it into a pandas DataFrame and shows you a preview table so you know it loaded correctly.
3. **You ask a question** — In the chat box, you type something like *"what's the average revenue by region?"* or *"remove duplicate rows"*.
4. **AI understands your data** — The app sends Claude a summary of your dataset (column names, data types, a few sample rows, null counts) along with your question — not the whole file, just enough context.
5. **AI writes the logic** — Claude responds with a short explanation plus a small pandas code snippet that would answer your question or perform the cleaning.
6. **App runs it safely** — That snippet runs in a restricted, sandboxed environment (no file access, no system commands) against your actual data.
7. **You see the result** — A table, a number, or your updated (cleaned) dataset appears in the chat.
8. **Changes persist** — If you cleaned something (e.g. removed duplicates), that change stays for your next question, so you can clean step by step.

---

## ✨ Features
- Upload Excel (`.xlsx`, `.xls`) or CSV files
- Live preview of your data right after upload
- Ask questions in plain English — no SQL or pandas knowledge needed
- Ask for data cleaning in plain English too (drop duplicates, fill nulls, filter rows, drop columns)
- Conversation-style interface — keep asking follow-up questions
- Cleaning actions apply to your working dataset immediately

---

## 🛠️ Tech Stack
| Layer | Tool |
|---|---|
| Backend | Flask (Python) |
| Data handling | pandas, NumPy, openpyxl |
| AI | Anthropic Claude API |
| Frontend | HTML, CSS, vanilla JS (fetch API) |

---

## 🚀 Setup — Step by Step

### Step 1: Clone the repository
Download the project files onto your computer.
```bash
git clone https://github.com/<your-username>/datachat-ai.git
cd datachat-ai
```

### Step 2: Create a virtual environment
A virtual environment keeps this project's Python packages separate from everything else on your system, so nothing conflicts.
```bash
python -m venv venv
```
Now activate it:
```bash
# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```
You'll see `(venv)` appear at the start of your terminal prompt when it's active.

### Step 3: Install the dependencies
This installs Flask, pandas, the Claude API library, and everything else the app needs.
```bash
pip install -r requirements.txt
```

### Step 4: Get a Claude API key
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up or log in
3. Open the API Keys section and create a new key
4. Copy it somewhere safe — you'll use it in the next step

### Step 5: Add your API key as an environment variable
Keeping the key as an environment variable (instead of writing it in code) keeps it private and out of your GitHub repo.
```bash
# Mac/Linux
export ANTHROPIC_API_KEY="your-api-key-here"

# Windows (Command Prompt)
set ANTHROPIC_API_KEY=your-api-key-here
```

### Step 6: Run the app
```bash
python app.py
```
You should see Flask start up and print a local URL in the terminal.

### Step 7: Open it in your browser

Upload a CSV or Excel file, wait for the preview to load, then type your first question in the chat box.

---

## 📁 Project Structure


---

## ⚠️ Note on Safety
AI-generated pandas code runs in a restricted namespace — no file, network, or system access, and no `import`, `exec`, or `eval` are allowed inside it. Even so, this project is meant for personal or portfolio use with your own trusted data, not as a public multi-user tool without further security hardening.

## 🔮 Future Improvements
- Connect directly to a SQL database instead of just files
- Download the cleaned dataset as CSV/Excel
- Generate charts from natural-language requests ("plot sales by month")
- Compare and merge multiple uploaded files

## 👤 Author
Built by **Mohd Zunaid** — [LinkedIn](https://www.linkedin.com/in/mohd-zunaid-23069a297/)
