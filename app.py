from flask import Flask, request, jsonify
from google import genai
import sqlite3
import json
import time
from PIL import Image

app = Flask(__name__)

def init_db():
    """Creates a local SQLite database and table if it doesn't exist."""
    conn = sqlite3.connect('contracts.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS leases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            lock_in TEXT,
            security_deposit TEXT,
            notice_period TEXT,
            maintenance TEXT,
            hidden_traps TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()


client = genai.Client(api_key="API KEY") 

@app.route('/analyze', methods=['POST'])
def analyze_contract():
    if 'document' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
        
    file = request.files['document']
    image = Image.open(file.stream)
    
    prompt = """
    You are an expert legal assistant specializing in real estate and tenancy agreements.
    Analyze the provided image/document of the lease agreement.
    
    Extract these 5 specific data points and return ONLY a raw JSON object matching this schema:
    {
      "lock_in": "Brief summary of lock-in period",
      "security_deposit": "Summary of deposit amount and rules",
      "notice_period": "Summary of notice period duration",
      "maintenance": "Summary of maintenance responsibilities",
      "hidden_traps": "Any unusual clauses, late fees, or escalation clauses"
    }
    Do not include markdown tags like ```json. Just output the raw JSON object.
    """

    try:
        max_retries = 3
        raw_text = ""
        
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model='gemini-3.5-flash',
                    contents=[image, prompt]
                )
                raw_text = response.text.strip()
                break 
                
            except Exception as api_error:
                if "503" in str(api_error) or "UNAVAILABLE" in str(api_error):
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt 
                        print(f"Google servers busy. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue 
                raise api_error
        
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
            
        summary_data = json.loads(raw_text)

        
        conn = sqlite3.connect('contracts.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO leases (filename, lock_in, security_deposit, notice_period, maintenance, hidden_traps)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            file.filename,
            summary_data.get("lock_in", "N/A"),
            summary_data.get("security_deposit", "N/A"),
            summary_data.get("notice_period", "N/A"),
            summary_data.get("maintenance", "N/A"),
            summary_data.get("hidden_traps", "N/A")
        ))
        db_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            "message": "Analysis successful",
            "db_id": db_id,
            "summary": summary_data
        }), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)