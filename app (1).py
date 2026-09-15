import os
import io
import uuid
import traceback

import pandas as pd
import numpy as np
from flask import Flask, render_template, request, session, jsonify
import anthropic

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# In-memory store: {session_id: {"df": DataFrame, "filename": str}}
DATA_STORE = {}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def load_dataframe(filepath):
    if filepath.lower().endswith(".csv"):
        return pd.read_csv(filepath)
    return pd.read_excel(filepath)


def get_session_id():
    if "sid" not in session:
        session["sid"] = str(uuid.uuid4())
    return session["sid"]


def build_data_summary(df):
    buf = io.StringIO()
    df.info(buf=buf)
    info_str = buf.getvalue()
    summary = f"""Shape: {df.shape[0]} rows x {df.shape[1]} columns
Columns and dtypes:
{info_str}

Sample rows (first 5):
{df.head(5).to_string()}

Basic stats (numeric columns):
{df.describe(include='number').to_string() if not df.select_dtypes('number').empty else 'No numeric columns'}

Null counts per column:
{df.isnull().sum().to_string()}
"""
    return summary


def ask_claude(question, df):
    data_summary = build_data_summary(df)

    system_prompt = """You are DataChat AI, an assistant that helps users explore, analyze, and clean tabular data using pandas.

The user has a pandas DataFrame called `df` already loaded. Given their question, respond ONLY with a JSON object with exactly these keys:
- "explanation": a short, plain-English answer or explanation for the user
- "code": a single pandas/python expression or short snippet (using only `df`, `pd`, and `np`) that computes or transforms the answer. If the question is purely conversational and needs no computation, set this to an empty string.

Rules for "code":
- Only use `df`, `pd`, and `np` — no file, network, or system operations.
- If the user asks to clean, filter, or transform data (e.g. remove duplicates, fill nulls, drop a column), write code that reassigns `df` (e.g. `df = df.drop_duplicates()`).
- If the user asks a question (e.g. "what's the average salary"), write code that computes a `result` variable (e.g. `result = df['salary'].mean()`).
- Keep code short and safe. Never use exec, eval, import, open, or os/sys modules.
- Return ONLY the JSON object, no extra text, no markdown fences.
"""

    user_prompt = f"""Dataset info:
{data_summary}

User question: {question}
"""

    message = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=800,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = message.content[0].text.strip()
    return raw


def run_generated_code(code, df):
    """Execute AI-generated pandas code in a restricted namespace."""
    safe_globals = {"__builtins__": {}}
    safe_locals = {"df": df.copy(), "pd": pd, "np": np, "result": None}

    exec(code, safe_globals, safe_locals)

    new_df = safe_locals.get("df", df)
    result = safe_locals.get("result", None)
    return new_df, result


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "datafile" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["datafile"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Please upload a CSV or Excel (.xlsx/.xls) file"}), 400

    sid = get_session_id()
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], f"{sid}_{file.filename}")
    file.save(filepath)

    try:
        df = load_dataframe(filepath)
    except Exception as e:
        return jsonify({"error": f"Could not read file: {e}"}), 400
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

    DATA_STORE[sid] = {"df": df, "filename": file.filename}

    preview_html = df.head(10).to_html(classes="data-table", border=0)
    return jsonify({
        "message": f"Loaded {file.filename} — {df.shape[0]} rows, {df.shape[1]} columns",
        "preview": preview_html,
        "columns": list(df.columns),
    })


@app.route("/chat", methods=["POST"])
def chat():
    sid = get_session_id()
    if sid not in DATA_STORE:
        return jsonify({"error": "Please upload a dataset first"}), 400

    question = request.json.get("question", "").strip()
    if not question:
        return jsonify({"error": "Please type a question"}), 400

    df = DATA_STORE[sid]["df"]

    try:
        raw = ask_claude(question, df)
        import json as _json
        cleaned = raw.replace("```json", "").replace("```", "").strip()
        parsed = _json.loads(cleaned)
    except Exception:
        return jsonify({"answer": raw if "raw" in dir() else "Sorry, I couldn't process that.", "table": None})

    explanation = parsed.get("explanation", "")
    code = parsed.get("code", "").strip()

    table_html = None
    if code:
        try:
            new_df, result = run_generated_code(code, df)
            DATA_STORE[sid]["df"] = new_df  # persist any cleaning/transform

            if result is not None:
                if isinstance(result, (pd.DataFrame, pd.Series)):
                    table_html = result.to_frame().to_html(classes="data-table", border=0) if isinstance(result, pd.Series) else result.to_html(classes="data-table", border=0)
                else:
                    explanation += f"\n\nResult: {result}"
            else:
                table_html = new_df.head(10).to_html(classes="data-table", border=0)
        except Exception as e:
            explanation += f"\n\n(Note: couldn't run the generated code — {e})"

    return jsonify({"answer": explanation, "table": table_html, "code": code})


@app.route("/reset", methods=["POST"])
def reset():
    sid = get_session_id()
    DATA_STORE.pop(sid, None)
    return jsonify({"message": "Session cleared"})


if __name__ == "__main__":
    app.run(debug=True)
