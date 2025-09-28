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
    if not search_text or not re.match(r'^[A-Za-z0-9]{1,8}$', search_text):
        return None, "Please enter a valid fault code (1-8 alphanumeric characters)"

    fault_code = search_text.upper().strip()

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
            # First try exact match with cleaned code (remove spaces, brackets, etc.)
            cleaned_code = re.sub(r'[\[\]\s]+', '', fault_code)
            cursor.execute(
                """SELECT code, title FROM fault_codes WHERE code = ?""",
                (cleaned_code,)
            )
            exact_cleaned = cursor.fetchone()
            
            if exact_cleaned:
                conn.close()
                return exact_cleaned, None
            
            # Try partial matches
            cursor.execute(
                """SELECT code, title FROM fault_codes WHERE code LIKE ?""",
                (f"%{fault_code}%",)
            )
            results = cursor.fetchall()
            
            # Also try with cleaned code
            if cleaned_code != fault_code:
                cursor.execute(
                    """SELECT code, title FROM fault_codes WHERE code LIKE ?""",
                    (f"%{cleaned_code}%",)
                )
                cleaned_results = cursor.fetchall()
                results.extend(cleaned_results)
            
            # Also check for similar codes (last 3-4 characters)
            if len(fault_code) >= 3:
                last_chars = fault_code[-3:]
                cursor.execute(
                    """SELECT code, title FROM fault_codes WHERE code LIKE ? ORDER BY code LIMIT 10""",
                    (f"%{last_chars}",)
                )
                similar_results = cursor.fetchall()
            else:
                similar_results = []
            
            conn.close()
            
            if results:
                return results, None
            elif similar_results:
                return similar_results, f"No exact match for '{search_text}', but found similar codes ending in '{last_chars}':"
            else:
                return None, f"No results found for '{search_text}'. Try searching for just the code number (e.g., 'P1757' instead of 'P1757 00 [237]')."

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
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }
            
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.4;
                color: #000000;
                background: #E6F3FF;
                min-height: 100vh;
                padding: 10px;
            }
            
            .container {
                max-width: 900px;
                margin: 0 auto;
                background: #FFFFFF;
                border: 1px solid #B0C4DE;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(to bottom, #4A90E2 0%, #357ABD 100%);
                color: #FFFFFF;
                padding: 15px 20px;
                border-bottom: 1px solid #357ABD;
                text-align: center;
            }
            
            h1 { 
                font-size: 1.8rem;
                font-weight: bold;
                margin-bottom: 5px;
                letter-spacing: 1px;
            }
            
            .subtitle {
                font-size: 0.9rem;
                color: #E6F3FF;
                font-weight: normal;
            }
            
            .search-section {
                padding: 20px;
                background: #F8FAFC;
            }
            
            .search-form {
                display: flex;
                gap: 10px;
                margin-bottom: 15px;
                align-items: center;
            }
            
            .search-label {
                color: #2C3E50;
                font-weight: bold;
                font-size: 14px;
                white-space: nowrap;
            }
            
            input[type=text] { 
                flex: 1;
                padding: 8px 12px;
                border: 1px solid #B0C4DE;
                border-radius: 3px;
                font-size: 14px;
                font-family: 'Segoe UI', sans-serif;
                background: #FFFFFF;
                color: #2C3E50;
                outline: none;
            }
            
            input[type=text]:focus {
                border-color: #4A90E2;
                box-shadow: 0 0 5px rgba(74, 144, 226, 0.3);
            }
            
            button { 
                padding: 8px 16px;
                background: linear-gradient(to bottom, #4A90E2 0%, #357ABD 100%);
                color: #FFFFFF;
                border: 1px solid #357ABD;
                border-radius: 3px;
                font-size: 14px;
                font-weight: bold;
                cursor: pointer;
                font-family: 'Segoe UI', sans-serif;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            button:hover {
                background: linear-gradient(to bottom, #357ABD 0%, #2C5F8A 100%);
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }
            
            .error { 
                color: #D32F2F; 
                font-weight: bold;
                background: #FFEBEE;
                padding: 10px 15px;
                border-radius: 3px;
                border-left: 4px solid #D32F2F;
                margin: 15px 0;
                font-size: 14px;
            }
            
            .result { 
                background: #FFFFFF; 
                border: 1px solid #B0C4DE;
                margin: 15px 0;
                overflow: hidden;
            }
            
            .result-header {
                background: linear-gradient(to bottom, #4A90E2 0%, #357ABD 100%);
                color: #FFFFFF;
                padding: 15px 20px;
                border-bottom: 1px solid #357ABD;
            }
            
            .result-title {
                font-size: 1.2rem;
                font-weight: bold;
                margin-bottom: 5px;
                text-transform: uppercase;
                letter-spacing: 1px;
                line-height: 1.4;
            }
            
            .result-content {
                padding: 20px;
                background: #FFFFFF;
            }
            
            .section {
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 1px solid #E0E6ED;
            }
            
            .section:last-child {
                border-bottom: none;
                margin-bottom: 0;
            }
            
            .section-title {
                font-size: 1rem;
                font-weight: bold;
                color: #2C3E50;
                margin-bottom: 10px;
                text-transform: uppercase;
                letter-spacing: 1px;
                background: #F8FAFC;
                padding: 8px 12px;
                border: 1px solid #B0C4DE;
                border-bottom: 2px solid #4A90E2;
            }
            
            .section-content {
                color: #2C3E50;
                line-height: 1.6;
                font-size: 14px;
                padding: 10px 0;
                white-space: pre-wrap;
            }
            
            .fault-title {
                font-size: 1.1rem;
                font-weight: bold;
                color: #2C3E50;
                margin-bottom: 10px;
                background: #F8FAFC;
                padding: 10px;
                border: 1px solid #B0C4DE;
                border-left: 4px solid #4A90E2;
            }
            
            .fault-code-bold {
                font-weight: bold;
                background: #4A90E2;
                color: #FFFFFF;
                padding: 2px 6px;
                font-size: 1.1em;
                border-radius: 3px;
            }
            
            .multiple-results {
                background: #F8FAFC;
                padding: 15px;
                border: 1px solid #B0C4DE;
            }
            
            .multiple-results h3 {
                color: #2C3E50;
                margin-bottom: 15px;
                font-size: 1.1rem;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .multiple-results ul {
                list-style: none;
            }
            
            .multiple-results li {
                background: #FFFFFF;
                padding: 8px 12px;
                margin-bottom: 5px;
                border: 1px solid #B0C4DE;
                border-left: 4px solid #4A90E2;
                font-size: 13px;
            }
            
            .multiple-results li:last-child {
                margin-bottom: 0;
            }
            
            .code-badge {
                background: #4A90E2;
                color: #FFFFFF;
                padding: 2px 6px;
                font-weight: bold;
                font-size: 0.9rem;
                margin-right: 8px;
                border-radius: 3px;
            }
            
            .status-bar {
                background: #F8FAFC;
                color: #2C3E50;
                padding: 8px 20px;
                border-top: 1px solid #B0C4DE;
                font-size: 12px;
                text-align: right;
                font-weight: bold;
            }
            
            .diagnostic-info {
                background: #F8FAFC;
                border: 1px solid #B0C4DE;
                padding: 10px;
                margin: 10px 0;
                font-size: 12px;
                color: #2C3E50;
                border-left: 4px solid #4A90E2;
            }
            
            .tab-container {
                background: #F8FAFC;
                border-bottom: 1px solid #B0C4DE;
                padding: 0;
                margin: 20px 0 0 0;
            }
            
            .tab {
                display: inline-block;
                padding: 12px 20px;
                background: #E0E6ED;
                color: #2C3E50;
                border: 1px solid #B0C4DE;
                border-bottom: none;
                cursor: pointer;
                font-weight: bold;
                font-size: 13px;
                text-transform: uppercase;
                letter-spacing: 1px;
                transition: all 0.3s ease;
            }
            
            .tab:hover {
                background: #D0D6DD;
            }
            
            .tab.active {
                background: #FFFFFF;
                color: #4A90E2;
                border-bottom: 1px solid #FFFFFF;
                margin-bottom: -1px;
            }
            
            .tab-content {
                display: none;
                padding: 20px;
                background: #FFFFFF;
                border: 1px solid #B0C4DE;
                border-top: none;
                min-height: 100px;
            }
            
            .tab-content.active {
                display: block;
            }
            
            .tab-content .section-content {
                color: #2C3E50;
                line-height: 1.6;
                font-size: 14px;
                white-space: pre-wrap;
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
        <script>
            function showTab(tabName) {
                // Hide all tab contents
                var tabContents = document.getElementsByClassName('tab-content');
                for (var i = 0; i < tabContents.length; i++) {
                    tabContents[i].classList.remove('active');
                }
                
                // Remove active class from all tabs
                var tabs = document.getElementsByClassName('tab');
                for (var i = 0; i < tabs.length; i++) {
                    tabs[i].classList.remove('active');
                }
                
                // Show selected tab content
                document.getElementById(tabName).classList.add('active');
                
                // Add active class to clicked tab
                event.target.classList.add('active');
            }
        </script>
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
                    <input type="text" name="code" placeholder="Enter fault code (e.g. 00532, P0123, B1234)" value="{{code}}">
                    <button type="submit">SCAN</button>
                </form>

                {% if error %}
                  <div class="error">{{error}}</div>
                {% endif %}

                {% if result %}
                  {% if result[0] is string %}
                    <div class="result">
                      <div class="result-header">
                        <div class="result-title">
                          FAULT CODE: <span class="code-badge">{{result[0]}}</span>
                          {% if result[1] and result[1].strip() %}
                            {% set title = result[1] %}
                            {% set fault_code = result[0] %}
                            {% if fault_code in title %}
                              - {{title.replace(fault_code, '<span class="fault-code-bold">' + fault_code + '</span>')|safe}}
                            {% else %}
                              - {{title}}
                            {% endif %}
                          {% else %}
                            - Description not available
                          {% endif %}
                        </div>
                      </div>
                      <div class="result-content">
                        {% if result[3] or result[4] or result[5] or result[6] %}
                          <div class="tab-container">
                            {% if result[3] %}
                              <div class="tab active" onclick="showTab('symptoms-tab')">SYMPTOMS</div>
                            {% endif %}
                            {% if result[4] %}
                              <div class="tab{% if not result[3] %} active{% endif %}" onclick="showTab('causes-tab')">CAUSES</div>
                            {% endif %}
                            {% if result[5] %}
                              <div class="tab{% if not result[3] and not result[4] %} active{% endif %}" onclick="showTab('solutions-tab')">SOLUTIONS</div>
                            {% endif %}
                            {% if result[6] %}
                              <div class="tab{% if not result[3] and not result[4] and not result[5] %} active{% endif %}" onclick="showTab('bonus-tab')">BONUS NOTES</div>
                            {% endif %}
                          </div>
                          
                          {% if result[3] %}
                            <div id="symptoms-tab" class="tab-content active">
                              <div class="section-content">{{result[3]}}</div>
                            </div>
                          {% endif %}
                          {% if result[4] %}
                            <div id="causes-tab" class="tab-content{% if not result[3] %} active{% endif %}">
                              <div class="section-content">{{result[4]}}</div>
                            </div>
                          {% endif %}
                          {% if result[5] %}
                            <div id="solutions-tab" class="tab-content{% if not result[3] and not result[4] %} active{% endif %}">
                              <div class="section-content">{{result[5]}}</div>
                            </div>
                          {% endif %}
                          {% if result[6] %}
                            <div id="bonus-tab" class="tab-content{% if not result[3] and not result[4] and not result[5] %} active{% endif %}">
                              <div class="section-content">{{result[6]}}</div>
                            </div>
                          {% endif %}
                        {% endif %}
                        
                        {% if result[2] %}
                          <div class="section">
                            <div class="section-title">FULL INFORMATION</div>
                            <div class="section-content">
                              {% set full_info = result[2] %}
                              {% set fault_code = result[0] %}
                              {% if fault_code in full_info %}
                                {{full_info.replace(fault_code, '<strong>' + fault_code + '</strong>')|safe}}
                              {% else %}
                                {{full_info}}
                              {% endif %}
                            </div>
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