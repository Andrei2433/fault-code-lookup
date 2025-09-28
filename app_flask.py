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
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }
            
            body { 
                font-family: 'Courier New', 'Consolas', 'Monaco', monospace;
                line-height: 1.4;
                color: #00FF00;
                background: #000000;
                min-height: 100vh;
                padding: 10px;
            }
            
            .container {
                max-width: 900px;
                margin: 0 auto;
                background: #000000;
                border: 2px solid #00FF00;
                box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
                overflow: hidden;
            }
            
            .header {
                background: #001100;
                color: #00FF00;
                padding: 15px 20px;
                border-bottom: 2px solid #00FF00;
                text-align: center;
            }
            
            h1 { 
                font-size: 1.8rem;
                font-weight: bold;
                margin-bottom: 5px;
                text-shadow: 0 0 10px #00FF00;
                letter-spacing: 2px;
            }
            
            .subtitle {
                font-size: 0.9rem;
                color: #00AA00;
                font-weight: normal;
            }
            
            .search-section {
                padding: 20px;
                background: #000000;
            }
            
            .search-form {
                display: flex;
                gap: 10px;
                margin-bottom: 15px;
                align-items: center;
            }
            
            .search-label {
                color: #00FF00;
                font-weight: bold;
                font-size: 14px;
                white-space: nowrap;
            }
            
            input[type=text] { 
                flex: 1;
                padding: 8px 12px;
                border: 2px solid #00FF00;
                border-radius: 0;
                font-size: 14px;
                font-family: 'Courier New', monospace;
                background: #000000;
                color: #00FF00;
                outline: none;
            }
            
            input[type=text]:focus {
                box-shadow: 0 0 10px #00FF00;
            }
            
            button { 
                padding: 8px 16px;
                background: #000000;
                color: #00FF00;
                border: 2px solid #00FF00;
                font-size: 14px;
                font-weight: bold;
                cursor: pointer;
                font-family: 'Courier New', monospace;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            button:hover {
                background: #00FF00;
                color: #000000;
                box-shadow: 0 0 15px #00FF00;
            }
            
            .error { 
                color: #FF0000; 
                font-weight: bold;
                background: #220000;
                padding: 10px 15px;
                border: 1px solid #FF0000;
                margin: 15px 0;
                font-size: 14px;
            }
            
            .result { 
                background: #000000; 
                border: 2px solid #00FF00;
                margin: 15px 0;
                overflow: hidden;
            }
            
            .result-header {
                background: #001100;
                color: #00FF00;
                padding: 15px 20px;
                border-bottom: 2px solid #00FF00;
            }
            
            .result-title {
                font-size: 1.2rem;
                font-weight: bold;
                margin-bottom: 5px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .result-content {
                padding: 20px;
                background: #000000;
            }
            
            .section {
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 1px solid #003300;
            }
            
            .section:last-child {
                border-bottom: none;
                margin-bottom: 0;
            }
            
            .section-title {
                font-size: 1rem;
                font-weight: bold;
                color: #00FF00;
                margin-bottom: 10px;
                text-transform: uppercase;
                letter-spacing: 1px;
                background: #001100;
                padding: 8px 12px;
                border: 1px solid #00FF00;
            }
            
            .section-content {
                color: #00AA00;
                line-height: 1.5;
                font-size: 13px;
                padding: 10px 0;
                white-space: pre-wrap;
            }
            
            .fault-title {
                font-size: 1.1rem;
                font-weight: bold;
                color: #00FF00;
                margin-bottom: 10px;
                background: #001100;
                padding: 10px;
                border: 1px solid #00FF00;
            }
            
            .fault-code-bold {
                font-weight: bold;
                background: #00FF00;
                color: #000000;
                padding: 2px 4px;
                font-size: 1.1em;
            }
            
            .multiple-results {
                background: #001100;
                padding: 15px;
                border: 1px solid #00FF00;
            }
            
            .multiple-results h3 {
                color: #00FF00;
                margin-bottom: 15px;
                font-size: 1.1rem;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .multiple-results ul {
                list-style: none;
            }
            
            .multiple-results li {
                background: #000000;
                padding: 8px 12px;
                margin-bottom: 5px;
                border: 1px solid #00FF00;
                font-size: 13px;
            }
            
            .multiple-results li:last-child {
                margin-bottom: 0;
            }
            
            .code-badge {
                background: #00FF00;
                color: #000000;
                padding: 2px 6px;
                font-weight: bold;
                font-size: 0.9rem;
                margin-right: 8px;
            }
            
            .status-bar {
                background: #001100;
                color: #00FF00;
                padding: 5px 20px;
                border-top: 2px solid #00FF00;
                font-size: 12px;
                text-align: right;
            }
            
            .diagnostic-info {
                background: #001100;
                border: 1px solid #00FF00;
                padding: 10px;
                margin: 10px 0;
                font-size: 12px;
                color: #00AA00;
            }
            
            @media (max-width: 600px) {
                body {
                    padding: 5px;
                }
                
                .header {
                    padding: 10px;
                }
                
                h1 {
                    font-size: 1.4rem;
                }
                
                .search-section {
                    padding: 15px;
                }
                
                .search-form {
                    flex-direction: column;
                    align-items: stretch;
                }
                
                .search-label {
                    margin-bottom: 5px;
                }
                
                .result-content {
                    padding: 15px;
                }
                
                .section-title {
                    font-size: 0.9rem;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>VCDS FAULT CODE LOOKUP</h1>
                <p class="subtitle">VAG-COM Diagnostic System v1.0</p>
            </div>
            
            <div class="search-section">
                <div class="diagnostic-info">
                    <strong>SYSTEM STATUS:</strong> ONLINE | <strong>CONNECTION:</strong> LOCAL | <strong>DATABASE:</strong> LOADED
                </div>
                
                <form method="get" class="search-form">
                    <label class="search-label">FAULT CODE:</label>
                    <input type="text" name="code" placeholder="Enter 5-digit fault code (e.g. 00532)" value="{{code}}">
                    <button type="submit">SCAN</button>
                </form>

                {% if error %}
                  <div class="error">{{error}}</div>
                {% endif %}

                {% if result %}
                  {% if result[0] is string %}
                    <div class="result">
                      <div class="result-header">
                        <div class="result-title">FAULT CODE: <span class="code-badge">{{result[0]}}</span></div>
                        {% if result[1] %}
                          <div class="fault-title">
                            {% set title = result[1] %}
                            {% set fault_code = result[0] %}
                            {% if fault_code in title %}
                              {{title.replace(fault_code, '<span class="fault-code-bold">' + fault_code + '</span>')|safe}}
                            {% else %}
                              {{title}}
                            {% endif %}
                          </div>
                        {% endif %}
                      </div>
                      <div class="result-content">
                        {% if result[2] %}
                          <div class="section">
                            <div class="section-title">FULL INFORMATION</div>
                            <div class="section-content">{{result[2]}}</div>
                          </div>
                        {% endif %}
                        {% if result[3] %}
                          <div class="section">
                            <div class="section-title">SYMPTOMS</div>
                            <div class="section-content">{{result[3]}}</div>
                          </div>
                        {% endif %}
                        {% if result[4] %}
                          <div class="section">
                            <div class="section-title">CAUSES</div>
                            <div class="section-content">{{result[4]}}</div>
                          </div>
                        {% endif %}
                        {% if result[5] %}
                          <div class="section">
                            <div class="section-title">SOLUTIONS</div>
                            <div class="section-content">{{result[5]}}</div>
                          </div>
                        {% endif %}
                        {% if result[6] %}
                          <div class="section">
                            <div class="section-title">BONUS NOTES</div>
                            <div class="section-content">{{result[6]}}</div>
                          </div>
                        {% endif %}
                        {% if result[7] %}
                          <div class="section">
                            <div class="section-title">TECHNICAL INFORMATION</div>
                            <div class="section-content">{{result[7]}}</div>
                          </div>
                        {% endif %}
                      </div>
                      <div class="status-bar">
                        SCAN COMPLETE | FAULT CODE: {{result[0]}} | STATUS: ANALYZED
                      </div>
                    </div>
                  {% else %}
                    <div class="result">
                      <div class="result-header">
                        <div class="result-title">MULTIPLE RESULTS FOR '{{code}}'</div>
                      </div>
                      <div class="result-content">
                        <div class="multiple-results">
                          <h3>FOUND {{result|length}} MATCHING CODES:</h3>
                          <ul>
                          {% for r in result %}
                            <li><span class="code-badge">{{r[0]}}</span> - {{r[1]}}</li>
                          {% endfor %}
                          </ul>
                        </div>
                      </div>
                      <div class="status-bar">
                        SCAN COMPLETE | MULTIPLE MATCHES FOUND | SELECT SPECIFIC CODE
                      </div>
                    </div>
                  {% endif %}
                {% endif %}
            </div>
        </div>
    </body>
    </html>
    """, code=code, result=result, error=error)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
