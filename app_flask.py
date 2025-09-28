#!/usr/bin/env python3
"""
Ross-Tech VCDS Fault Codes Web Application (Flask version)

A Flask-based application for searching fault codes offline,
works on Android via Termux.
"""

from flask import Flask, request, render_template_string
import sqlite3
import os
import re

DB_PATH = "fault_codes.db"

app = Flask(__name__)

def query_fault_code(search_text):
    """Search for a fault code in the database."""
    if not search_text or not re.match(r'^\d{1,5}$', search_text):
        return None, "Please enter a valid fault code (1–5 digits)"

    fault_code = search_text.zfill(5)

    if not os.path.exists(DB_PATH):
        return None, "Database not found. Please run crawler.py first."

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Exact match
        cursor.execute(
            """SELECT code, title, full_content, symptoms, causes, solutions,
                      special_notes, technical_info
               FROM fault_codes WHERE code = ?""",
            (fault_code,)
        )
        result = cursor.fetchone()

        # If no exact match, look for partial matches
        if not result:
            cursor.execute(
                """SELECT code, title FROM fault_codes WHERE code LIKE ?""",
                (f"%{fault_code}%",)
            )
            results = cursor.fetchall()
            conn.close()
            if results:
                return results, None
            else:
                return None, f"No results found for '{search_text}'"

        conn.close()
        return result, None

    except sqlite3.Error as e:
        return None, f"Database error: {e}"

@app.route("/", methods=["GET"])
def home():
    code = request.args.get("code", "").strip()
    result, error = (None, None)

    if code:
        result, error = query_fault_code(code)

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>VCDS Fault Code Lookup</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #2E86AB; }
            .error { color: #E17055; font-weight: bold; }
            .result { background: #f9f9f9; padding: 10px; border-radius: 8px; }
            input[type=text] { width: 70%; padding: 8px; }
            button { padding: 8px 12px; }
        </style>
    </head>
    <body>
        <h1>VCDS Fault Code Lookup</h1>
        <form method="get">
            <input type="text" name="code" placeholder="Enter code (e.g. 00532)" value="{{code}}">
            <button type="submit">Search</button>
        </form>

        {% if error %}
          <p class="error">{{error}}</p>
        {% endif %}

        {% if result %}
          {% if result[0] is string %}
            <div class="result">
              <h3>Fault Code: {{result[0]}}</h3>
              {% if result[1] %}<p><b>{{result[1]}}</b></p>{% endif %}
              {% if result[2] %}<p><b>Full Info:</b><br>{{result[2]}}</p>{% endif %}
              {% if result[3] %}<p><b>Symptoms:</b><br>{{result[3]}}</p>{% endif %}
              {% if result[4] %}<p><b>Causes:</b><br>{{result[4]}}</p>{% endif %}
              {% if result[5] %}<p><b>Solutions:</b><br>{{result[5]}}</p>{% endif %}
              {% if result[6] %}<p><b>Notes:</b><br>{{result[6]}}</p>{% endif %}
              {% if result[7] %}<p><b>Technical Info:</b><br>{{result[7]}}</p>{% endif %}
            </div>
          {% else %}
            <div class="result">
              <h3>Multiple results for '{{code}}'</h3>
              <ul>
              {% for r in result %}
                <li><b>{{r[0]}}</b> - {{r[1]}}</li>
              {% endfor %}
              </ul>
            </div>
          {% endif %}
        {% endif %}
    </body>
    </html>
    """, code=code, result=result, error=error)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
