#!/usr/bin/env python3
"""
Ross-Tech VCDS Fault Codes Web Application (Flask version) - Mobile Optimized

A Flask-based application for searching fault codes offline,
works on Android via Termux with mobile-friendly UI.
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
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <meta name="theme-color" content="#4A90E2">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="default">
        <style>
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }
            
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                line-height: 1.5;
                color: #2C3E50;
                background: linear-gradient(135deg, #E6F3FF 0%, #F0F8FF 100%);
                min-height: 100vh;
                padding: 0;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
            }
            
            .container {
                max-width: 100%;
                margin: 0;
                background: #FFFFFF;
                min-height: 100vh;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
            }
            
            .header {
                background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%);
                color: #FFFFFF;
                padding: 20px 15px;
                text-align: center;
                position: sticky;
                top: 0;
                z-index: 100;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            
            h1 { 
                font-size: 1.5rem;
                font-weight: 700;
                margin-bottom: 5px;
                letter-spacing: 0.5px;
            }
            
            .subtitle {
                font-size: 0.85rem;
                color: #E6F3FF;
                font-weight: 400;
            }
            
            .search-section {
                padding: 20px 15px;
                background: #F8FAFC;
                border-bottom: 1px solid #E0E6ED;
            }
            
            .diagnostic-info {
                background: #E8F4FD;
                border: 1px solid #B0C4DE;
                padding: 12px 15px;
                margin-bottom: 20px;
                font-size: 0.8rem;
                color: #2C3E50;
                border-left: 4px solid #4A90E2;
                border-radius: 0 4px 4px 0;
            }
            
            .search-form {
                display: flex;
                flex-direction: column;
                gap: 15px;
            }
            
            .search-label {
                color: #2C3E50;
                font-weight: 600;
                font-size: 0.9rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .input-group {
                display: flex;
                gap: 10px;
                align-items: stretch;
            }
            
            input[type=text] { 
                flex: 1;
                padding: 15px 12px;
                border: 2px solid #E0E6ED;
                border-radius: 8px;
                font-size: 16px;
                font-family: inherit;
                background: #FFFFFF;
                color: #2C3E50;
                outline: none;
                transition: all 0.3s ease;
                -webkit-appearance: none;
            }
            
            input[type=text]:focus {
                border-color: #4A90E2;
                box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
                transform: translateY(-1px);
            }
            
            button { 
                padding: 15px 25px;
                background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%);
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                font-family: inherit;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                transition: all 0.3s ease;
                min-width: 80px;
                -webkit-tap-highlight-color: transparent;
            }
            
            button:hover, button:active {
                background: linear-gradient(135deg, #357ABD 0%, #2C5F8A 100%);
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
            }
            
            .error { 
                color: #D32F2F; 
                font-weight: 600;
                background: #FFEBEE;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #D32F2F;
                margin: 15px 0;
                font-size: 0.9rem;
                line-height: 1.4;
            }
            
            .result { 
                background: #FFFFFF; 
                margin: 0;
                overflow: hidden;
            }
            
            .result-header {
                background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%);
                color: #FFFFFF;
                padding: 20px 15px;
            }
            
            .result-title {
                font-size: 1.1rem;
                font-weight: 700;
                margin-bottom: 8px;
                line-height: 1.3;
            }
            
            .code-badge {
                background: rgba(255, 255, 255, 0.2);
                color: #FFFFFF;
                padding: 4px 8px;
                font-weight: 700;
                font-size: 0.9rem;
                margin-right: 8px;
                border-radius: 4px;
                display: inline-block;
            }
            
            .fault-code-bold {
                font-weight: 700;
                background: rgba(255, 255, 255, 0.2);
                color: #FFFFFF;
                padding: 2px 6px;
                border-radius: 3px;
                font-size: 1em;
            }
            
            .result-content {
                padding: 0;
                background: #FFFFFF;
            }
            
            .tab-container {
                background: #F8FAFC;
                border-bottom: 1px solid #E0E6ED;
                padding: 0;
                margin: 0;
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
            }
            
            .tab-wrapper {
                display: flex;
                min-width: max-content;
            }
            
            .tab {
                display: inline-block;
                padding: 15px 20px;
                background: #E0E6ED;
                color: #2C3E50;
                border: none;
                border-right: 1px solid #B0C4DE;
                cursor: pointer;
                font-weight: 600;
                font-size: 0.85rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                transition: all 0.3s ease;
                white-space: nowrap;
                -webkit-tap-highlight-color: transparent;
                min-width: 80px;
                text-align: center;
            }
            
            .tab:hover, .tab:active {
                background: #D0D6DD;
            }
            
            .tab.active {
                background: #FFFFFF;
                color: #4A90E2;
                border-bottom: 3px solid #4A90E2;
            }
            
            .tab-content {
                display: none;
                padding: 20px 15px;
                background: #FFFFFF;
                min-height: 120px;
            }
            
            .tab-content.active {
                display: block;
            }
            
            .section {
                margin-bottom: 25px;
                padding-bottom: 20px;
                border-bottom: 1px solid #F0F0F0;
            }
            
            .section:last-child {
                border-bottom: none;
                margin-bottom: 0;
            }
            
            .section-title {
                font-size: 0.95rem;
                font-weight: 700;
                color: #2C3E50;
                margin-bottom: 12px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                background: #F8FAFC;
                padding: 12px 15px;
                border: 1px solid #E0E6ED;
                border-left: 4px solid #4A90E2;
                border-radius: 0 6px 6px 0;
            }
            
            .section-content {
                color: #2C3E50;
                line-height: 1.6;
                font-size: 0.9rem;
                padding: 0;
                white-space: pre-wrap;
                word-wrap: break-word;
            }
            
            .multiple-results {
                background: #F8FAFC;
                padding: 20px 15px;
                border: 1px solid #E0E6ED;
                margin: 15px;
                border-radius: 8px;
            }
            
            .multiple-results h3 {
                color: #2C3E50;
                margin-bottom: 15px;
                font-size: 1rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .multiple-results ul {
                list-style: none;
            }
            
            .multiple-results li {
                background: #FFFFFF;
                padding: 12px 15px;
                margin-bottom: 8px;
                border: 1px solid #E0E6ED;
                border-left: 4px solid #4A90E2;
                border-radius: 0 6px 6px 0;
                font-size: 0.9rem;
                transition: all 0.2s ease;
            }
            
            .multiple-results li:hover {
                background: #F8FAFC;
                transform: translateX(2px);
            }
            
            .multiple-results li:last-child {
                margin-bottom: 0;
            }
            
            .status-bar {
                background: #F8FAFC;
                color: #2C3E50;
                padding: 12px 15px;
                border-top: 1px solid #E0E6ED;
                font-size: 0.8rem;
                text-align: center;
                font-weight: 600;
            }
            
            /* Mobile-specific optimizations */
            @media (max-width: 768px) {
                .header {
                    padding: 15px 10px;
                }
                
                h1 {
                    font-size: 1.3rem;
                }
                
                .subtitle {
                    font-size: 0.8rem;
                }
                
                .search-section {
                    padding: 15px 10px;
                }
                
                .diagnostic-info {
                    font-size: 0.75rem;
                    padding: 10px 12px;
                }
                
                .input-group {
                    flex-direction: column;
                }
                
                button {
                    padding: 15px;
                    font-size: 16px;
                }
                
                .result-header {
                    padding: 15px 10px;
                }
                
                .result-title {
                    font-size: 1rem;
                }
                
                .tab {
                    padding: 12px 15px;
                    font-size: 0.8rem;
                    min-width: 70px;
                }
                
                .tab-content {
                    padding: 15px 10px;
                }
                
                .section-title {
                    font-size: 0.85rem;
                    padding: 10px 12px;
                }
                
                .section-content {
                    font-size: 0.85rem;
                }
                
                .multiple-results {
                    margin: 10px;
                    padding: 15px 10px;
                }
                
                .multiple-results li {
                    padding: 10px 12px;
                    font-size: 0.85rem;
                }
            }
            
            /* Very small screens */
            @media (max-width: 480px) {
                .header {
                    padding: 12px 8px;
                }
                
                h1 {
                    font-size: 1.2rem;
                }
                
                .search-section {
                    padding: 12px 8px;
                }
                
                .tab {
                    padding: 10px 12px;
                    font-size: 0.75rem;
                    min-width: 60px;
                }
                
                .tab-content {
                    padding: 12px 8px;
                }
            }
            
            /* Touch-friendly improvements */
            @media (hover: none) and (pointer: coarse) {
                button, .tab {
                    min-height: 44px;
                }
                
                input[type=text] {
                    min-height: 44px;
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
            
            // Auto-focus search input on mobile
            document.addEventListener('DOMContentLoaded', function() {
                var searchInput = document.querySelector('input[type="text"]');
                if (searchInput && window.innerWidth <= 768) {
                    // Small delay to ensure keyboard doesn't interfere with initial load
                    setTimeout(function() {
                        searchInput.focus();
                    }, 500);
                }
            });
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
                    <div class="input-group">
                        <input type="text" name="code" placeholder="Enter fault code (e.g. 00532, P0123, B1234)" value="{{code}}" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false">
                        <button type="submit">SCAN</button>
                    </div>
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
                            <div class="tab-wrapper">
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
    print("Starting VCDS Fault Code Lookup Server...")
    print("Mobile-optimized version")
    print("=" * 40)
    app.run(host="0.0.0.0", port=5000, debug=False)
